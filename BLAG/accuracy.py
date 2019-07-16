from termcolor import colored
import time
import sys
import json
import glob
import operator
import multiprocessing

dataset=sys.argv[1]

###Generate stats for NO-FP###
###------------------------###
###1) Write the false posiitves to file per date and per dataset. This is done in analyse_fp_tp function
###2) Generate the blacklist count for every dataset. This is used to remove the top 10 % of blacklists which contribute to false positives. generate_blacklist_fp_count
###3) Isolate data based on the false positives blacklists and run expansion on it -- generate_10_fp
###4) Generate results for expansion and no-expansion for NO- FP generate_10_fp_results
###------------------------###
def generate_blacklist_fp_count(dataset):
        print "No Expansion"
        fp={}
        fp_16={}
        fp_16_set=set()
        fp_24={}
        f=open("top_10_fp/false_positives_expansion_"+dataset,"r")
        for line in f:
                ip=line.strip().split(",")[0]
                ip_16=".".join(ip.split(".")[0:2])+".0.0"
                ip_24=".".join(ip.split(".")[0:3])+".0"
                date=line.strip().split(",")[1]
                if date not in fp:
                        fp[date]=set()
                if date not in fp_16:
                        fp_16[date]={}
                if ip_16 not in fp_16[date]:
                        fp_16[date][ip_16]=set()
                fp[date].add(ip)
                if date not in fp_24:
                        fp_24[date]={}
                if ip_24 not in fp_24[date]:
                        fp_24[date][ip_24]=set()
                fp_24[date][ip_24].add(ip)
                fp_16[date][ip_16].add(ip)
        f.close()
        active_16=set()
        f=open("../../../google_blacklist_lib/blacklist_support_files/active_16","r")
        for line in f:
                active_16.add(line.strip())
        f.close()
        blacklist_count={}	
	count=0
        for date,ip_16_data in fp_16.iteritems():
		count=count+1
		print count,len(fp_16)
                if date not in blacklist_count:
                        blacklist_count[date]={}
                all_16=set()
                for ip_16 in ip_16_data:
                        all_16.add(ip_16)
                common=all_16.intersection(active_16)
                for ip_16 in common:
                        f=open("../../Results6/"+ip_16,"r")
                        for line in f:
                                ip=line.strip().split("qwerty123")[0]
                                ip_24=".".join(ip.split(".")[0:3])+".0"
                                if ip_24 in fp_24[date]:
                                        data=json.loads(line.strip().split("qwerty123")[1])
                                        for bl,_ in data["Blacklist"].iteritems():
                                                if bl not in blacklist_count[date]:
                                                        blacklist_count[date][bl]=0
                                                blacklist_count[date][bl]=blacklist_count[date][bl]+1
        for date,bl_data in blacklist_count.iteritems():
                fw=open("top_10_fp/false_positives/"+dataset+"/"+date+"_no_expansion","w")
                for bl,count in bl_data.iteritems():
                        fw.write(bl+","+str(count)+"\n")
                fw.close()
        print "Expansion"
        fp={}
        fp_16={}
        fp_16_set=set()
        fp_24={}
        f=open("top_10_fp/false_positives_expansion_"+dataset,"r")
        for line in f:
                ip=line.strip().split(",")[0]
                ip_16=".".join(ip.split(".")[0:2])+".0.0"
                ip_24=".".join(ip.split(".")[0:3])+".0"
                date=line.strip().split(",")[1]
                if date not in fp:
                        fp[date]=set()
                if date not in fp_16:
                        fp_16[date]={}
                if ip_16 not in fp_16[date]:
                        fp_16[date][ip_16]=set()
                fp[date].add(ip)
                if date not in fp_24:
                        fp_24[date]={}
                if ip_24 not in fp_24[date]:
                        fp_24[date][ip_24]=set()
                fp_24[date][ip_24].add(ip)
                fp_16[date][ip_16].add(ip)
        f.close()
        active_16=set()
        f=open("../../google_blacklist_lib/blacklist_support_files/active_16","r")
        for line in f:
                active_16.add(line.strip())
        f.close()
        blacklist_count={}
	count=0
        for date,ip_16_data in fp_16.iteritems():
		count=count+1
		print count,len(fp_16)
                if date not in blacklist_count:
                        blacklist_count[date]={}
                all_16=set()
                for ip_16 in ip_16_data:
                        all_16.add(ip_16)
                common=all_16.intersection(active_16)
                for ip_16 in common:
                        f=open("../../Results6/"+ip_16,"r")
                        for line in f:
                                ip=line.strip().split("qwerty123")[0]
                                if ip in fp_16[date][ip_16]:
                                        data=json.loads(line.strip().split("qwerty123")[1])
                                        for bl,_ in data["Blacklist"].iteritems():
                                                if bl not in blacklist_count[date]:
                                                        blacklist_count[date][bl]=0
                                                blacklist_count[date][bl]=blacklist_count[date][bl]+1
        for date,bl_data in blacklist_count.iteritems():
                fw=open("top_10_fp/false_positives/"+dataset+"/"+date+"_expansion","w")
                for bl,count in bl_data.iteritems():
                        fw.write(bl+","+str(count)+"\n")
                fw.close()

#Generates blacklists without the TOP 10
def generate_10_fp(dataset):
        file_list=glob.glob("top_10_fp/false_positives/"+dataset+"/*")
        blacklist_count={}
        for file in file_list:
                f=open(file,"r")
                for line in f:
                        bl=line.strip().split(",")[0]
                        count=int(line.strip().split(",")[1])
                        if bl not in blacklist_count:
                                blacklist_count[bl]=0
                        blacklist_count[bl]=blacklist_count[bl]+count
                f.close()
        blacklist_count=sorted(blacklist_count.items(),key=operator.itemgetter(1),reverse=True)
        blacklists=[]
        for item in blacklist_count:
                print item
                blacklists.append(item[0])
        ten_percent=int(0.1*len(blacklist_count))
        avoid_blacklists=blacklists[:ten_percent]
        avoid_blacklists=set()
        f=open(dataset+"_avoid","r")
        for line in f:
                avoid_blacklists.add(line.strip())
        f.close()
        file_list=glob.glob("../../all_results/"+dataset+"/results_"+dataset+"/*")
        for file in file_list:
                blag_ips=set()
                date=file.split("/")[-1].split("_")[0]
                print date
                f=open(file,"r")
                blag_ip_16=set()
                for line in f:
                        ip=line.strip().split(",")[1]
                        ip_16=".".join(ip.split(".")[0:2])+".0.0"
                        blag_ips.add(ip)
                        blag_ip_16.add(ip_16)
                f.close()
                fp_10=set()
                for ip_16 in blag_ip_16:
                        f=open("../../Results6/"+ip_16,"r")
                        for line in f:
                                ip=line.strip().split("qwerty123")[0]
                                if ip in blag_ips:
                                        data=json.loads(line.strip().split("qwerty123")[1])
                                        all_blacklists=set()
                                        for bl,_ in data["Blacklist"].iteritems():
                                                if bl not in avoid_blacklists:
                                                        all_blacklists.add(bl)
                                        if len(all_blacklists)!=0:
                                                fp_10.add(ip)
                fw=open("top_10_fp/fp_10/"+dataset+"/"+date,"w")
                for ip in fp_10:
                        fw.write(ip+"\n")
                fw.close()


