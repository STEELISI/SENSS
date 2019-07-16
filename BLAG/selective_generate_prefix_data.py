#This script is used to generate the scores file for individual /16 prefixes which can be used for analysis
import os
import glob
import json
import time
import numpy as np
from blacklist_support import check_overlap,half_life,parser

def generate_prefix_data(current_prefix,reference_end_time,date,output_folder,dataset,accuracy_scores,avoid_blacklists):
		#Reading data from raw file
		ip_16_dict={}
		ip_16_dict[current_prefix]=set()
		all_ips_data={}

		f=open(output_folder+"/"+current_prefix,"r")
		for line in f:
			#Sometimes data are not being written properly
			try:
				ip=line.strip().split("qwerty123")[0]
				value=json.loads(line.strip().split("qwerty123")[1])
			except:
				continue
			all_ips_data[ip]=value
			ip_16_dict[current_prefix].add(ip)
		f.close()

		#Getting relevant blacklist
		
		all_blacklists=set()
		for ip in ip_16_dict[current_prefix]:
			for blacklist,_ in all_ips_data[ip]["Blacklist"].iteritems():
				blacklist=blacklist.split(".")[0]
				if blacklist in avoid_blacklists:
					continue
				all_blacklists.add(blacklist)
		all_blacklists=sorted(list(all_blacklists))

		hf_array=[]
		h_array=[]
		f_array=[]
		ip_blacklist_map={}
		for ip in ip_16_dict[current_prefix]:
			ip_24=".".join(ip.split(".")[0:3])+".0"
			skip_chaos=False
			temp_array_hf=[0]*len(all_blacklists)
			temp_array_h=[0]*len(all_blacklists)
			temp_array_f=[0]*len(all_blacklists)
			all_late=0
			for blacklist,blacklist_data in all_ips_data[ip]["Blacklist"].iteritems():
				blacklist=blacklist.split(".")[0].strip()
				if blacklist in avoid_blacklists:
					continue
				if blacklist=="chaosreigns_iprep100":
					skip_chaos=True
					continue

				start=blacklist_data["Start Time"]
				last_end_time=parser("Sun Jan 5 22:10:02 UTC 2016")
				last_end_string=""
				start_included=False
				unknown_flag=False
				for timeline in blacklist_data["History"].split("|")[1:]:
					if start in timeline:
						start_included=True
					if "unknown" in timeline:
						unknown_flag=True
						break
					start_time=parser(timeline.strip().split("    ")[0].strip())
					end_time=parser(timeline.strip().split("    ")[1].strip())
					if end_time > last_end_time:
						last_end_time=end_time
						last_end_string=timeline.strip().split("    ")[1].strip()
				if unknown_flag==True:
					continue

				delay=reference_end_time-last_end_time
				if start_included==False:
					start=parser(start)
					if start<=reference_end_time:
						delay=0
				#The IP was reported after the event
				if delay<0:
					all_late=all_late+1
					continue
				total_etime=half_life(delay,29)
				if ip not in ip_blacklist_map:
					ip_blacklist_map[ip]=set()
				ip_blacklist_map[ip].add(blacklist)
				
				try:
					false_positives_score=1-accuracy_scores[ip_24][blacklist]
				except:
					false_positives_score=0

				total_score_hf=float(total_etime+false_positives_score)/2
				total_score_h=total_etime
				total_score_f=false_positives_score


				if false_positives_score==0:
					total_score_hf=total_score_h
					total_score_h=total_score_h
					total_score_f=0

				if total_score_hf<=0:
					total_score_hf=0.1
				if total_score_hf>1:
					total_score_hf=1
				total_score_hf=total_score_hf*10
				temp_array_hf[all_blacklists.index(blacklist)]=total_score_hf


				if total_score_h<=0:
					total_score_h=0.1
				if total_score_h>1:
					total_score_h=1
				total_score_h=total_score_h*10
				temp_array_h[all_blacklists.index(blacklist)]=total_score_h


				if total_score_f<=0:
					total_score_f=0.1
				if total_score_f>1:
					total_score_f=1
				total_score_f=total_score_f*10
				temp_array_f[all_blacklists.index(blacklist)]=total_score_f


			if skip_chaos==True or all_late==len(all_ips_data[ip]["Blacklist"]):
				continue
			hf_array.append((ip,temp_array_hf,"hf"))
			f_array.append((ip,temp_array_f,"f"))
			h_array.append((ip,temp_array_h,"h"))
		return hf_array,f_array,h_array,ip_blacklist_map
