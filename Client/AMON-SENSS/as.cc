/*
#
# Copyright (C) 2018 University of Southern California.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License,
# version 2, as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
*/

#include <signal.h>
#include <iostream>
#include <algorithm>
#include <fstream>
#include <sched.h>
#include <sys/types.h>
#include <sys/select.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>
#include <errno.h>
#include <sys/poll.h>
#include <netinet/in_systm.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <netinet/udp.h>
#include <netinet/ip6.h>
#include <net/ethernet.h>
#include <sys/time.h>
#include <time.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <monetary.h>
#include <locale.h>
#include <regex.h>
#include <iostream>
#include <sstream>
#include <string>
#include <map>
#include <cmath>
#include <pcap.h>
#include <dirent.h>

// MySQL includes
#include "mysql_connection.h"

#include <cppconn/driver.h>
#include <cppconn/exception.h>
#include <cppconn/resultset.h>
#include <cppconn/statement.h>
#include <cppconn/prepared_statement.h>


#include "utils.h"

#define BILLION 1000000000L

using namespace std;

// We store delimiters in this array
int* delimiters;

// Something like strtok but it doesn't create new
// strings. Instead it replaces delimiters with 0
// in the original string
void parse(char* input, char delimiter, int** array)
{
  int pos = 0;
  memset(*array, 255, AR_LEN);
  int len = strlen(input);
  for(int i = 0; i<len; i++)
    {
      if (input[i] == delimiter)
	{
	  (*array)[pos] = i+1;
	  input[i] = 0;
	  pos++;
	}
    }
}

// Variables/structs needed for detection
struct cell
{
  long int databrick_p[BRICK_DIMENSION];	 // databrick volume
  long int databrick_s[BRICK_DIMENSION];         // databrick symmetry 
  unsigned int wfilter_p[BRICK_DIMENSION];	 // volume w filter 
  int wfilter_s[BRICK_DIMENSION];	         // symmetry w filter 
  int fresh;
};
// Should we require destination prefix
bool noorphan = false;
// How many service ports are there
int numservices = 0;
// Save all flows for a given time slot
map<long, time_flow*> timeflows;

// These are the bins where we store stats
cell cells[QSIZE];
int cfront = 0;
int crear = 0;
bool cempty = true;

// Samples of flows for signatures
sample samples;

// Signatures per bin
stat_r signatures[BRICK_DIMENSION];
// We remember all time slots here and
// do statistics update when we are sure
// that the time slot did not have an attack
vector<long> times;

// Save some stats about each bin if verbose bit is set
// This helps later with debugging
ofstream debug[BRICK_DIMENSION];
// Is the bin abnormal or not
int is_abnormal[BRICK_DIMENSION];
// Did we detect an attack in this bin
int is_attack[BRICK_DIMENSION];
// Should we allow broad signatures
int broad_allowed[BRICK_DIMENSION];
// Are we simulating filtering. This is not for live experiments.
bool sim_filter = false;

// Did we complete training
bool training_done = false;
int trained = 0;

// Current time
double curtime = 0;
double lasttime = 0;

// Verbose bit
int verbose = 0;

double firsttime = 0;       // Beginning of trace 
long freshtime = 0;       // Where we last ended when processing data 
double firsttimeinfile = 0; // First time in the current file 
long updatetime = 0;      // Time of last stats update
long statstime = 0;       // Time when we move the stats to history 
char filename[MAXLINE];   // A string to hold filenames
struct timespec last_entry;

// Is this pcap file or flow file? Default is flow
bool is_pcap = false;
bool is_live = false;

// Serialize access to statistics
pthread_mutex_t cells_lock = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t sql_lock = PTHREAD_MUTEX_INITIALIZER;

// Types of statistics. If this changes, update the entire section 
enum period{cur, hist};
enum type{n, avg, ss};
enum dim{vol, sym};
double stats[2][3][2][BRICK_DIMENSION]; // historical and current stats for attack detection
string label;

// Parameters from as.config
map<string,double> parms;

// Variables for DB access
sql::Driver *driver;
sql::Connection *con;
sql::ResultSet *res;


// Keeping track of procesed flows
long int processedflows = 0;
long int processedbytes = 0;
int nl = 0;
int l = 0;
int mal = 0;
int inserts = 0;
int cinserts = 0;

// Trim strings 
char *trim(char *str)
{
    size_t len = 0;
    char *frontp = str;
    char *endp = NULL;

    if( str == NULL ) { return NULL; }
    if( str[0] == '\0' ) { return str; }

    len = strlen(str);
    endp = str + len;

    while( isspace((unsigned char) *frontp) ) { ++frontp; }
    if( endp != frontp )
    {
        while( isspace((unsigned char) *(--endp)) && endp != frontp ) {}
    }

    if( str + len - 1 != endp )
            *(endp + 1) = '\0';
    else if( frontp != str &&  endp == frontp )
            *str = '\0';

    endp = str;
    if( frontp != str )
    {
            while( *frontp ) { *endp++ = *frontp++; }
            *endp = '\0';
    }

    return str;
}