def generate_10_fp_results(dataset):
        ham_ips={}
        ham_ips_24={}
        file_list=glob.glob("../../google_blacklist_lib/testing_data/"+dataset+"_testing_data/*")
        all_dates=set()
        for file in file_list:
                date=file.split("/")[-1]
                all_dates.add(date)
                f=open(file,"r")
                for line in f:
                        ip=line.strip()
                        if date not in ham_ips:
                                        ham_ips[date]=set()
                        ham_ips[date].add(ip)
                        ip_24=".".join(ip.split(".")[0:3])+".0"
                        if date not in ham_ips_24:
                                        ham_ips_24[date]={}
                        if ip_24 not in ham_ips_24[date]:
                                ham_ips_24[date][ip_24]=set()
                        ham_ips_24[date][ip_24].add(ip)
                f.close()
        if dataset=="mailinator":
                f=open("../../google_blacklist_lib/blacklist_support_files/ham","r")
                for line in f:
                        ip=line.strip().split(",")[0]
                        ip_24=".".join(ip.split(".")[0:3])+".0"
                        for date in all_dates:
                                ham_ips[date].add(ip)
                                if ip_24 not in ham_ips_24[date]:
                                        ham_ips_24[date][ip_24]=set()
                                ham_ips_24[date][ip_24].add(ip)
                f.close()
        #Reads expansion score
        expansion_score={}
        f=open("fp_tp/"+dataset,"r")
        for line in f:
                reported_dates=[]
                ip_24=line.strip().split("qwerty123")[0]
                data=json.loads(line.strip().split("qwerty123")[1])
                tp=0
                fp=0
                all=0
                expansion_score[ip_24]={}
                for date in all_dates:
                        if date in data:
                                tp=tp+data[date]["TP"]
                                fp=fp+data[date]["FP"]
                                all=all+data[date]["all"]
                        #FPTP=1-(# of FP/(# of TP+# of FP))
                        expansion_score[ip_24][date]={}
                        expansion_score[ip_24][date]["TP"]=tp
                        expansion_score[ip_24][date]["FP"]=fp
                        expansion_score[ip_24][date]["all"]=all
        f.close()
        f=open("fp_tp/"+dataset+"_threshold_tp","r")
        for line in f:
                ip_24=line.strip().split("qwerty123")[0]
                data=json.loads(line.strip().split("qwerty123")[1])
                threshold_tp=0
                for date in all_dates:
                        if date in data:
                                threshold_tp=threshold_tp+data[date]
                        if ip_24 not in expansion_score:
                                expansion_score[ip_24]={}
                        if date not in expansion_score[ip_24]:
                                expansion_score[ip_24][date]={}
                                expansion_score[ip_24][date]["TP"]=0
                                expansion_score[ip_24][date]["FP"]=0
                                expansion_score[ip_24][date]["threshold_TP"]=0
                        expansion_score[ip_24][date]["threshold_TP"]=threshold_tp
        f.close()

        print "Done reading expansion scores"
        mismanaged={}
        f=open("../../google_blacklist_lib/blacklist_support_files/mismanaged_networks","r")
        for line in f:
                ip_24=line.strip().split(",")[0]
                score=float(line.strip().split(",")[1])
                mismanaged[ip_24]=score
        f.close()
        spatio_temporal={}
        filling_degree={}
        f=open("../../google_blacklist_lib/blacklist_support_files/fd_stu_all","r")
        for line in f:
                ip_24=line.strip().split(",")[0]
                fd=float(line.strip().split(",")[1])
                stu=float(line.strip().split(",")[2])
                spatio_temporal[ip_24]=stu
                filling_degree[ip_24]=fd
        f.close()
        spam_ips_24={}
        spam_ips={}
        total_spam=0
        if dataset=="darknet":
                dataset_file_list=glob.glob("../../google_blacklist_lib/relevant_data/split_darknet/*")
        if dataset=="mirai":
                dataset_file_list=glob.glob("../../google_blacklist_lib/relevant_data/"+dataset+"_ip_data/2016-09-*")
        if dataset=="mailinator":
                dataset_file_list=glob.glob("../../google_blacklist_lib/relevant_data/"+dataset+"_ip_data/*")
        for file in dataset_file_list:
                date=file.split("/")[-1]
                if date not in spam_ips:
                        spam_ips_24[date]={}
                        spam_ips[date]=set()
                f=open(file,"r")
                for line in f:
                        ip=line.strip()
                        ip_24=".".join(ip.split(".")[0:3])+".0"
                        spam_ips[date].add(ip)
                        if ip_24 not in spam_ips_24[date]:
                                spam_ips_24[date][ip_24]=set()
                        spam_ips_24[date][ip_24].add(ip)
                f.close()
        file_list=glob.glob("fp_10/"+dataset+"/*")
        tp_expanded=0
        tp_not_expanded=0
        fp_expanded=0
        fp_not_expanded=0
        all_spam=0
        all_ham=0
        for key,value in spam_ips.iteritems():
                all_spam=all_spam+len(value)
        for key,value in ham_ips.iteritems():
                all_ham=all_ham+len(value)
        print "All spam",all_spam
        for file in file_list:
                date=file.split("/")[-1]
                fp_10_expanded=set()
                fp_10_not_expanded=set()
                local_ham_expanded=set()
                local_ham_not_expanded=set()
                f=open(file,"r")
                for line in f:
                        ip=line.strip()
                        ip_24=".".join(ip.split(".")[0:3])+".0"
                        if ip in spam_ips[date]:
                                fp_10_not_expanded.add(ip)
                        if ip in ham_ips[date]:
                                local_ham_not_expanded.add(ip)
                        ms=0
                        fd=0
                        stu=0
                        e_score=0
                        try:
                                e_tp=expansion_score[ip_24][date]["TP"]
                        except:
                                e_tp=0
                        try:
                                e_fp=expansion_score[ip_24][date]["FP"]
                        except:
                                e_fp=0
                        if e_tp==0 and e_fp==0:
                                e_score=0
                        else:
                                e_score=e_fp/float(e_tp+e_fp)
                        e_score=1-e_score
                        e_threshold=0.8
                        if e_score>=e_threshold:
                                if ip_24 in mismanaged:
                                        ms=mismanaged[ip_24]
                                if ip_24 in filling_degree:
                                        fd=filling_degree[ip_24]
                                if ip_24 in spatio_temporal:
                                        stu=spatio_temporal[ip_24]
                                if ms>=2 or fd>=0.8 or stu>=0.8:
                                        if ip_24 in spam_ips_24[date]:
                                                for ip1 in spam_ips_24[date][ip_24]:
                                                        fp_10_expanded.add(ip1)
                                        if ip_24 in ham_ips_24[date]:
                                                for ip1 in ham_ips_24[date][ip_24]:
                                                        local_ham_expanded.add(ip1)
                f.close()
                tp_expanded=tp_expanded+len(fp_10_expanded)
                tp_not_expanded=tp_not_expanded+len(fp_10_not_expanded)
                fp_expanded=fp_expanded+len(local_ham_expanded)
                fp_not_expanded=fp_not_expanded+len(local_ham_not_expanded)
                f.close()
	to_write={}
	to_write["not_expanded"]={}
        print "Before"
        print "Not expanded"
        print "Spam",tp_not_expanded,all_spam
        print "Ham",fp_not_expanded,all_ham
        recall=tp_not_expanded/float(all_spam)
        specificity=(all_ham-fp_not_expanded)/float(all_ham)
	to_write["not_expanded"]["recall"]=recall
	to_write["not_expanded"]["specificity"]=specificity
        print "Specificity",specificity,"Recall",recall
        print "Expanded"
        print "Spam",tp_expanded,all_spam
        print "Ham",fp_expanded
        recall=tp_expanded/float(all_spam)
        specificity=(all_ham-fp_expanded)/float(all_ham)
	to_write["expanded"]={}
	to_write["expanded"]["recall"]=recall
	to_write["expanded"]["specificity"]=specificity
        print "Specificity",specificity,"Recall",recall
	#fw=open("final_results/"+dataset+"/false_positives_10_"+dataset,"w")
	#fw.write(json.dumps(to_write))
	#fw.close()
