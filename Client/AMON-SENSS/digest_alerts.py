# This file continuously reads alerts.txt
# and keeps track of signatures, which should be
# sent to SENSS. If an older signature is not useful
# anymore, e.g., because the newer signature is better,
# it deletes it and sends a more useful signature.
import time, sys, os

targets = dict()
limit = 0

class Target:
    def __init__(self, ip):
        self.ip = ip
        self.signatures = []
        
class Signature:
    
    def __init__(self, line):
        self.time = None
        self.src = None
        self.sport = None
        self.dst = None
        self.dport = None
        self.proto = None
        self.rate = 0
        ar = line.split()
        self.time = int(ar[1])
        self.rate = int(ar[4])*8/1000000000.0;
        self.oci = int(ar[5])
        for delim in ("src ip", "src port", "dst ip", "dst port", "proto"):
            i = line.find(delim)
            if (i > -1):
                j = line.find(" ", i+len(delim)+1)
                arg = line[i+len(delim)+1:j]
                if (delim == "src ip"):
                  self.src = arg
                elif (delim == "src port"):
                    self.sport = arg
                elif (delim == "dst ip"):
                    self.dst = arg
                elif (delim == "dst port"):
                    self.dport = arg
                elif (delim == "proto"):
                    self.proto = arg

    def __eq__(self, other):
        return (self.src == other.src) and (self.sport == other.sport) and (self.dst == other.dst) and (self.dport == other.dport)

    def __ne__(self, other):
        return not self.__eq__(other)

    def contains(self,s):
        if ((self.src == "0.0.0.0" or self.src == None or self.src == s.src) and
            (self.sport == None or self.sport == s.sport) and
            (self.dst == "0.0.0.0" or self.dst == None or self.dst == s.dst) and
            (self.dport == None or self.dport == s.dport) and
            (self.proto == s.proto)):
            return True
        else:
            return False


    def printsig(self):
        return self.time , " rate " , self.rate, "Gbps oci ", self.oci, " src ip ", self.src, " and src port ", self.sport, " and dst ip ", self.dst, " and dst port ", self.dport, " and proto ", self.proto

def insertSignature(sig):
    if (sig.dst not in targets.keys()):
        targets[sig.dst] = Target(sig.dst)
    siglist = targets[sig.dst].signatures
    for s in siglist:
        if (sig == s):
            if (sig.rate > s.rate):
                s.rate = sig.rate
            return
        if (sig.contains(s)):
            targets[sig.dst].signatures.remove(s)
        elif(s.contains(sig)):
            if (sig.rate > s.rate):
                s.rate = sig.rate
            return
        else:
            pass    
    # We came here because this sig is like none other
    # insert it
    targets[sig.dst].signatures.append(sig)
        
# Continuously read from the alert file
def follow(name):
    current = open(name, "r")
    curino = os.fstat(current.fileno()).st_ino
    while True:
        while True:
            line = current.readline()
            if not line:
                break
            yield line

        try:
            if os.stat(name).st_ino != curino:
                new = open(name, "r")
                current.close()
                current = new
                curino = os.fstat(current.fileno()).st_ino
                continue
        except IOError:
            pass
        time.sleep(1)

def processalert(line):
# 0 1449680158 START 497 18315152 8456 src ip 23.45.32.0 and dst ip 0.0.0.0 and proto tcp
    items = line.split()
    oci = items[5]
    s = Signature(line)
    if (s.rate >= limit):
        insertSignature(s)
    for t in targets:
        for ss in targets[t].signatures:
            print "Signature ",ss.printsig()
    print "\n\n\n\n\n\n";
        
# Alert file is specified on the cmd line        
if __name__ == '__main__':
    loglines = follow(sys.argv[1])
    limit = float(sys.argv[2])
    for line in loglines:
        processalert(line)