// Parse configuration file and load into parms
void
parse_config (map <string,double>& parms)
{
  char *s, buff[256];
  FILE *fp = fopen ("as.config", "r");
  if (fp == NULL)
  {
    cout <<"Config file as.config does not exist. Please include it and re-run.. \n";
    exit (0);
  }
  cout << "Reading config file as.config ...";
  while ((
	  s = fgets (buff, sizeof buff, fp)) != NULL)
  {
        // Skip blank lines and comment lines 
        if (buff[0] == '\n' || buff[0] == '#')
          continue;

	// Look for = sign and abort if that does not
	// exist
	char name[MAXLINE], value[MAXLINE];
	int found = -1;
	int i = 0;
	for(i=0; i<strlen(buff); i++)
	  {
	    if (buff[i] == '=')
	      {
		strncpy(name,buff, i);
		name[i] = 0;
		found = i;
	      }
	    else if((buff[i] == ' ' || buff[i] == '\n') && found >= 0)
	      {
		strncpy(value,buff+found+1,i-found-1);
		value[i-found-1] = 0;
		break;
	      }
	  }
	if (i > 0 && found > -1)
	  {
	    strncpy(value,buff+found+1,i-found-1);
	    value[i-found-1] = 0;
	  }
	if (found == -1)
	  continue;
	trim(name);
	trim(value);
	cout<<"Parm "<<name<<" val "<<value<<endl;
	parms.insert(pair<string,double>(name,strtod(value,0)));
  }
  fclose (fp);
}


// Check if the signature contains all zeros
// proto doesn't count
int empty(flow_t sig)
{
  return ((sig.src == 0) && (sig.sport == 0) &&
	  (sig.dst == 0) && (sig.dport == 0));
}

// Check if the signature is subset or matches
// exactly the slot where anomaly was found.
// For example, if a source port's traffic was
// anomalous we have to have that source port in the
// signature
bool compliantsig(int i, flow_t sig)
{
  switch (i/BRICK_UNIT)
    {
    case 0:
      return (sig.src != 0);
    case 1:
    case 2:
      return (sig.dst != 0 && (sig.src != 0 || sig.dport != 0 || sig.sport != 0));
    case 3:
      return (sig.sport != 0 && (sig.dst != 0 || sig.dport != 0 || sig.sport != 0));
    case 4:
      return (sig.dport != 0 && (sig.dst != 0 || sig.src != 0 || sig.sport != 0));
    default:
      return false;
    }
}


void clearSamples(int index)
{
  flow_t key;
  for (int s=1; s<NF; s++)
    {
      samples.bins[index].flows[s].flow = key;
      samples.bins[index].flows[s].len = 0;
      samples.bins[index].flows[s].oci = 0;
    }
}
// Add a flow to the samples bin
void addSample(int index, flow_p* f, int way)
{
  // Create some partial signatures for this flow, like src-dst combination,
  // src-sport, etc. Don't allow just protocol
  for (int s=1; s<NF; s++)
    {
      flow_t k;
      k.proto = f->flow.proto;
      if ((s & 8) > 0)
	k.src = f->flow.src;
      if ((s & 4) > 0)
	k.sport = f->flow.sport;
      if ((s & 2) > 0)
	k.dst = f->flow.dst;
      if ((s & 1) > 0)
	k.dport = f->flow.dport;
      if (way == FOR)
	k.src = f->flow.src;
      else if (way == LOC || way == LOCPREF)
	{
	  k.dst = f->flow.dst;
	  if (way == LOCPREF)
	    k.dst &= 0xffffff00;
	}
      else if (way == FPORT)
	k.sport = f->flow.sport;
      else if (way == LPORT)
	k.dport = f->flow.dport;

      // src, dst, sport, dport
      // Overload len so we can track frequency of contributions
      // Jelena - there was continue here
      // Insert sample if it does not exist
      if (samples.bins[index].flows[s].flow == k)
	{
	  // Else increase contributions of this signature wrt symmetry
	  samples.bins[index].flows[s].len += abs(f->oci);
	  samples.bins[index].flows[s].oci += f->oci;
	}
      else	
	{
	  // Boyer Moore to find signatures that cover the most flows
	  if (empty(samples.bins[index].flows[s].flow))
	    samples.bins[index].flows[s].flow = k;
	  else
	    {
	      samples.bins[index].flows[s].len -= abs(f->oci);
	      // Replace this signature if there's another one,
	      // which covers more
	      if (samples.bins[index].flows[s].len < 0)
		{
		  samples.bins[index].flows[s].flow = k;
		  samples.bins[index].flows[s].len = abs(f->oci);
		  samples.bins[index].flows[s].oci = f->oci;
		}
	    }
	}
    }	
} 


// Does this flow match the given signature
int match(flow_t flow, flow_t sig)
{
  if (flow.proto != sig.proto && sig.proto != 0)
    return 0;
  if (empty(sig))
    return 0;
  if ((flow.src == sig.src || sig.src == 0) &&
      (flow.sport == sig.sport || sig.sport == 0) &&
      (flow.dst == sig.dst || sig.dst == 0) &&
      (flow.dport == sig.dport || sig.dport == 0))
    return 1;
  else
    return 0;
}

// Is this timestamp within the range, which we expect in a given input file
int malformed(long timestamp)
{
  if (timestamp < firsttimeinfile || timestamp > firsttimeinfile +
      parms["file_interval"])
    return 1;
  return 0;
}



bool shouldFilter(int bucket, flow_t flow)
{
  if (!empty(signatures[bucket].sig) && match(flow,signatures[bucket].sig))
    return true;
  else
    return false;
}
long votedtime = 0;
int votes = 0;