#generate_10_fp_results(dataset)
###Generate Blacklist contribution by size###
###Used to remove blacklists by certain count and generate results
###1) Generate results which are present in ../blacklist_results_size
###file_list=[1,2,5,10,30,60,90,120,150,195]
###for file in file_list:
###        generate_blacklist_large_testing("../all_results/large_testing/results_"+str(file)+"_mailinator")
###2)Call function to generate specificity and recall

def generate_blacklist_large_testing(original_file):
        ham_ips={}
        ham_ips_24={}
        file_list=glob.glob("../../google_blacklist_lib/testing_data/mailinator_testing_data/*")
        all_dates=set()
        for file in file_list:
                date=file.split("/")[-1]
                all_dates.add(date)
                f=open(file,"r")
                for line in f:
                        ip=line.strip()
                        if date not in ham_ips:
                                        ham_ips[date]=set()
                        ham_ips[date].add(ip)
                        ip_24=".".join(ip.split(".")[0:3])+".0"
                        if date not in ham_ips_24:
                                        ham_ips_24[date]={}
                        if ip_24 not in ham_ips_24[date]:
                                ham_ips_24[date][ip_24]=set()
                        ham_ips_24[date][ip_24].add(ip)
                f.close()
        if True:
                f=open("../../google_blacklist_lib/blacklist_support_files/ham","r")
                for line in f:
                        ip=line.strip().split(",")[0]
                        ip_24=".".join(ip.split(".")[0:3])+".0"
                        for date in all_dates:
                                ham_ips[date].add(ip)
                                if ip_24 not in ham_ips_24[date]:
                                        ham_ips_24[date][ip_24]=set()
                                ham_ips_24[date][ip_24].add(ip)
                f.close()
        #Reads expansion score
        expansion_score={}
        f=open("../../other_res/fp_tp/mailinator","r")
        for line in f:
                reported_dates=[]
                ip_24=line.strip().split("qwerty123")[0]
                data=json.loads(line.strip().split("qwerty123")[1])
                tp=0
                fp=0
                all=0
                expansion_score[ip_24]={}
                for date in all_dates:
                        if date in data:
                                tp=tp+data[date]["TP"]
                                fp=fp+data[date]["FP"]
                                all=all+data[date]["all"]
                        #FPTP=1-(# of FP/(# of TP+# of FP))
                        expansion_score[ip_24][date]={}
                        expansion_score[ip_24][date]["TP"]=tp
                        expansion_score[ip_24][date]["FP"]=fp
                        expansion_score[ip_24][date]["all"]=all
        f.close()
        print "Done reading expansion scores"
        spatio_temporal={}
        filling_degree={}
        f=open("../../google_blacklist_lib/blacklist_support_files/fd_stu_all","r")
        for line in f:
                ip_24=line.strip().split(",")[0]
                fd=float(line.strip().split(",")[1])
                stu=float(line.strip().split(",")[2])
                spatio_temporal[ip_24]=stu
                filling_degree[ip_24]=fd
        f.close()
        spam_ips_24={}
        spam_ips={}
        total_spam=0
        dataset_file_list=glob.glob("../../google_blacklist_lib/relevant_data/mailinator_ip_data/*")
        for file in dataset_file_list:
                date=file.split("/")[-1]
                if date not in spam_ips:
                        spam_ips_24[date]={}
                        spam_ips[date]=set()
                f=open(file,"r")
                for line in f:
                        ip=line.strip()
                        ip_24=".".join(ip.split(".")[0:3])+".0"
                        spam_ips[date].add(ip)
                        if ip_24 not in spam_ips_24[date]:
                                spam_ips_24[date][ip_24]=set()
                        spam_ips_24[date][ip_24].add(ip)
                f.close()
        mismanaged={}
        f=open("../../google_blacklist_lib/blacklist_support_files/mismanaged_networks","r")
        for line in f:
                ip_24=line.strip().split(",")[0]
                score=float(line.strip().split(",")[1])
                mismanaged[ip_24]=score
        f.close()
        results={}
        #Should be marked as everything
        print
        file_list=glob.glob(original_file+"/*")
        print file_list
        done_spam_ips={}
        done_ham_ips={}
        check_spam=set()
        for file in file_list:
                print file
                f=open(file,"r")
                date=file.split("/")[-1]
                date=date.split("_")[0]
                if date not in spam_ips_24 or date not in spam_ips:
                        continue
                done_count=0
                if date not in results:
                        results[date]={}
                mark_flag=False
                for line in f:
                        type=line.strip().split(",")[0]
                        if type!="hf":
                                continue
                        ip=line.strip().split(",")[1]
                        score=float(line.strip().split(",")[-1])
                        ip_24=".".join(ip.split(".")[0:3])+".0"
                        stu=0
                        fdu=0
                        if type not in results[date]:
                                results[date][type]={}
                        mismanaged_score=0
                        threshold=0
                        e_score=0
                        try:
                                e_tp=expansion_score[ip_24][date]["TP"]
                        except:
                                e_tp=0
                        try:
                                e_fp=expansion_score[ip_24][date]["FP"]
                        except:
                                e_fp=0
                        if e_tp==0 and e_fp==0:
                                e_score=0
                        else:
                                e_score=e_fp/float(e_tp+e_fp)
                        e_score=1-e_score
                        e_threshold=0.1
                        if ip_24 in spatio_temporal or ip_24 in filling_degree:
                                stu=spatio_temporal[ip_24]
                                fd=filling_degree[ip_24]
                        if ip_24 in mismanaged:
                                mismanaged_score=mismanaged[ip_24]
                        for threshold in range(0,12):
                                if threshold!=7:
                                        continue
                                if threshold not in results[date][type]:
                                        results[date][type][threshold]={}
                                        results[date][type][threshold]["TP"]=set()
                                        results[date][type][threshold]["FP"]=set()
                                        results[date][type][threshold]["all_spam"]=len(spam_ips[date])
                                        results[date][type][threshold]["all_ham"]=len(ham_ips[date])
                                if score>=threshold:
                                        if ip in spam_ips[date]:
                                                results[date][type][threshold]["TP"].add(ip)
                                        if ip in ham_ips[date]:
                                                results[date][type][threshold]["FP"].add(ip)
                                        if e_score>=e_threshold:
                                                if fd>=0.8 or stu>=0.8 or mismanaged_score>=2:
                                                        if ip_24 in spam_ips_24[date]:
                                                                for ip_1 in spam_ips_24[date][ip_24]:
                                                                        results[date][type][threshold]["TP"].add(ip_1)
                                                        if ip_24 in ham_ips_24[date]:
                                                                for ip_1 in ham_ips_24[date][ip_24]:
                                                                        results[date][type][threshold]["FP"].add(ip_1)
                f.close()
        os.system("mkdir ../../blacklist_results_size")
        new_results={}
        #date type thrshold
        for date,type_data in results.iteritems():
                        for type,threshold_data in type_data.iteritems():
                                if type not in new_results:
                                        new_results[type]={}
                                for threshold,data in threshold_data.iteritems():
                                        if threshold not in new_results[type]:
                                                new_results[type][threshold]={}
                                                new_results[type][threshold]["TP"]=0
                                                new_results[type][threshold]["FP"]=0
                                                new_results[type][threshold]["all_spam"]=0
                                                new_results[type][threshold]["all_ham"]=0
                                        new_results[type][threshold]["FP"]=new_results[type][threshold]["FP"]+len(data["FP"])
                                        new_results[type][threshold]["TP"]=new_results[type][threshold]["TP"]+len(data["TP"])
                                        new_results[type][threshold]["all_spam"]=new_results[type][threshold]["all_spam"]+data["all_spam"]
                                        new_results[type][threshold]["all_ham"]=new_results[type][threshold]["all_ham"]+data["all_ham"]
                                        print threshold
                                        print date,type,"False positives",len(data["FP"]),data["all_ham"],"True Positives",len(data["TP"]),data["all_spam"]
                                        print date,type,"False positives",new_results[type][threshold]["FP"],new_results[type][threshold]["all_ham"],"True positives",new_results[type][threshold]["TP"],new_results[type][threshold]["all_spam"]
                                        print
        token=original_file.split("/")[-1].split("_")[1]
        fw=open("../../blacklist_results_size/mailinator_"+str(token),"w")
        for key,value in new_results.iteritems():
                fw.write(key+"qwerty123"+json.dumps(value)+"\n")
        fw.close()


