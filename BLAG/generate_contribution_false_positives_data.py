import sys
import glob
from blacklist_support import check_overlap,half_life,parser,pre_parser
import time
import json
from dateutil.parser import parse
import operator
import datetime
#Change it to per time
def generate_contribution_data():
        month_array=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        mirai_ham_list=set()
        darknet_ham_list=set()
        mailinator_ham_list=set()

        all_16=set()
        mailinator_ham_24={}
        mirai_ham_24={}
        darknet_ham_24={}
	darknet_ips={}
	mirai_ips={}
	mailinator_ips={}
        file_list=glob.glob("training_data/mailinator_training_data/*")
        for file in file_list:
                f=open(file,"r")
                date=file.split("/")[-1]
                for line in f:
                        ip=line.strip()
                        ip_16=".".join(ip.split(".")[0:2])+".0.0"
                        ip_24=".".join(ip.split(".")[0:3])+".0"
                        if ip_24 not in mailinator_ham_24:
                                mailinator_ham_24[ip_24]=set()
                        mailinator_ham_24[ip_24].add(date)
                        mailinator_ham_list.add(ip)
                        all_16.add(ip_16)
			if date not in mailinator_ips:
				mailinator_ips[date]=set()
			mailinator_ips[date].add(ip)
                f.close()
        file_list=glob.glob("training_data/mirai_training_data/*")
        for file in file_list:
                f=open(file,"r")
                date=file.split("/")[-1]
                for line in f:
                        ip=line.strip()
                        ip_16=".".join(ip.split(".")[0:2])+".0.0"
                        ip_24=".".join(ip.split(".")[0:3])+".0"
                        if ip_24 not in mirai_ham_24:
                                mirai_ham_24[ip_24]=set()
                        mirai_ham_24[ip_24].add(date)
                        mirai_ham_list.add(ip)
                        all_16.add(ip_16)
			if date not in mirai_ips:
				mirai_ips[date]=set()
			mirai_ips[date].add(ip)
                f.close()

        file_list=glob.glob("training_data/darknet_training_data/*")
        for file in file_list:
                f=open(file,"r")
                date=file.split("/")[-1]
                for line in f:
                        ip=line.strip()
                        ip_16=".".join(ip.split(".")[0:2])+".0.0"
                        ip_24=".".join(ip.split(".")[0:3])+".0"
                        if ip_24 not in darknet_ham_24:
                                darknet_ham_24[ip_24]=set()
                        darknet_ham_24[ip_24].add(date)
                        darknet_ham_list.add(ip)
			if date not in darknet_ips:
				darknet_ips[date]=set()
			darknet_ips[date].add(ip)
                        all_16.add(ip_16)
                f.close()

        active_16=set()
        f=open("blacklist_support_files/active_16","r")
        for line in f:
                active_16.add(line.strip())
        f.close()
        common=active_16.intersection(all_16)
        print "Common",len(common)
        mailinator_blacklist={}
        mirai_blacklist={}
        darknet_blacklist={}
	mailinator_false_positives={}
	mirai_false_positives={}
	darknet_false_positives={}
        total=len(common)
        done_count=0
	break_flag=False
        for ip_16 in common:
                done_count=done_count+1
                f=open("../../Results6/"+ip_16,"r")
                for line in f:
                        ip=line.strip().split("qwerty123")[0]
                        ip_24=".".join(ip.split(".")[0:3])+".0"
                        if ip_24 in mailinator_ham_24 or ip_24 in mirai_ham_24 or ip_24 in darknet_ham_24:
                                data=json.loads(line.strip().split("qwerty123")[1])["Blacklist"]
                                for blacklist,blacklist_data in data.iteritems():
                                        blacklist=blacklist.split(".")[0].strip()
                                        if blacklist=="chaosreigns_iprep100":
                                                skip_chaos=True
                                                continue
                                        start=blacklist_data["Start Time"]
                                        start_included=False
                                        for timeline in blacklist_data["History"].split("|")[1:]:
                                                if start in timeline:
                                                        start_included=True
                                                if "unknown" in timeline:
                                                        break
                                                start_time=parser(timeline.strip().split("    ")[0].strip())
                                                end_time=parser(timeline.strip().split("    ")[1].strip())


                                                if ip_24 in mailinator_ham_24:
                                                        for mailinator_end_time in mailinator_ham_24[ip_24]:
                                                                o_time=pre_parser(mailinator_end_time)
                                                                if o_time>=start_time and o_time<=end_time:
                                                                        if mailinator_end_time not in mailinator_blacklist:
                                                                                mailinator_blacklist[mailinator_end_time]={}
                                                                        if ip_24 not in mailinator_blacklist[mailinator_end_time]:
                                                                                mailinator_blacklist[mailinator_end_time][ip_24]={}
                                                                        if blacklist not in mailinator_blacklist[mailinator_end_time][ip_24]:
                                                                                mailinator_blacklist[mailinator_end_time][ip_24][blacklist]=0
                                                                        mailinator_blacklist[mailinator_end_time][ip_24][blacklist]=mailinator_blacklist[mailinator_end_time][ip_24][blacklist]+1
									if ip in mailinator_ips[mailinator_end_time]:
										break_flag=True
										if mailinator_end_time not in mailinator_false_positives:
											mailinator_false_positives[mailinator_end_time]={}
										if ip_24 not in mailinator_false_positives[mailinator_end_time]:
											mailinator_false_positives[mailinator_end_time][ip_24]={}
										if blacklist not in mailinator_false_positives[mailinator_end_time][ip_24]:
                                                                                	mailinator_false_positives[mailinator_end_time][ip_24][blacklist]=set()
										mailinator_false_positives[mailinator_end_time][ip_24][blacklist].add(ip)

                                                if ip_24 in mirai_ham_24:
                                                        for mirai_end_time in mirai_ham_24[ip_24]:
                                                                o_time=pre_parser(mirai_end_time)
                                                                if o_time>=start_time and o_time<=end_time:
                                                                        if mirai_end_time not in mirai_blacklist:
                                                                                mirai_blacklist[mirai_end_time]={}
                                                                        if ip_24 not in mirai_blacklist[mirai_end_time]:
                                                                                mirai_blacklist[mirai_end_time][ip_24]={}
                                                                        if blacklist not in mirai_blacklist[mirai_end_time][ip_24]:
                                                                                mirai_blacklist[mirai_end_time][ip_24][blacklist]=0
                                                                        mirai_blacklist[mirai_end_time][ip_24][blacklist]=mirai_blacklist[mirai_end_time][ip_24][blacklist]+1
									if ip in mirai_ips[mirai_end_time]:
										break_flag=True
										if mirai_end_time not in mirai_false_positives:
											mirai_false_positives[mirai_end_time]={}
										if ip_24 not in mirai_false_positives[mirai_end_time]:
											mirai_false_positives[mirai_end_time][ip_24]={}
										if blacklist not in mirai_false_positives[mirai_end_time][ip_24]:
                                                                                	mirai_false_positives[mirai_end_time][ip_24][blacklist]=set()
										mirai_false_positives[mirai_end_time][ip_24][blacklist].add(ip)

                                                if ip_24 in darknet_ham_24:
                                                        for darknet_end_time in darknet_ham_24[ip_24]:
                                                                o_time=pre_parser(darknet_end_time)
                                                                if o_time>=start_time and o_time<=end_time:
                                                                        if darknet_end_time not in darknet_blacklist:
                                                                                darknet_blacklist[darknet_end_time]={}
                                                                        if ip_24 not in darknet_blacklist[darknet_end_time]:
                                                                                darknet_blacklist[darknet_end_time][ip_24]={}
                                                                        if blacklist not in darknet_blacklist[darknet_end_time][ip_24]:
                                                                                darknet_blacklist[darknet_end_time][ip_24][blacklist]=0
                                                                        darknet_blacklist[darknet_end_time][ip_24][blacklist]=darknet_blacklist[darknet_end_time][ip_24][blacklist]+1
									if ip in darknet_ips[darknet_end_time]:
										break_flag=True
										if darknet_end_time not in darknet_false_positives:
											darknet_false_positives[darknet_end_time]={}
										if ip_24 not in darknet_false_positives[darknet_end_time]:
											darknet_false_positives[darknet_end_time][ip_24]={}
										if blacklist not in darknet_false_positives[darknet_end_time][ip_24]:
                                                                                	darknet_false_positives[darknet_end_time][ip_24][blacklist]=set()
										darknet_false_positives[darknet_end_time][ip_24][blacklist].add(ip)





                                        if start_included==False:
                                                start=parser(start)
                                                if ip_24 in mailinator_ham_24:
                                                        for mailinator_end_time in mailinator_ham_24[ip_24]:
                                                                o_time=pre_parser(mailinator_end_time)
                                                                if o_time>=start:
                                                                        if mailinator_end_time not in mailinator_blacklist:
                                                                                mailinator_blacklist[mailinator_end_time]={}
                                                                        if ip_24 not in mailinator_blacklist[mailinator_end_time]:
                                                                                mailinator_blacklist[mailinator_end_time][ip_24]={}
                                                                        if blacklist not in mailinator_blacklist[mailinator_end_time][ip_24]:
                                                                                mailinator_blacklist[mailinator_end_time][ip_24][blacklist]=0
                                                                        mailinator_blacklist[mailinator_end_time][ip_24][blacklist]=mailinator_blacklist[mailinator_end_time][ip_24][blacklist]+1
									if ip in mailinator_ips[mailinator_end_time]:
										break_flag=True
										if mailinator_end_time not in mailinator_false_positives:
											mailinator_false_positives[mailinator_end_time]={}
										if ip_24 not in mailinator_false_positives[mailinator_end_time]:
											mailinator_false_positives[mailinator_end_time][ip_24]={}
										if blacklist not in mailinator_false_positives[mailinator_end_time][ip_24]:
											mailinator_false_positives[mailinator_end_time][ip_24][blacklist]=set()
										mailinator_false_positives[mailinator_end_time][ip_24][blacklist].add(ip)


                                                if ip_24 in mirai_ham_24:
                                                        for mirai_end_time in mirai_ham_24[ip_24]:
                                                                o_time=pre_parser(mirai_end_time)
                                                                if o_time>=start:
                                                                        if mirai_end_time not in mirai_blacklist:
                                                                                mirai_blacklist[mirai_end_time]={}
                                                                        if ip_24 not in mirai_blacklist[mirai_end_time]:
                                                                                mirai_blacklist[mirai_end_time][ip_24]={}
                                                                        if blacklist not in mirai_blacklist[mirai_end_time][ip_24]:
                                                                                mirai_blacklist[mirai_end_time][ip_24][blacklist]=0
                                                                        mirai_blacklist[mirai_end_time][ip_24][blacklist]=mirai_blacklist[mirai_end_time][ip_24][blacklist]+1
									if ip in mirai_ips[mirai_end_time]:
										break_flag=True
										if mirai_end_time not in mirai_false_positives:
											mirai_false_positives[mirai_end_time]={}
										if ip_24 not in mirai_false_positives[mirai_end_time]:
											mirai_false_positives[mirai_end_time][ip_24]={}
										if blacklist not in mirai_false_positives[mirai_end_time][ip_24]:
											mirai_false_positives[mirai_end_time][ip_24][blacklist]=set()
										mirai_false_positives[mirai_end_time][ip_24][blacklist].add(ip)

                                                if ip_24 in darknet_ham_24:
                                                        for darknet_end_time in darknet_ham_24[ip_24]:
                                                                o_time=pre_parser(darknet_end_time)
                                                                if o_time>=start:
                                                                        if darknet_end_time not in darknet_blacklist:
                                                                                darknet_blacklist[darknet_end_time]={}
                                                                        if ip_24 not in darknet_blacklist[darknet_end_time]:
                                                                                darknet_blacklist[darknet_end_time][ip_24]={}
                                                                        if blacklist not in darknet_blacklist[darknet_end_time][ip_24]:
                                                                                darknet_blacklist[darknet_end_time][ip_24][blacklist]=0
                                                                        darknet_blacklist[darknet_end_time][ip_24][blacklist]=darknet_blacklist[darknet_end_time][ip_24][blacklist]+1
									if ip in darknet_ips[darknet_end_time]:
										break_flag=True
										if darknet_end_time not in darknet_false_positives:
											darknet_false_positives[darknet_end_time]={}
										if ip_24 not in darknet_false_positives[darknet_end_time]:
											darknet_false_positives[darknet_end_time][ip_24]={}
										if blacklist not in darknet_false_positives[darknet_end_time][ip_24]:
											darknet_false_positives[darknet_end_time][ip_24][blacklist]=set()
										darknet_false_positives[darknet_end_time][ip_24][blacklist].add(ip)


                print done_count,total
                f.close()
		#if break_flag==True:
		#	break
        for date,data in mailinator_blacklist.iteritems():
                f_mailinator=open("contributions/contributions_mailinator/"+date,"w")
                for key,value in data.iteritems():
                        for bl,count in value.iteritems():
                                f_mailinator.write(key+","+bl+","+str(count)+"\n")
                f_mailinator.close()

        for date,data in mirai_blacklist.iteritems():
                f_mirai=open("contributions/contributions_mirai/"+date,"w")
                for key,value in data.iteritems():
                        for bl,count in value.iteritems():
                                f_mirai.write(key+","+bl+","+str(count)+"\n")
                f_mirai.close()

        for date,data in darknet_blacklist.iteritems():
                f_darknet=open("contributions/contributions_darknet/"+date,"w")
                for key,value in data.iteritems():
                        for bl,count in value.iteritems():
                                f_darknet.write(key+","+bl+","+str(count)+"\n")
                f_darknet.close()


	for date,data in mailinator_false_positives.iteritems():
		f_mailinator=open("false_positives/mailinator_false_positives/"+date,"w")
		for ip_24,value in data.iteritems():
			for bl,ips in value.iteritems():
				f_mailinator.write(ip_24+","+bl+","+str(len(ips))+"\n")
		f_mailinator.close()

	for date,data in mirai_false_positives.iteritems():
		f_mirai=open("false_positives/mirai_false_positives/"+date,"w")
		for ip_24,value in data.iteritems():
			for bl,ips in value.iteritems():
				f_mirai.write(ip_24+","+bl+","+str(len(ips))+"\n")
		f_mirai.close()

	for date,data in darknet_false_positives.iteritems():
		f_darknet=open("false_positives/darknet_false_positives/"+date,"w")
		for ip_24,value in data.iteritems():
			for bl,ips in value.iteritems():
				f_darknet.write(ip_24+","+bl+","+str(len(ips))+"\n")
		f_darknet.close()


generate_contribution_data()