// Main function, which processes each flow
void
amonProcessing(flow_t flow, int len, double start, double end, int oci)
{
  // Detect if the flow is malformed and reject it
  if (malformed(start) || malformed(end))
    {
      mal++;
      return;
    }
  // Standardize time
  if (curtime == 0)
    curtime = start;
  if (start > curtime)
    {
      if (votes == 0)
	votedtime = (int)start;
      if ((int)start == votedtime)
	votes++;
      else
	votes--;
      if (votes >= 5)
	{
	  curtime = start;
	  votedtime = 0;
	  votes = 0;
	}
    }

  if (lasttime == 0)
    lasttime = curtime;

  flow_p fp(start, end, len, oci, flow);
      
  int d_bucket = -1, s_bucket = -1;	    // indices for the databrick 

  cell *c = &cells[crear];

  int is_filtered = false;

  if (sim_filter)
    {
      for (int way = FOR; way <= LPORT; way++) // SERV is included in CLI
	{
	  // Find buckets on which to work
	  if (way == FOR)
	    {
	      if (flow.dlocal)
		{
		  s_bucket = myhash(flow.src, 0, FOR);
		  if (shouldFilter(s_bucket, flow))
		    {
		      is_filtered = true;
		      c->wfilter_p[s_bucket] += len;
		      c->wfilter_s[s_bucket] += oci;
		    }
		}
	    }
	  else if (way == LOC || way == LOCPREF)
	    {
	      if (flow.dlocal)
		{
		  d_bucket = myhash(flow.dst, 0, way);
		  if (shouldFilter(d_bucket, flow))
		    {
		      is_filtered = true;
		      c->wfilter_p[d_bucket] += len;
		      c->wfilter_s[d_bucket] += oci;
		    }
		}
	    }
	  else if (way == FPORT) 
	    {
	      if (flow.dlocal)
		{
		  // traffic from FPORT
		  s_bucket = myhash(0, flow.sport, way);
		  if (shouldFilter(s_bucket, flow))
		    {
		      is_filtered = true;
		      c->wfilter_p[s_bucket] += len;
		      c->wfilter_s[s_bucket] += oci;
		    }
		}
	    }
	  else if (way == LPORT)
	    {
	      if (flow.dlocal)
		{
		  // traffic to LPORT
		  d_bucket = myhash(0, flow.dport, way);
		  if (shouldFilter(d_bucket, flow))
		    {
		      is_filtered = true;
		      c->wfilter_p[d_bucket] += len;
		      c->wfilter_s[d_bucket] += oci;
		    }
		}
	    }
	}
    }

  if (is_filtered)
    {
      return;
    }

  for (int way = FOR; way <= LPORT; way++) 
    {
      // Find buckets on which to work
      if (way == FOR)
	{
	  if (flow.dlocal)
	    {
	      // traffic to us from FOR
	      s_bucket = myhash(flow.src, 0, FOR);
	      c->databrick_p[s_bucket] += len;
	      c->databrick_s[s_bucket] += oci;
	      addSample(s_bucket, &fp, way);
	    }
	  if (flow.slocal)
	    {
	      // our traffic to FOR
	      d_bucket = myhash(flow.dst, 0, FOR);
	      c->databrick_p[d_bucket] -= len;
	      c->databrick_s[d_bucket] -= oci;
	    }
	}
      else if (way == LOC || way == LOCPREF)
	{
	  if (flow.dlocal)
	    {
	      // traffic to LOC
	      d_bucket = myhash(flow.dst, 0, way);
	      c->databrick_p[d_bucket] += len;
	      c->databrick_s[d_bucket] += oci;
	      addSample(d_bucket, &fp, way);
	    }
	  if (flow.slocal)
	    {
	      // traffic from LOC
	      s_bucket = myhash(flow.src, 0, way);
	      c->databrick_p[s_bucket] -= len;
	      c->databrick_s[s_bucket] -= oci;
	    }	      
	}
      else if (way == FPORT)
	{
	  if (flow.dlocal)
	    {
	      // traffic from FPORT
	      s_bucket = myhash(0, flow.sport, way);
	      c->databrick_p[s_bucket] += len;
	      c->databrick_s[s_bucket] += oci;
	      addSample(s_bucket, &fp, way);
	    }
	  if (flow.slocal)
	    {
	      // traffic to FPORT
	      d_bucket = myhash(0, flow.dport, way);
	      c->databrick_p[d_bucket] -= len;
	      c->databrick_s[d_bucket] -= oci;	      
	    }
	}
      else if (way == LPORT)
	{
	  if (flow.dlocal)
	    {
	      // traffic to LPORT
	      d_bucket = myhash(0, flow.dport, way);
	      c->databrick_p[d_bucket] += len;
	      c->databrick_s[d_bucket] += oci;
	      addSample(d_bucket, &fp, way);
	    }
	  if (flow.slocal)
	    {
	      // traffic from LPORT
	      s_bucket = myhash(0, flow.sport, way);
	      c->databrick_p[s_bucket] -= len;
	      c->databrick_s[s_bucket] -= oci;
	    }
	}
    }
}

// Function to detect values higher than mean + parms[numstd] * stdev 
int abnormal(int type, int index, cell* c)
{
  // Look up std and mean
  double mean = stats[hist][avg][type][index];
  double std = sqrt(stats[hist][ss][type][index]/
		    (stats[hist][n][type][index]-1));
  // Look up current value
  int data;
  if (type == vol)
    data = c->databrick_p[index];
  else
    data = c->databrick_s[index];
  // Volume larger than mean + numstd*stdev is abnormal 
  if (data > mean + parms["numstd"]*std)
    {
      return 1;
    }
  else
    {
      return 0;
    }
}