def size_results():
	file_list=[1,2,5,10,30,60,90,120,150,195]
	print "F Specificity Recall"
	for file in file_list:
        	f=open("../../blacklist_results_size/mailinator_"+str(file),"r")
        	for line in f:
                	data=json.loads(line.strip().split("qwerty123")[1])["7"]
			fp=data["FP"]
			tp=data["TP"]
			all_ham=data["all_ham"]
			all_spam=data["all_spam"]
			recall=str(tp/float(all_spam))
                        specificity=str((all_ham-fp)/float(all_ham))
			print file,specificity,recall
        	f.close()

###Generate expanded and not expanded with results for varying blag threshold###
def generate_threshold_tp(dataset):
	all_dates=[]
        if dataset=="darknet":
                dataset_file_list=glob.glob("/home/krutikahmanawat/google_blacklist_lib/relevant_data/split_darknet/*")
        if dataset=="mirai":
                dataset_file_list=glob.glob("/home/krutikahmanawat/google_blacklist_lib/relevant_data/"+dataset+"_ip_data/2016-09-*")
        if dataset=="mailinator":
                dataset_file_list=glob.glob("/home/krutikahmanawat/google_blacklist_lib/relevant_data/"+dataset+"_ip_data/*")
        for file in dataset_file_list:
                date=file.split("/")[-1]
		all_dates.append(date)
	all_dates=sorted(all_dates)	

	threshold=0.7
        file_list=glob.glob("/home/krutikahmanawat/all_results/"+dataset+"/results_"+dataset+"/*")
        for date in all_dates:
                if dataset!="darknet":
                        file_list=file_list+glob.glob(date+"_whitelist")
	#ip_24,date,TP
	results={}
	done_count=0
	for file in file_list:
		date=file.split("/")[-1].split("_")[0]
		f=open(file,"r")
		for line in f:
                        type=line.strip().split(",")[0]
			if type!="hf":
				continue
                        ip=line.strip().split(",")[1]
                        score=float(line.strip().split(",")[-1])
			if score>=threshold:
				ip_24=".".join(ip.split(".")[0:3])+".0"
				if ip_24 not in results:
					results[ip_24]={}
				if date not in results[ip_24]:
					results[ip_24][date]={}
					results[ip_24][date]=set()
				results[ip_24][date].add(ip)
		f.close()
		done_count=done_count+1
		print done_count,len(file_list)
	fw=open("fp_tp/"+dataset+"_threshold_tp","w")
	final_results={}
	for ip_24,date_data in results.iteritems():
		final_results[ip_24]={}
		for date,ips in date_data.iteritems():
			final_results[ip_24][date]=len(ips)
	
	for ip_24,data in final_results.iteritems():
		fw.write(ip_24+"qwerty123"+json.dumps(data)+"\n")
	fw.close()
#generate_threshold_tp(dataset)
#plsmark
#blag_threshold,escore_threshold,e_score_threhold_flag,allowed_types
def analyse_fp_tp(dataset,allowed_types,write_false_positives,blag_threshold_start,blag_threshold_end,e_score_threshold_start,e_score_threshold_end,e_score_flag,test_flag,blacklist_contribution_flag,write_results_flag):
        testing_dates={}
        testing_dates["mailinator"]=["2016-05-19","2016-05-20","2016-05-21","2016-05-22","2016-05-23","2016-06-01","2016-06-02"]
        testing_dates["mirai"]=["2016-09-01","2016-09-02","2016-09-03","2016-09-04","2016-09-05","2016-09-06","2016-09-07"]
        testing_dates["darknet"]=["2017-01-30","2017-01-31","2017-02-01","2017-02-02","2017-02-03","2017-02-04","2017-02-05"]

	#Getting all dates for datasets
	all_dates=[]
        if dataset=="darknet":
                dataset_file_list=glob.glob("/home/krutikahmanawat/google_blacklist_lib/relevant_data/split_darknet/*")
        if dataset=="mirai":
                dataset_file_list=glob.glob("/home/krutikahmanawat/google_blacklist_lib/relevant_data/"+dataset+"_ip_data/2016-09-*")
        if dataset=="mailinator":
                dataset_file_list=glob.glob("/home/krutikahmanawat/google_blacklist_lib/relevant_data/"+dataset+"_ip_data/*")
        for file in dataset_file_list:
                date=file.split("/")[-1]
		if date in testing_dates[dataset]:
			continue
		all_dates.append(date)
	all_dates=sorted(all_dates)	

	#Reads expansion score | The cost for expanding based on previous datsets
	expansion_score={}
	#Higher accuracy score means more false positives
	f=open("accuracy_scores/"+dataset,"r")
	for line in f:
		ip_24=line.strip().split(",")[0]
		score=float(line.strip().split(",")[2])
		if ip_24 not in expansion_score:
			expansion_score[ip_24]=score		
			continue
		if score>expansion_score[ip_24]:
			expansion_score[ip_24]=score
	f.close()

	print "Done reading expansion scores"

	#Reading ham ips
        ham_ips={}
        ham_ips_24={}
        file_list=glob.glob("testing_data/"+dataset+"_testing_data/*")
        for file in file_list:
		if test_flag==True:
			break
                date=file.split("/")[-1]
		if date in testing_dates[dataset]:
			continue
                f=open(file,"r")
                for line in f:
                        ip=line.strip()
                        if date not in ham_ips:
                        	ham_ips[date]=set()
                        ham_ips[date].add(ip)
                        ip_24=".".join(ip.split(".")[0:3])+".0"
                        if date not in ham_ips_24:
                        	ham_ips_24[date]={}
                        if ip_24 not in ham_ips_24[date]:
                                ham_ips_24[date][ip_24]=set()
                        ham_ips_24[date][ip_24].add(ip)
                f.close()
        if dataset=="mailinator":
                f=open("/home/krutikahmanawat/google_blacklist_lib/blacklist_support_files/ham","r")
                for line in f:
			if test_flag==True:
				break
                        ip=line.strip().split(",")[0]
                        ip_24=".".join(ip.split(".")[0:3])+".0"
                        for date in all_dates:
                                ham_ips[date].add(ip)
                                if ip_24 not in ham_ips_24[date]:
                                        ham_ips_24[date][ip_24]=set()
                                ham_ips_24[date][ip_24].add(ip)
                f.close()

	#Reading spam
        spam_ips_24={}
        spam_ips={}
        total_spam=0
        if dataset=="darknet":
                dataset_file_list=glob.glob("/home/krutikahmanawat/google_blacklist_lib/relevant_data/split_darknet/*")
        if dataset=="mirai":
                dataset_file_list=glob.glob("/home/krutikahmanawat/google_blacklist_lib/relevant_data/"+dataset+"_ip_data/2016-09-*")
        if dataset=="mailinator":
                dataset_file_list=glob.glob("/home/krutikahmanawat/google_blacklist_lib/relevant_data/"+dataset+"_ip_data/*")
        for file in dataset_file_list:			
		if test_flag==True:
			break
                date=file.split("/")[-1]
		if date in testing_dates[dataset]:
			continue
                if date not in spam_ips:
                        spam_ips_24[date]={}
                        spam_ips[date]=set()
                f=open(file,"r")
                for line in f:
                        ip=line.strip()
                        ip_24=".".join(ip.split(".")[0:3])+".0"
                        spam_ips[date].add(ip)
                        if ip_24 not in spam_ips_24[date]:
                                spam_ips_24[date][ip_24]=set()
                        spam_ips_24[date][ip_24].add(ip)
                f.close()
	print "Done reading ham and spam"
	

	all_spam=0
        for date,ips in spam_ips.iteritems():
                all_spam=all_spam+len(ips)
	all_ham=0
	for date,ips in ham_ips.iteritems():
		all_ham=all_ham+len(ips)


	print "Ham",all_ham,"Spam",all_spam
        mismanaged={}
        f=open("/home/krutikahmanawat/google_blacklist_lib/blacklist_support_files/mismanaged_networks","r")
        for line in f:
		if test_flag==True:
			break
                ip_24=line.strip().split(",")[0]
                score=float(line.strip().split(",")[1])
                mismanaged[ip_24]=score
        f.close()

        spatio_temporal={}
        filling_degree={}
        f=open("/home/krutikahmanawat/google_blacklist_lib/blacklist_support_files/fd_stu_all","r")
        for line in f:
		if test_flag==True:
			break
                ip_24=line.strip().split(",")[0]
                fd=float(line.strip().split(",")[1])
                stu=float(line.strip().split(",")[2])
                spatio_temporal[ip_24]=stu
                filling_degree[ip_24]=fd
        f.close()
	print "Done reading fd,su,ms"
	results_plus={}
	results={}
	done_count=0
	
	#Reading results including whitelist results
	#file_list=glob.glob("/home/krutikahmanawat/all_results/"+dataset+"/results_"+dataset+"/*")
	file_list=glob.glob("/home/krutikahmanawat/new_results_"+dataset+"/*")
	#for date in all_dates:
	#	if dataset!="darknet":
	#		file_list=file_list+glob.glob(date+"_whitelist")

	
	print "Total files",len(file_list)
	blag_threshold=7
	e_results={}
	file_count=0
	for file in file_list:
		start_time=time.time()
		date=file.split("/")[-1].split("_")[0]
		if date in testing_dates[dataset]:
			continue
		start_time=time.time()
		f=open(file,"r")
		count=0
		for line in f:
			type=line.strip().split(",")[0]
			#plsmark
			if type not in allowed_types:
				continue	
			if type not in results:
				results[type]={}
			if date not in results[type]:
				results[type][date]={}
			ip=line.strip().split(",")[1]
			score=float(line.strip().split(",")[-1])
			ip_24=".".join(ip.split(".")[0:3])+".0"
			spam_flag=False
			ham_flag=False
			try:
				a=spam_ips_24[date][ip_24]
				spam_flag=True
			except:
				spam_flag=False
			try:
				a=ham_ips_24[date][ip_24]
				ham_flag=True
			except:
				ham_flag=False
			if spam_flag==False and ham_flag==False:
				continue
			for blag_threshold in range(blag_threshold_start,blag_threshold_end):
				if blag_threshold not in results[type][date]:
					results[type][date][blag_threshold]={}
					results[type][date][blag_threshold]["expanded"]={}
					results[type][date][blag_threshold]["not_expanded"]={}
					results[type][date][blag_threshold]["expanded"]["TP"]=set()
					results[type][date][blag_threshold]["expanded"]["FP"]=set()
					results[type][date][blag_threshold]["not_expanded"]["TP"]=set()
					results[type][date][blag_threshold]["not_expanded"]["FP"]=set()
				if score>=blag_threshold:
					ms=0
					fd=0
					stu=0
					try:
						ms=mismanaged[ip_24]
					except:
						ms=0
					try:
						stu=spatio_temporal[ip_24]
					except:
						stu=0
					try:
						fd=filling_degree[ip_24]		
					except:
						fd=0

					if ip in spam_ips[date]:
						results[type][date][blag_threshold]["expanded"]["TP"].add(ip)
						results[type][date][blag_threshold]["not_expanded"]["TP"].add(ip)
					if ip in ham_ips[date]:
						results[type][date][blag_threshold]["expanded"]["FP"].add(ip)
						results[type][date][blag_threshold]["not_expanded"]["FP"].add(ip)
					try:
						e_score=expansion_score[ip_24]
					except:
						e_score=0

					e_score=1-e_score			
					e_threshold=0.9
					if e_score>=e_threshold:
						if fd>=0.8 or stu>=0.8 or ms>=2:
							#if ip_24 in spam_ips_24[date]:
							try:
								for ip_1 in spam_ips_24[date][ip_24]:	
									results[type][date][blag_threshold]["expanded"]["TP"].add(ip_1)
							except:
								a=1
							#if ip_24 in ham_ips_24[date]:
							try:
								for ip_1 in ham_ips_24[date][ip_24]:	
									results[type][date][blag_threshold]["expanded"]["FP"].add(ip_1)
							except:
								a=1
					#Getting new stratergy results
					if type=="hf" and e_score_flag==True:
						if blag_threshold not in e_results:
							e_results[blag_threshold]={}
						for e_threshold in range(e_score_threshold_start,e_score_threshold_end):
							e_threshold=e_threshold/10.0
							if e_threshold not in e_results[blag_threshold]:
								e_results[blag_threshold][e_threshold]={}
							if date not in e_results[blag_threshold][e_threshold]:
								e_results[blag_threshold][e_threshold][date]={}
								e_results[blag_threshold][e_threshold][date]["TP"]=set()
								e_results[blag_threshold][e_threshold][date]["FP"]=set()
							if ip in spam_ips[date]:
								e_results[blag_threshold][e_threshold][date]["TP"].add(ip)
							if ip in ham_ips[date]:
								e_results[blag_threshold][e_threshold][date]["FP"].add(ip)
							if e_score>=e_threshold:
								if fd>=0.8 or stu>=0.8 or ms>=2:
									#if ip_24 in spam_ips_24[date]:
									try:
										for ip_1 in spam_ips_24[date][ip_24]:	
											e_results[blag_threshold][e_threshold][date]["TP"].add(ip_1)
									except:
										a=1
									#if ip_24 in ham_ips_24[date]:
									try:
										for ip_1 in ham_ips_24[date][ip_24]:	
											e_results[blag_threshold][e_threshold][date]["FP"].add(ip_1)
									except:
										a=1


	
		f.close()
		file_count=file_count+1
		print file,file_count,len(file_list),time.time()-start_time
		#plsmark
	#results[type][date][blag_threshold]["expanded"]["FP"]
	
	if write_false_positives==True and "hf" in allowed_types:
		fw_expansion=open("top_10_fp/false_positives_expansion_"+dataset,"w")
		fw_no_expansion=open("top_10_fp/false_positives_no_expansion_"+dataset,"w")
		for date,threshold_data in results["hf"].iteritems():
			for blag_threshold,data in threshold_data.iteritems():
				if int(blag_threshold)!=7:
					continue
				for ip in data["expanded"]["FP"]:
					fw_expansion.write(ip+","+date+"\n")
				for ip in data["not_expanded"]["FP"]:
					fw_no_expansion.write(ip+","+date+"\n")
		fw_expansion.close()
		fw_no_expansion.close()
	
	if blacklist_contribution_flag==True:
		#results[type][date][blag_threshold]["expanded"]["FP"]
		for date,threshold_data in results["hf"].iteritems():
			fw_expanded=open("blacklist_contribution/"+dataset+"/"+date+"_expanded","w")
			fw_not_expanded=open("blacklist_contribution/"+dataset+"/"+date+"_not_expanded","w")
			for blag_threshold,data in threshold_data.iteritems():
				if int(blag_threshold)!=7:
					continue
				for ip in data["expanded"]["FP"]:
					fw_expanded.write(ip+",FP\n")
				for ip in data["not_expanded"]["FP"]:
					fw_not_expanded.write(ip+",FP\n")
				for ip in data["expanded"]["TP"]:
					fw_expanded.write(ip+",TP\n")
				for ip in data["not_expanded"]["TP"]:
					fw_not_expanded.write(ip+",TP\n")
			fw_expanded.close()
			fw_not_expanded.close()
	all_results={}
	print len(results)
	for type,date_data in results.iteritems():
		all_results[type]={}
		for date,threshold_data in date_data.iteritems():
			for threshold,data in threshold_data.iteritems():
				if threshold not in all_results[type]:
					all_results[type][threshold]={}
					all_results[type][threshold]["expanded"]={}
					all_results[type][threshold]["not_expanded"]={}
					all_results[type][threshold]["expanded"]["TP"]=0
					all_results[type][threshold]["not_expanded"]["TP"]=0
					all_results[type][threshold]["expanded"]["FP"]=0
					all_results[type][threshold]["not_expanded"]["FP"]=0
				all_results[type][threshold]["expanded"]["TP"]=all_results[type][threshold]["expanded"]["TP"]+len(data["expanded"]["TP"])
				all_results[type][threshold]["not_expanded"]["TP"]=all_results[type][threshold]["not_expanded"]["TP"]+len(data["not_expanded"]["TP"])
				all_results[type][threshold]["expanded"]["FP"]=all_results[type][threshold]["expanded"]["FP"]+len(data["expanded"]["FP"])
				all_results[type][threshold]["not_expanded"]["FP"]=all_results[type][threshold]["not_expanded"]["FP"]+len(data["not_expanded"]["FP"])

	spam=0
	ham=0
	allowed_types_string="_".join(allowed_types)
	if write_results_flag==True:
		fw=open("final_results/"+dataset+"/all_results","w")		
		for type,type_results in all_results.iteritems():
			fw.write(type+"qwerty123"+json.dumps(type_results)+"\n")
		fw.close()

	
		if e_score_flag==True:
			e_all_results={}
			for blag_threshold,threshold_data in e_results.iteritems():
				e_all_results[blag_threshold]={}
				for threshold,date_data in threshold_data.iteritems():
					if threshold not in e_all_results[blag_threshold]:
						e_all_results[blag_threshold][threshold]={}
						e_all_results[blag_threshold][threshold]["TP"]=0
						e_all_results[blag_threshold][threshold]["FP"]=0
					for date,data in date_data.iteritems():
						e_all_results[blag_threshold][threshold]["TP"]=e_all_results[blag_threshold][threshold]["TP"]+len(data["TP"])
						e_all_results[blag_threshold][threshold]["FP"]=e_all_results[blag_threshold][threshold]["FP"]+len(data["FP"])

			fw=open("final_results/"+dataset+"/e_all_results","w")		
			for blag_threshold,data in e_all_results.iteritems():
				fw.write(str(blag_threshold)+"qwerty123"+json.dumps(data)+"\n")
			fw.close()