// Update statistics
void update_stats(cell* c)
{
  for (int i=0;i<BRICK_DIMENSION;i++)
    {
      for (int j=vol; j<=sym; j++)
	{
	  int data;
	  if (j == vol)
	    data = c->databrick_p[i];
	  else
	    data = c->databrick_s[i];
	  // Only update if everything looks normal 
	  if (!is_abnormal[i])
	    {
	      // Update avg and ss incrementally
	      stats[cur][n][j][i] += 1;
	      if (stats[cur][n][j][i] == 1)
		{
		  stats[cur][avg][j][i] =  data;
		  stats[cur][ss][j][i] =  0;
		}
	      else
		{
		  int ao = stats[cur][avg][j][i];
		  stats[cur][avg][j][i] = stats[cur][avg][j][i] +
		    (data - stats[cur][avg][j][i])/stats[cur][n][j][i];
		  stats[cur][ss][j][i] = stats[cur][ss][j][i] +
		    (data-ao)*(data - stats[cur][avg][j][i]);
		}
	    }
	}
    }
  trained++;
  if (trained == parms["min_train"])
    {
      if (!training_done)
	{
	  training_done = true;
	  cout<<"Training has completed\n";
	}
      trained = 0;
     
      for (int x = ss; x >= n; x--)
	for (int j = vol; j <= sym; j++)
	  for(int i = 0; i<BRICK_DIMENSION; i++)
	  {
	    // Check if we have enough samples.
	    // If the attack was long maybe we don't
	    if (stats[cur][n][j][i] <
		parms["min_train"]*MIN_SAMPLES)
		continue;
	    stats[hist][x][j][i] = stats[cur][x][j][i];
	    stats[cur][x][j][i] = 0;
	  }
    }
}

void findBestSignature(int i, cell* c)
{
  flow_t bestsig;
  int oci = 0;
  int maxoci = 0;
  int totoci = c->databrick_s[i];
  
  // Go through candidate signatures
  for (int s=1; s<NF; s++)
    {
      if (empty(samples.bins[i].flows[s].flow))
	continue;

      double candrate = (double)samples.bins[i].flows[s].oci;

      if (!compliantsig(i, samples.bins[i].flows[s].flow))
	{
	  if (verbose)
	    cout<<"non compliant SIG: "<<i<<" for slot "<<i/BRICK_UNIT<<" candidate "<<printsignature(samples.bins[i].flows[s].flow)<<" v="<<samples.bins[i].flows[s].len<<" o="<<samples.bins[i].flows[s].oci<<" toto="<<totoci<<" candrate "<<candrate<<" divided "<<candrate/totoci<<endl;
	    continue;
	}

      // Print out each signature for debugging
      if (verbose)
	cout<<"SIG: "<<i<<" candidate "<<printsignature(samples.bins[i].flows[s].flow)<<" v="<<samples.bins[i].flows[s].len<<" o="<<samples.bins[i].flows[s].oci<<" toto="<<totoci<<" candrate "<<candrate<<" divided "<<candrate/totoci<<endl;
      // Potential candidate
      if (candrate/totoci > parms["filter_thresh"])
	{
	  // Is it a more specific signature?
	  if (bettersig(samples.bins[i].flows[s].flow, bestsig))
	    {
	      if (verbose)
		cout<<"SIG: changing to "<< printsignature(samples.bins[i].flows[s].flow)<<endl;
	      bestsig = samples.bins[i].flows[s].flow;
	      oci = candrate;
	    }
	}
    }
  if (verbose)
    cout<<"SIG: "<<i<<" best sig "<<printsignature(bestsig)<<" Empty? "<<empty(bestsig)<<" oci "<<maxoci<<" out of "<<totoci<<endl;
  broad_allowed[i]++;
  // Remember the signature if it is not empty and can filter
  // at least filter_thresh flows in the sample
  if (!empty(bestsig))
    {
      if (verbose)
	cout<<"ISIG: "<<i<<" installed sig "<<printsignature(bestsig)<<endl;

      // insert signature and reset all the stats
      // this is needed only for simulation of filtering
      if (sim_filter)
	{
	  signatures[i].sig = bestsig;
	  signatures[i].vol = 0;
	  signatures[i].oci = 0;
	}
      double diff = curtime - lasttime;
      if (diff < 1)
	diff = 1;
      double avgv = stats[hist][avg][vol][i];
      double stdv = sqrt(stats[hist][ss][vol][i]/(stats[hist][n][vol][i]-1));
      double avgs = stats[hist][avg][sym][i];
      double stds = sqrt(stats[hist][ss][sym][i]/(stats[hist][n][sym][i]-1));
      long int rate = c->databrick_p[i]/diff - avgv - parms["num_std"]*stdv;
      long int roci = c->databrick_s[i]/diff - avgs - parms["num_std"]*stds;
      // Write the start of the attack into alerts
      ofstream out;
      

      out.open("alerts.txt", std::ios_base::app);
      out<<i/BRICK_UNIT<<" "<<(long)curtime<<" ";
      out<<"START "<<i<<" "<<rate;
      out<<" "<<roci<<" ";
      out<<printsignature(bestsig)<<endl;
      out.close();
      // Now remove abnormal measure and samples, we're done
      is_abnormal[i] = 0;
      // Clear samples
      clearSamples(i);
      // Clear broad_allowed if we did get a broad sig
      if (broad_allowed[i] >= 16)
	broad_allowed[i] = 0;
    }
  // Did not find a good signature
  // drop the attack signal and try again later
  else
    {
      if (verbose)
	cout << "AT: Did not find good signature for attack "<<
	  " on bin "<<i<<" best sig "<<empty(bestsig)<<
	  " coverage "<<(float)oci/totoci<<" thresh "<<
	  parms["filter_thresh"]<<endl;
      is_attack[i] = false;
    }
}