def analyse_ms(dataset):
	#Getting all dates for datasets
	all_dates=[]
        if dataset=="darknet":
                dataset_file_list=glob.glob("/home/krutikahmanawat/google_blacklist_lib/relevant_data/split_darknet/*")
        if dataset=="mirai":
                dataset_file_list=glob.glob("/home/krutikahmanawat/google_blacklist_lib/relevant_data/"+dataset+"_ip_data/2016-09-*")
        if dataset=="mailinator":
                dataset_file_list=glob.glob("/home/krutikahmanawat/google_blacklist_lib/relevant_data/"+dataset+"_ip_data/*")
        for file in dataset_file_list:
                date=file.split("/")[-1]
		all_dates.append(date)
	all_dates=sorted(all_dates)	

	#Reads expansion score | The cost for expanding based on previous datsets
	expansion_score={}
	f=open("fp_tp/"+dataset,"r")
	for line in f:
		reported_dates=[]
		ip_24=line.strip().split("qwerty123")[0]
		data=json.loads(line.strip().split("qwerty123")[1])
		tp=0
		fp=0	
		all=0
		expansion_score[ip_24]={}
		for date in all_dates:
			if date in data:
				tp=tp+data[date]["TP"]
				fp=fp+data[date]["FP"]
				#all=all+data[date]["all"]
			#FPTP=1-(# of FP/(# of TP+# of FP))
			expansion_score[ip_24][date]={}
			expansion_score[ip_24][date]["TP"]=tp
			expansion_score[ip_24][date]["FP"]=fp
			expansion_score[ip_24][date]["threshold_TP"]=0
			#expansion_score[ip_24][date]["all"]=all
	f.close()
	#This is the predicted values obtained from alpha in BLAG
	f=open("fp_tp/"+dataset+"_threshold_tp","r")	
	for line in f:
		ip_24=line.strip().split("qwerty123")[0]
		data=json.loads(line.strip().split("qwerty123")[1])
		threshold_tp=0
		for date in all_dates:
			if date in data:
				threshold_tp=threshold_tp+data[date]
			if ip_24 not in expansion_score:
				expansion_score[ip_24]={}
			if date not in expansion_score[ip_24]:
				expansion_score[ip_24][date]={}
				expansion_score[ip_24][date]["TP"]=0
				expansion_score[ip_24][date]["FP"]=0
				expansion_score[ip_24][date]["threshold_TP"]=0
			expansion_score[ip_24][date]["threshold_TP"]=threshold_tp
	f.close()		
	print "Done reading expansion scores"

	#Reading ham ips
        ham_ips={}
        ham_ips_24={}
        file_list=glob.glob("/home/krutikahmanawat/google_blacklist_lib/testing_data/"+dataset+"_testing_data/*")
        for file in file_list:
                date=file.split("/")[-1]
                f=open(file,"r")
                for line in f:
                        ip=line.strip()
                        if date not in ham_ips:
                        	ham_ips[date]=set()
                        ham_ips[date].add(ip)
                        ip_24=".".join(ip.split(".")[0:3])+".0"
                        if date not in ham_ips_24:
                        	ham_ips_24[date]={}
                        if ip_24 not in ham_ips_24[date]:
                                ham_ips_24[date][ip_24]=set()
                        ham_ips_24[date][ip_24].add(ip)
                f.close()
        if dataset=="mailinator":
                f=open("/home/krutikahmanawat/google_blacklist_lib/blacklist_support_files/ham","r")
                for line in f:
                        ip=line.strip().split(",")[0]
                        ip_24=".".join(ip.split(".")[0:3])+".0"
                        for date in all_dates:
                                ham_ips[date].add(ip)
                                if ip_24 not in ham_ips_24[date]:
                                        ham_ips_24[date][ip_24]=set()
                                ham_ips_24[date][ip_24].add(ip)
                f.close()

	#Reading spam
        spam_ips_24={}
        spam_ips={}
        total_spam=0
        if dataset=="darknet":
                dataset_file_list=glob.glob("/home/krutikahmanawat/google_blacklist_lib/relevant_data/split_darknet/*")
        if dataset=="mirai":
                dataset_file_list=glob.glob("/home/krutikahmanawat/google_blacklist_lib/relevant_data/"+dataset+"_ip_data/2016-09-*")
        if dataset=="mailinator":
                dataset_file_list=glob.glob("/home/krutikahmanawat/google_blacklist_lib/relevant_data/"+dataset+"_ip_data/*")
        for file in dataset_file_list:			
                date=file.split("/")[-1]
                if date not in spam_ips:
                        spam_ips_24[date]={}
                        spam_ips[date]=set()
                f=open(file,"r")
                for line in f:
                        ip=line.strip()
                        ip_24=".".join(ip.split(".")[0:3])+".0"
                        spam_ips[date].add(ip)
                        if ip_24 not in spam_ips_24[date]:
                                spam_ips_24[date][ip_24]=set()
                        spam_ips_24[date][ip_24].add(ip)
                f.close()
	print "Done reading ham and spam"
	

	all_spam=0
        for date,ips in spam_ips.iteritems():
                all_spam=all_spam+len(ips)
	all_ham=0
	for date,ips in ham_ips.iteritems():
		all_ham=all_ham+len(ips)


	print "Ham",all_ham,"Spam",all_spam
	
        mismanaged={}
        f=open("/home/krutikahmanawat/google_blacklist_lib/blacklist_support_files/mismanaged_networks","r")
        for line in f:
                ip_24=line.strip().split(",")[0]
                score=float(line.strip().split(",")[1])
                mismanaged[ip_24]=score
        f.close()

        spatio_temporal={}
        filling_degree={}
        f=open("/home/krutikahmanawat/google_blacklist_lib/blacklist_support_files/fd_stu_all","r")
        for line in f:
                ip_24=line.strip().split(",")[0]
                fd=float(line.strip().split(",")[1])
                stu=float(line.strip().split(",")[2])
                spatio_temporal[ip_24]=stu
                filling_degree[ip_24]=fd
        f.close()
	print "Done reading fd,su,ms"
	results_plus={}
	results={}
	done_count=0
	
	#Reading results including whitelist results
	file_list=glob.glob("/home/krutikahmanawat/all_results/"+dataset+"/results_"+dataset+"/*")
	for date in all_dates:
		if dataset!="darknet":
			file_list=file_list+glob.glob(date+"_whitelist")

	
	print "Total files",len(file_list)
	blag_threshold=7
	e_results={}
	file_count=0
	for file in file_list:
		start_time=time.time()
		date=file.split("/")[-1].split("_")[0]
		start_time=time.time()
		f=open(file,"r")
		count=0
		for line in f:
			type=line.strip().split(",")[0]
			#plsmark
			if type !="hf":
				continue	
			if date not in results:
				results[date]={}
				
			ip=line.strip().split(",")[1]
			score=float(line.strip().split(",")[-1])
			ip_24=".".join(ip.split(".")[0:3])+".0"
			spam_flag=False
			ham_flag=False
			try:
				a=spam_ips_24[date][ip_24]
				spam_flag=True
			except:
				spam_flag=False
			try:
				a=ham_ips_24[date][ip_24]
				ham_flag=True
			except:
				ham_flag=False
			if spam_flag==False and ham_flag==False:
				continue
			blag_threshold=7
			if score>=blag_threshold:
				ms=0
				fd=0
				stu=0
				try:
					ms=mismanaged[ip_24]
				except:
					ms=0
				try:
					stu=spatio_temporal[ip_24]
				except:
					stu=0
				try:
					fd=filling_degree[ip_24]		
				except:
					fd=0
				
				e_score=0
				try:
					e_tp=expansion_score[ip_24][date]["threshold_TP"]
				except:
					e_tp=0
				try:
					e_fp=expansion_score[ip_24][date]["FP"]
				except:
					e_fp=0
				if e_tp==0 and e_fp==0:
					e_score=0
				else:
					e_score=e_fp/float(e_tp+e_fp)
				e_score=1-e_score			
				e_threshold=0.9
				for ms_threshold in range(0,257):
					if ms_threshold!=0:
						continue
					if ms_threshold not in results[date]:
						results[date][ms_threshold]={}
						results[date][ms_threshold]["TP"]=set()
						results[date][ms_threshold]["FP"]=set()
					if ip in spam_ips[date]:
						results[date][ms_threshold]["TP"].add(ip)
					if ip in ham_ips[date]:
						results[date][ms_threshold]["FP"].add(ip)

					if e_score>=e_threshold:
						if ms_threshold not in results[date]:
							results[date][ms_threshold]={}
							results[date][ms_threshold]["TP"]=set()
							results[date][ms_threshold]["FP"]=set()
						if fd>=0.8 or stu>=0.8 or ms>=ms_threshold:
							try:
								for ip_1 in spam_ips_24[date][ip_24]:	
									results[date][ms_threshold]["TP"].add(ip_1)
							except:
								a=1
							try:
								for ip_1 in ham_ips_24[date][ip_24]:	
									results[date][ms_threshold]["FP"].add(ip_1)
							except:
								a=1
		f.close()
		file_count=file_count+1
		print file,file_count,len(file_list),time.time()-start_time
		#plsmark
	#results[type][date][blag_threshold]["expanded"]["FP"]
	

	all_results={}
	print len(results)
	for date,ms_data in results.iteritems():
		for ms,data in ms_data.iteritems():
			if ms not in all_results:
				all_results[ms]={}
				all_results[ms]["TP"]=0
				all_results[ms]["FP"]=0
			all_results[ms]["TP"]=all_results[ms]["TP"]+len(data["TP"])
			all_results[ms]["FP"]=all_results[ms]["FP"]+len(data["FP"])
		
	fw=open("final_results/final_results/"+dataset+"/ms_results_0","w")		
	for type,type_results in all_results.iteritems():
		fw.write(str(type)+"qwerty123"+json.dumps(type_results)+"\n")
		print type,type_results	
	fw.close()