// This function detects an attack
void detect_attack(cell* c)
{
  // If verbose, output debugging statistics into DB
  if (false) // Jelena verbose
    {
      sql::PreparedStatement *stmt;
      DataBuf buffer((char*)c, sizeof(cell));
      istream stream(&buffer);
      pthread_mutex_lock (&sql_lock);
      bool succ = false;
      while (!succ)
	{
	  try{
	    stmt = con->prepareStatement ("INSERT INTO stats VALUES (?, ?, ?)");
	    
	    stmt->setString(1, label);
	    stmt->setUInt(2, curtime);
	    stmt->setBlob(3, &stream);
	    succ = true;
	  }
	  catch(std::exception &e) {
	    cout << "Exception conn is "<<con<<" error "<<e.what()<<endl;
	    driver = get_driver_instance();
	    con = driver->connect("tcp://127.0.0.1:3306", "amon-senss", "St33llab@isi");
	    con->setSchema("AMONSENSS");
	  }
	}
      succ = false;
      while (!succ)
	{
	  try{
	    int res = stmt->executeUpdate();
	    if (res)
	      {
		cout<<"Executed one update"<<pthread_self()<<endl;
		succ = true;
	      }	    
	  }
	  catch(sql::SQLException &e) {
	    cout << " (MySQL error code: " << e.getErrorCode();
	    cout << ", SQLState: " << e.getSQLState() << " )" << endl;
	  }
	}
      delete stmt;
      pthread_mutex_unlock (&sql_lock);
    }
  // For each bin
  for (int i=0;i<BRICK_DIMENSION;i++)
    {
      // Pull average and stdev for volume and symmetry
      double avgv = stats[hist][avg][vol][i];
      double stdv = sqrt(stats[hist][ss][vol][i]/(stats[hist][n][vol][i]-1));
      double avgs = stats[hist][avg][sym][i];
      double stds = sqrt(stats[hist][ss][sym][i]/(stats[hist][n][sym][i]-1));

      if (is_attack[i] == true)
	is_attack[i] = false;
      // If both volume and asymmetry are abnormal and training has completed
      int a = abnormal(vol, i, c);
      int b = abnormal(sym, i, c);
      int volume = c->databrick_p[i];
      int asym = c->databrick_s[i];
      if (training_done && abnormal(vol, i, c) && abnormal(sym, i, c))
	{
	  double aavgs = abs(avgs);
	  if (aavgs == 0)
	    aavgs = 1;
	  double d = abs(abs(asym) - abs(avgs) - parms["numstd"]*abs(stds))/aavgs;
	  if (d > parms["max_oci"])
	    d = parms["max_oci"];
	  if (verbose)
	    cout<<curtime<<" abnormal for "<<i<<" points "<<is_abnormal[i]<<" oci "<<c->databrick_s[i]<<" ranges " <<avgs<<"+-"<<stds<<", vol "<<c->databrick_p[i]<<" ranges " <<avgv<<"+-"<<stdv<<" over mean "<<d<<endl;
	  
	  // Increase abnormal score, but cap at attack_high
	  if (is_abnormal[i] < int(parms["attack_high"]))
	    is_abnormal[i] += int(d+1);
	  if (is_abnormal[i] > int(parms["attack_high"]))
	    is_abnormal[i] = int(parms["attack_high"]);
	  
	  // If abnormal score is above attack_low
	  // and oci is above MAX_OCI
	  if (is_abnormal[i] >= int(parms["attack_low"])
	      && !is_attack[i] && abs(c->databrick_s[i]) >= int(parms["max_oci"]))
	    {
	      // Signal attack detection 
	      is_attack[i] = true;
	      if (verbose)
		cout<<"AT: Attack detected on "<<i<<" but not reported yet vol "<<c->databrick_p[i]<<" oci "<<c->databrick_s[i]<<" max oci "<<int(parms["max_oci"])<<endl;
	     
	      // Find the best signature
	      findBestSignature(i, c);
	    }
	}
      // Training is completed and both volume and symmetry are normal
      else if (training_done && !abnormal(vol, i, c) && !abnormal(sym, i, c))
	{
	  // if (verbose)
	  //cout<<curtime<<" is normal for "<<i<<" points "<<is_abnormal[i]<<" oci "<<c->databrick_s[i]<<" ranges " <<avgs<<"+-"<<stds<<", vol "<<c->databrick_p[i]<<" ranges " <<avgv<<"+-"<<stdv<<endl;
	  // Reduce abnormal score
	  if (is_abnormal[i] > 0)
	    {
	      is_abnormal[i] --;
	    }
	}
    }
}

// Read pcap packet format
void
amonProcessingPcap (pcap_pkthdr* hdr, u_char* p, double time)
{
  // Start and end time of a flow are just pkt time
  double start = time;
  double end = time;
  double dur = 1;
  int pkts, bytes;

  struct ip ip;
  // Get source and destination IP and port and protocol 
  flow_t flow;

  struct ether_header ehdr;
  memcpy (&ehdr, p, sizeof (struct ether_header));
  int eth_type = ntohs (ehdr.ether_type);
  if (eth_type == 0x0800)
    {
      memcpy (&ip, p + sizeof (ehdr),sizeof (struct ip));   
      flow.src = ntohl (ip.ip_src.s_addr);
      flow.dst = ntohl (ip.ip_dst.s_addr);
      int proto = ip.ip_p;
      if (proto == IPPROTO_TCP)
	{
	  struct tcphdr *tcp = (struct tcphdr*)(p + sizeof (ehdr) + ip.ip_hl*4);
	  flow.sport = ntohs(tcp->th_sport);
	  flow.dport = ntohs(tcp->th_dport);
	}
      else if (proto == IPPROTO_UDP)
	{
	  struct udphdr *udp = (struct udphdr*)(p + sizeof (ehdr) + ip.ip_hl*4);
	  flow.sport = ntohs(udp->uh_sport);
	  flow.dport = ntohs(udp->uh_dport);
	}
      else
	{
	  flow.sport = 0;
	  flow.dport = 0;
	}
      pkts = 1;
      bytes = ntohs(ip.ip_len);
      flow.slocal = islocal(flow.src);
      flow.dlocal = islocal(flow.dst);
      flow.proto = proto;
      int oci = 1;
      amonProcessing(flow, bytes, start, end, oci); 
    }
}