def print_analysis(dataset):
	#Reading ham ips
	#Ham 4198605 Spam 39284
	all_spam={"mailinator":39284,"mirai":322053,"darknet":7509620}
	all_ham={"mailinator":4198605,"mirai":5441779,"darknet":3533270}
	#0qwerty123{"FP": 1658681, "TP": 33659} 0.7319684201630184 0.5985844107342925

	all_results={}
	f=open("final_results/"+dataset+"/all_results","r")
	for line in f:
		type=line.strip().split("qwerty123")[0]
		data=json.loads(line.strip().split("qwerty123")[1])
		all_results[type]=data
	f.close()
	results={}
	print "Expanded"
	for type,type_data in all_results.iteritems():
		if type not in results:
			results[type]={}
		for threshold,threshold_data in type_data.iteritems():
			threshold=int(threshold)
			if threshold not in results[type]:
				results[type][threshold]={}
			tp=threshold_data["expanded"]["TP"]
			fp=threshold_data["expanded"]["FP"]
			recall=tp/float(all_spam[dataset])
			specificity=(all_ham[dataset]-fp)/float(all_ham[dataset])
			results[type][threshold]["recall"]=recall
			results[type][threshold]["specificity"]=specificity
	types=["hf","h","f"]
	for i in range(0,10):
		try:
			print i,
			for type in types:
				
				if i==7:
					print colored(str(results[type][i]["specificity"])+" "+str(results[type][i]["recall"]),"red"),
				if i==0:
					print results[type][i]["specificity"],results[type][i]["recall"],"<---- Historical Expanded",
				else:
					print results[type][i]["specificity"],results[type][i]["recall"],
			print
		except:
			print
			continue
	print


	print "Not expanded"
	for type,type_data in all_results.iteritems():
		if type not in results:
			results[type]={}
		for threshold,threshold_data in type_data.iteritems():
			threshold=int(threshold)
			if threshold not in results[type]:
				results[type][threshold]={}
			tp=threshold_data["not_expanded"]["TP"]
			fp=threshold_data["not_expanded"]["FP"]
			recall=tp/float(all_spam[dataset])
			specificity=(all_ham[dataset]-fp)/float(all_ham[dataset])
			results[type][threshold]["recall"]=recall
			results[type][threshold]["specificity"]=specificity
	print "Historical Not expanded"
	types=["hf"]
	for i in range(0,8):
		try:	
			if i!=0 and i!=7:		
				continue
			print i,
			for type in types:
				if i==7:
					print colored(str(results[type][i]["specificity"])+" "+str(results[type][i]["recall"]),"red"),
				else:
					print results[type][i]["specificity"],results[type][i]["recall"],
			print
		except:
			continue
	print

	original_dataset=dataset
	datasets=["mailinator","mirai","darknet"]	
	datasets=["mailinator"]
	final_results={}
	for dataset in datasets:
		f=open("final_results/"+dataset+"/e_all_results","r")
		e_results={}
		for line in f:
			print line.strip()
			threshold=line.strip().split("qwerty123")[0]
			data=line.strip().split("qwerty123")[1]
			e_results[threshold]=json.loads(data)
		f.close()
		for i in range(0,8):
				if i!=0 and i!=7:
					continue
			#try:
				print "Threshold",i
				e_results_1=e_results[str(i)]
				e_results_1=sorted(e_results_1.items(),key=operator.itemgetter(0))
				for item in e_results_1:
					key=item[0]
					if key not in final_results:
						final_results[key]=[]
					value=item[1]
					tp=value["TP"]
					fp=value["FP"]
					recall=str(tp/float(all_spam[dataset]))
					specificity=str((all_ham[dataset]-fp)/float(all_ham[dataset]))
					if i==7 and key=="0.9":
						print colored(key+" "+specificity+" "+recall,"red")
						final_results[key].append(specificity)
						final_results[key].append(recall)
						
					else:
						print key,specificity,recall
						final_results[key].append(specificity)
						final_results[key].append(recall)

				print
			#except:
			#	continue
	final_results=sorted(final_results.items(),key=operator.itemgetter(0))
	for y in final_results:
		i=y[0]
		data=y[1]
		print i,
		for item in data:
			print item,
		print

	print 
	return
	dataset=original_dataset
	fw=open("final_results/"+dataset+"/ms_results_recall","w")
	f=open("final_results/"+dataset+"/ms_results","r")
	for line in f:
		threshold=line.strip().split("qwerty123")[0]
		data=json.loads(line.strip().split("qwerty123")[1])
		tp=data["TP"]
		fp=data["FP"]
		recall=tp/float(all_spam[dataset])
		specificity=(all_ham[dataset]-fp)/float(all_ham[dataset])
		print threshold,recall,specificity
		fw.write(str(threshold)+" "+str(recall)+" "+str(specificity)+"\n")
	fw.close()
	f.close()