// Read nfdump flow format
void
amonProcessingNfdump (char* line, double time)
{
  /* 2|1453485557|768|1453485557|768|6|0|0|0|2379511808|44694|0|0|0|2792759296|995|0|0|0|0|2|0|1|40 */
  // Get start and end time of a flow
  char* tokene;
  char saveline[MAXLINE];
  parse(line,'|', &delimiters);
  double start = (double)strtol(line+delimiters[0], &tokene, 10);
  start = start + strtol(line+delimiters[1], &tokene, 10)/1000.0;
  double end = (double)strtol(line+delimiters[2], &tokene, 10);
  end = end + strtol(line+delimiters[3], &tokene, 10)/1000.0;
  double dur = end - start;
  // Normalize duration
  if (dur < 0)
    dur = 0;
  if (dur > 3600)
    dur = 3600;
  int pkts, bytes;

  // Get source and destination IP and port and protocol 
  flow_t flow;
  int proto = atoi(line+delimiters[4]);
  flow.src = strtol(line+delimiters[8], &tokene, 10);
  flow.sport = atoi(line+delimiters[9]); 
  flow.dst = strtol(line+delimiters[13], &tokene, 10);
  flow.dport = atoi(line+delimiters[14]); 
  flow.proto = proto;
  flow.slocal = islocal(flow.src);
  flow.dlocal = islocal(flow.dst);
  bytes = atoi(line+delimiters[22]);
  processedbytes+=bytes;

  // Cross-traffic, do nothing
  if (!flow.slocal && !flow.dlocal)
    {
      nl++;
      return;
    }
  l++;
  int flags = atoi(line+delimiters[19]);
  pkts = atoi(line+delimiters[21]);
  pkts = (int)(pkts/(dur+1))+1;
  bytes = (int)(bytes/(dur+1))+1;

  /* Is this outstanding connection? For TCP, connections without 
     PUSH are outstanding. For UDP, connections that have a request
     but not a reply are outstanding. Because bidirectional flows
     may be broken into two unidirectional flows we have values of
     0, -1 and +1 for outstanding connection indicator or oci. For 
     TCP we use 0 (there is a PUSH) or 1 (no PUSH) and for UDP/ICMP we 
     use +1 for requests and -1 for replies. */
  int oci;
  if (proto == TCP)
    {
      // There is a PUSH flag
      if ((flags & 8) > 0)
	oci = 0;
      else
	oci = 1;
    }
  else if (proto == UDP)
    {
      oci = pkts;
    }
  else
    // unknown proto
    oci = pkts;
  
  amonProcessing(flow, bytes, start, end, oci); 
}



// Ever so often go through flows and process what is ready
void *reset_transmit (void* passed_parms)
{
  // Serialize access to cells
  pthread_mutex_lock (&cells_lock);

  lasttime = curtime;
  // We will process this one now
  int current = cfront;

  // This one will be next for processing
  cfront = (cfront + 1)%QSIZE;
  if (cfront == crear)
    cempty = true;
  
  // Serialize access to cells
  pthread_mutex_unlock (&cells_lock);
  
  cell* c = &cells[current];
  
  // Check if there is an attack that was waiting
  // a long time to be reported. Perhaps we had too specific
  // signature and we will never collect enough matches
  // Serialize access to stats
  if (training_done)
    detect_attack(c);
  update_stats(c);
  std::cout.precision(5);

    // Detect attack here
  pthread_exit (NULL);
}

// Save historical data for later run
void save_history()
{  
  // Only save if training has completed
  if (training_done)
    {
      ofstream out;
      out.open("as.dump", std::ios_base::out);
      for (int i=n; i<=ss;i++)
	for (int j=vol; j<=sym; j++)
	  {
	    out<<i<<" "<<j<<" ";
	    for (int k=0;k<BRICK_DIMENSION;k++)
	      {
		out<<stats[hist][i][j][k]<<" ";
	      }
	    out<<endl;
	  }
      out.close();
    }
}


// Load historical data
void load_history()
{
  ifstream in;
  in.open("as.dump", std::ios_base::in);
  if (in.is_open())
    {
      int malformed = 0;
      for (int i=n; i<=ss;i++)
	for (int j=vol; j<=sym; j++)
	  {
	    int a, b;
	    in>>a>>b;
	    if (a != i || b !=j)
	      {
		malformed = 1;
		break;
	      }
	    for (int k=0;k<BRICK_DIMENSION;k++)
	      {
		in>>stats[hist][i][j][k];
	      }
	  }
      in.close();
      if (!malformed)
	{
	  training_done = true;
	  cout<<"Training data loaded"<<endl;
	}
    }  
}