def parser(date_string):
                month_array=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
                month_dict=[31,28,31,30,31,30,31,31,30,31,30,31]
                date_string=" ".join(date_string.split()).replace("UTC","")
                date_string=date_string.strip().split()
                year=int(date_string[-1])
                month=date_string[1]
                date=int(date_string[2])
                year_sum=(year-1)*365
                month_sub_array=month_dict[0:month_array.index(month)]
                month_sum=sum(month_sub_array)
                #print date_string,month_sum,year_sum,date
                date_sum=date
                sum_1=year_sum+month_sum+date_sum
                return sum_1

def convert_date(date):
        month_dict=[31,28,31,30,31,30,31,31,30,31,30,31]
        year_sum=(int(date.split("-")[0])-1)*365
        month_sub_array=month_dict[0:int(date.split("-")[1])-1]
        month_sum=sum(month_sub_array)
        date_sum=int(date.split("-")[-1])
        return year_sum+month_sum+date_sum

def list_blacklist(dataset):
	active_16=set()
        f=open("../../google_blacklist_lib/blacklist_support_files/active_16","r")
        for line in f:
                active_16.add(line.strip())
        f.close()
	file_list=glob.glob("blacklist_contribution/"+dataset+"/*")
	results={}
	all_16=set()

	ip_dates={}
	print "Total files",len(file_list)
	for file in file_list:
		date=file.split("/")[-1].split("_")[0]
		f=open(file,"r")
		if "expanded" in file:
			type="expanded"
		if "not_expanded" in file:
			type="not_expanded"
		for line in f:
			ip=line.strip().split(",")[0]
			if ip not in ip_dates:
				ip_dates[ip]=set()
			ip_dates[ip].add(date)
			ip_16=".".join(ip.split(".")[0:2])+".0.0"
			ip_type=line.strip().split(",")[1]
			all_16.add(ip_16)
			if ip_16 not in results:
				results[ip_16]={}
			if ip not in results[ip_16]:
				results[ip_16][ip]={}
			if type not in results[ip_16][ip]:
				results[ip_16][ip][type]=set()
			results[ip_16][ip][type].add(ip_type)
		f.close()
		print len(results)
	common=active_16.intersection(all_16)
	print "Common",len(common)
	bl_count_tp={}
	bl_count_fp={}
	done_count=0
	for ip_16 in common:
		done_count=done_count+1
		print done_count,len(common)
		f=open("../../Results6/"+ip_16,"r")
		for line in f:
			ip=line.strip().split("qwerty123")[0]
			try:
				check=results[ip_16][ip]
			except:
				continue
			data=json.loads(line.strip().split("qwerty123")[1])	
			for date in ip_dates[ip]:
				reference_end_time=convert_date(date)
				all_blacklists=set()
        	                for blacklist,blacklist_data in data["Blacklist"].iteritems():
                	                blacklist=blacklist.split(".")[0].strip()
					'''
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
                                        	continue
					'''
					all_blacklists.add(blacklist)
				
				for blacklist in all_blacklists:
					if blacklist not in bl_count_tp:
						bl_count_tp[blacklist]={}
						bl_count_tp[blacklist]["expanded"]=0
						bl_count_tp[blacklist]["not_expanded"]=0
					if blacklist not in bl_count_fp:
						bl_count_fp[blacklist]={}
						bl_count_fp[blacklist]["expanded"]=0
						bl_count_fp[blacklist]["not_expanded"]=0
					#results[ip_16][ip][type]
					for type,ip_types in results[ip_16][ip].iteritems():
						for ip_type in ip_types:
							if ip_type=="TP":
								bl_count_tp[blacklist][type]=bl_count_tp[blacklist][type]+1
							if ip_type=="FP":
								bl_count_fp[blacklist][type]=bl_count_fp[blacklist][type]+1
		f.close()
	all_blacklists=set()
	for blacklist,_ in bl_count_tp.iteritems():
		all_blacklists.add(blacklist)			
	fw=open("blacklist_contribution/"+dataset+"/contributions","w")
	for blacklist in all_blacklists:
		fw.write(blacklist+","+str(bl_count_tp[blacklist]["not_expanded"])+","+str(bl_count_fp[blacklist]["not_expanded"])+","+str(bl_count_tp[blacklist]["expanded"])+","+str(bl_count_fp[blacklist]["expanded"])+"\n")
	fw.close()
#list_blacklist(dataset)
#analyse_fp_tp(dataset,allowed_types,write_false_positives,blag_threshold_start,blag_threshold_end,e_score_threshold_start,e_score_threshold_end,e_score_flag,test_flag,blacklist_contribution_flag,write_results_flag):
analyse_fp_tp(dataset,["hf"],False,0,11,0,11,True,False,False,True)
print_analysis(dataset)			
#analyse_ms(dataset)