// Print help for the program
void
printHelp (void)
{
  printf ("amon-senss\n(C) 2018 University of Southern California.\n\n");
  printf ("-h                             Print this help\n");
  printf ("-r <inputfile or inputfolder>  Input is in nfdump or flow-tools file(s)\n");
  printf ("-l                             Load historical data from as.dump\n");
  printf ("-s                             Start from this given file in the input folder\n");
  printf ("-e                             End with this given file in the input folder\n");
  printf ("-f                             Simulate filtering, because we're working with traces\n");
  printf ("-v                             Verbose\n");
}


// Main program
int main (int argc, char *argv[])
{  
  delimiters = (int*)malloc(AR_LEN*sizeof(int));
  memset(is_attack, 0, BRICK_DIMENSION*sizeof(int));
  memset(is_abnormal, 0, BRICK_DIMENSION*sizeof(int));
  // Parse configuration
  parse_config (parms);
  // Load service port numbers
  noorphan = (bool) parms["no_orphan"];
  numservices = loadservices("services.txt");
  loadprefixes("localprefs.txt");
  
  char c, buf[32];
  char *file_in = NULL;
  char *startfile = NULL, *endfile = NULL;
  
  while ((c = getopt (argc, argv, "hvlr:s:e:f")) != '?')
    {
      if ((c == 255) || (c == -1))
	break;

      switch (c)
	{
	case 'h':
	  printHelp ();
	  return (0);
	  break;
	case 'r':
	  file_in = strdup(optarg);
	  label = file_in;
	  break;
	case 'f':
	  sim_filter = true;
	  break;
	case 'l':
	  load_history();
	  break;
	case 's':
	  startfile = strdup(optarg);
	  cout<<"Start file "<<startfile<<endl;
	  break;
	case 'e':
	  endfile = strdup(optarg);
	  cout<<"End file "<<endfile<<endl;
	  break;
	case 'v':
	  verbose = 1;
	  break;
	}
    }
  if (file_in == NULL)
    {
      cerr<<"You must specify an input folder, which holds Netflow records\n";
      exit(-1);
    }
  cout<<"Verbose "<<verbose<<endl;

  // Connect to DB
  try {
    driver = get_driver_instance();
    con = driver->connect("tcp://127.0.0.1:3306", "amon-senss", "St33llab@isi");
    con->setSchema("AMONSENSS");
   }
  catch (sql::SQLException &e) {
    cerr<<"Could not connect to the DB\n";
  }


  clock_gettime(CLOCK_MONOTONIC, &last_entry);      
  // This is going to be a pointer to input
  // stream, either from nfdump or flow-tools */
  FILE* nf;
  unsigned long long num_pkts = 0;      

  // Read flows from a file
  if (file_in)
    {
      int isdir = 0;
      vector<string> tracefiles;
      vector<string> inputs;
      struct stat s;
      inputs.push_back(file_in);
      int i = 0;
      // Recursively read if there are several directories that hold the files
      while(i < inputs.size())
	{
	  if(stat(inputs[i].c_str(),&s) == 0 )
	    {
	      if(s.st_mode & S_IFDIR )
		{
		  // it's a directory, read it and fill in 
		  // list of files
		  DIR *dir;
		  struct dirent *ent;

		  if ((dir = opendir (inputs[i].c_str())) != NULL) {
		    // Remember all the files and directories within directory 
		    while ((ent = readdir (dir)) != NULL) {
		      if((strcmp(ent->d_name,".") != 0) && (strcmp(ent->d_name,"..") != 0)){
			inputs.push_back(string(inputs[i]) + "/" + string(ent->d_name));
		      }
		    }
		    closedir (dir);
		  } else {
		    perror("Could not read directory ");
		    exit(1);
		  }
		}
	      else if(s.st_mode & S_IFREG)
		{
		  tracefiles.push_back(inputs[i]);
		}
	      // Ignore other file types
	    }
	  i++;
	}
      inputs.clear();

      tracefiles.push_back(file_in);
      
      std::sort(tracefiles.begin(), tracefiles.end(), sortbyFilename());

      int started = 1;
      if (startfile != NULL)
	started = 0;
      int allflows = 0;
      double start = time(0);
      // Go through tracefiles and read each one
      // Jelena: should delete after reading
      for (vector<string>::iterator vit=tracefiles.begin(); vit != tracefiles.end(); vit++)
      {
	const char* file = vit->c_str();

	if (!started && startfile && strstr(file,startfile) == NULL)
	  {
	    continue;
	  }

	started = 1;
	
	char cmd[MAXLINE];

	// Try to read from an interface as pcap
	sprintf(cmd,"tcpdump -i %s 2>/dev/null", file);
	nf = popen(cmd, "r");
	// Close immediately so we get the error code 
	// and we can detect if this is not an interface
	int error = pclose(nf);
	if (error > 0)
	  {
	    // Try to read as pcap file
	    sprintf(cmd,"tcpdump -r %s 2>/dev/null", file);
	    nf = popen(cmd, "r");
	    // Close immediately so we get the error code 
	    // and we can detect if this is maybe netflow or flow-tools format 
	    int error = pclose(nf);
	    if (error > 0)
	      {
		// Try to read as netflow file
		sprintf(cmd,"nfdump -r %s -o pipe 2>/dev/null", file);
		nf = popen(cmd, "r");
		// Close immediately so we get the error code 
		// and we can detect if this is maybe flow-tools format 
		int error = pclose(nf);
		if (error == 64000)
		  {
		    sprintf(cmd,"ft2nfdump -r %s | nfdump -r - -o pipe", file);
		    nf = popen(cmd, "r");
		  }
		else
		  {
		    nf = popen(cmd, "r");
		  }
	      }
	    else
	      {
		is_pcap = true;
	      }
	    if (!nf && !is_pcap)
	      {
		fprintf(stderr,"Cannot open file %s for reading. Unknown format.\n", file);
		pclose(nf);
		exit(1);
	      }
	  }
	else
	  {
	    is_live = true;
	    is_pcap = true;
	  }

	// Now read from file
	char line[MAXLINE];
	cout<<"Reading from "<<file<<endl;
	firsttimeinfile = 0;

	if (!is_pcap)
	  {
	    while (fgets(line, MAXLINE, nf) != NULL)
	      {
		// Check that this is the line with a flow
		char tmpline[255];
		strcpy(tmpline, line);
		if (strstr(tmpline, "|") == NULL)
		  continue;
		strtok(tmpline,"|");
		strtok(NULL,"|");
		strtok(NULL,"|");
		char* tokene;
		char* token = strtok(NULL, "|");
		double epoch = strtol(token, &tokene, 10);
		token = strtok(NULL, "|");
		int usec = atoi(token);
		epoch = epoch + usec/1000000.0;
		if (num_pkts == 0)
		  firsttime = epoch;
		num_pkts++;
		if (firsttimeinfile == 0)
		  firsttimeinfile = epoch;
		allflows++;
		if (allflows % 1000000 == 0)
		  {
		    double diff = time(0) - start;
		    cout<<"Processed "<<allflows<<", 1M in "<<diff<<endl;
		    start = time(0);
		  }
		processedflows++;
		// Each second
		if (curtime - lasttime >= 1) //processedflows == (int)parms["max_flows"])
		  {
		    pthread_mutex_lock (&cells_lock);
		    cout<<std::fixed<<"Done "<<time(0)<<" curtime "<<curtime<<" flows "<<processedflows<<endl;
		    
		    // This one we will work on next
		    crear = (crear + 1)%QSIZE;
		    if (crear == cfront && !cempty)
		      {
			perror("QSIZE is too small\n");
			exit(1);
		      }
		    // zero out stats
		    cell* c = &cells[crear];
		    memset(c->databrick_p, 0, BRICK_DIMENSION*sizeof(int));
		    memset(c->databrick_s, 0, BRICK_DIMENSION*sizeof(int));
		    memset(c->wfilter_p, 0, BRICK_DIMENSION*sizeof(unsigned int));
		    memset(c->wfilter_s, 0, BRICK_DIMENSION*sizeof(int));	  
		    // and it will soon be full
		    cempty = false;
		    pthread_mutex_unlock (&cells_lock);
		    
		    pthread_t thread_id;
		    pthread_create (&thread_id, NULL, reset_transmit, NULL);
		    pthread_detach(thread_id);
		    processedflows = 0;
		    lasttime = curtime;
		  }
		amonProcessingNfdump(line, epoch); 
	      }
	  }
	else
	  {
	    char ebuf[MAXLINE];
	    pcap_t *pt;
	    if (is_live)
	      pt = pcap_open_live(file, BUFSIZ, 1, 1000, ebuf);
	    else
	      pt = pcap_open_offline (file, ebuf);
	    u_char* p;
	    struct pcap_pkthdr *h;
	    if (pt)
	      {
		while (true)
		  {
		    int rc = pcap_next_ex(pt, &h, (const u_char **) &p);
		    if (rc <= 0)
		      break;
		    struct ether_header* eth_header = (struct ether_header *) p;
    
		    if (ntohs(eth_header->ether_type) != ETHERTYPE_IP) 
		      continue;
		    double epoch = h->ts.tv_sec + h->ts.tv_usec/1000000.0;

		    if (num_pkts == 0)
		      firsttime = epoch;
		    num_pkts++;
		    if (firsttimeinfile == 0)
		      firsttimeinfile = epoch;
		    allflows++;
		    if (allflows % 1000000 == 0)
		      {
			double diff = time(0) - start;
			cout<<"Processed "<<allflows<<", 1M in "<<diff<<endl;
			start = time(0);
		      }
		    processedflows++;
		    // Each second
		    if (curtime - lasttime >= 1) //processedflows == (int)parms["max_flows"])
		      {
			pthread_mutex_lock (&cells_lock);
			cout<<std::fixed<<"Done "<<time(0)<<" curtime "<<curtime<<" flows "<<processedflows<<endl;
		    
			// This one we will work on next
			crear = (crear + 1)%QSIZE;
			if (crear == cfront && !cempty)
			  {
			    perror("QSIZE is too small\n");
			    exit(1);
			  }
			// zero out stats
			cell* c = &cells[crear];
			memset(c->databrick_p, 0, BRICK_DIMENSION*sizeof(int));
			memset(c->databrick_s, 0, BRICK_DIMENSION*sizeof(int));
			memset(c->wfilter_p, 0, BRICK_DIMENSION*sizeof(unsigned int));
			memset(c->wfilter_s, 0, BRICK_DIMENSION*sizeof(int));	  
			// and it will soon be full
			cempty = false;
			pthread_mutex_unlock (&cells_lock);
			
			pthread_t thread_id;
			pthread_create (&thread_id, NULL, reset_transmit, NULL);
			pthread_detach(thread_id);
			processedflows = 0;
			lasttime = curtime;
		      }
		    amonProcessingPcap(h, p, epoch); 
		  }
	      }
	  }
	cout<<"Done with the file "<<file<<" time "<<time(0)<<endl;
	pclose(nf);
	if (endfile && strstr(file,endfile) != 0)
	  break;
      }
    }
  save_history();
  return 0;
}
