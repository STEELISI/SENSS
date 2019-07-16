import sys
import json 
from selective_generate_prefix_data import generate_prefix_data 
from new_matrix import run_recommender 
from blacklist_support import parser,send_mail 
import multiprocessing 
import time 
import progressbar 
import glob 
import os

def convert_date(date):
	month_dict=[31,28,31,30,31,30,31,31,30,31,30,31]
	year_sum=(int(date.split("-")[0])-1)*365
	month_sub_array=month_dict[0:int(date.split("-")[1])-1]
	month_sum=sum(month_sub_array)
	date_sum=int(date.split("-")[-1])
	return year_sum+month_sum+date_sum

def listener(queue,date,type,dataset,to_avoid):
	f = open("../../new_results_"+dataset+"_"+to_avoid+"/"+date+"_"+type, 'w')
	#fbl=open("../../blacklists/"+dataset,"w")
	print "At Listener"
	while 1:
		return_value=queue.get()
		if return_value == "kill":
			print "Kill"
			break
		type=return_value[0]
		if type=="bl":
			ip=return_value[1]
			bl=return_value[2]
			#fbl.write(ip+","+bl+"\n")
			continue
		ip=return_value[2]
		total_steps=str(return_value[3])
		error=str(return_value[4])
		total_time=str(return_value[5])
		score=str(return_value[6])
		f.write(type+","+ip+","+total_steps+","+error+","+total_time+","+score+"\n")
		f.flush()
	f.flush()
	f.close()
	#fbl.flush()
	#fbl.close()

#damn i take the max of the scores
def run_process(ip_16,reference_end_time,date,queue,dataset,send_accuracy_scores,avoid_blacklists,to_avoid):
	#generate_prefix_data(current_prefix,reference_end_time,date,output_folder,dataset,accuracy_scores)
	hf_array,f_array,h_array,ip_blacklist_map=generate_prefix_data(ip_16,reference_end_time,date,"../../Results6",dataset,send_accuracy_scores,avoid_blacklists)
	to_do=[hf_array,f_array,h_array]
	for ip,blacklists in ip_blacklist_map.iteritems():
		#queue.put((type,date,ip_order[i],total_steps,error,total_time,max(list(item))))
		for blacklist in blacklists:
			queue.put(("bl",ip,blacklist))

	return_values=[]
	for item in to_do:
		matrix=[]
		ip_order=[]
		for data in item:
			ip_order.append(data[0])
			matrix.append(data[1])
			type=data[2]
		return_array=run_recommender(matrix)
		#step,error,end_time-start_time,nR
		for data in return_array:
			total_steps=data[0]
			if total_steps=="0":
					continue
			error=str(round(data[1],3))
			total_time=str(round(data[2],3))
			nR=data[3]
			i=0
			for item in nR:
				queue.put((type,date,ip_order[i],total_steps,error,total_time,max(list(item))))
				i=i+1
	return

def generate_pd(dataset,avoid_blacklists,to_avoid):
	os.system("mkdir ../../new_results_"+dataset+"_"+to_avoid)
	#os.system("mkdir ../../blacklists")
	active_16=set()
	f=open("blacklist_support_files/active_16","r")
	for line in f:
		active_16.add(line.strip())
	f.close()
	total=0

	#Run only for training data
	testing_dates={}
	testing_dates["mailinator"]=["2016-05-19","2016-05-20","2016-05-21","2016-05-22","2016-05-23","2016-06-01","2016-06-02"]
	testing_dates["mirai"]=["2016-09-01","2016-09-02","2016-09-03","2016-09-04","2016-09-05","2016-09-06","2016-09-07"]
	testing_dates["darknet"]=["2017-01-30","2017-01-31","2017-02-01","2017-02-02","2017-02-03","2017-02-04","2017-02-05"]
	#Change this
	file_list=glob.glob("testing_data/"+dataset+"_testing_data/*")+glob.glob("../../google_blacklist_lib/relevant_data/"+dataset+"_ip_data/*")
	#glob.glob("../../google_blacklist_lib/relevant_data/"+dataset+"_ip_data/*")
	temp1=set()
	for file in file_list:
		date=file.split("/")[-1]
		if date in testing_dates[dataset]:
			continue
		f=open(file,"r")
		temp=set()
		for line in f:
			ip=line.strip()
			ip_16=".".join(ip.split(".")[0:2])+".0.0"
			if ip_16 in active_16:
				temp.add(ip_16)
				temp1.add(ip_16)
		f.close()
		total=total+len(temp)

	bar = progressbar.ProgressBar(maxval=total,widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage(),' ',progressbar.Timer()])
	bar.start()
	done_count=0
	print "Total",total,len(temp1)
	print "All files",len(file_list)
	file_done_count=0
	for file in file_list:
		jobs=[]
		date=file.split("/")[-1]
		file_done_count=file_done_count+1
		print file_done_count,len(file_list)
		#Changed for generating training darknet data
		if date in testing_dates[dataset]:
			continue
		accuracy_scores={}
		f=open("accuracy_scores/"+dataset,"r")
		for line in f:
			ip_24=line.strip().split(",")[0]
			ip_16=".".join(ip_24.split(".")[0:2])+".0.0"
			bl=line.strip().split(",")[1]
			score=float(line.strip().split(",")[2])
			if ip_16 not in accuracy_scores:
				accuracy_scores[ip_16]={}
			if ip_24 not in accuracy_scores[ip_16]:
				accuracy_scores[ip_16][ip_24]={}
			accuracy_scores[ip_16][ip_24][bl]=score
		f.close()



		date_sum=convert_date(file.split("/")[-1])
		f=open(file,"r")
		ip_16_set=set()
		for line in f:
			ip=line.strip()
			ip_16=".".join(ip.split(".")[0:2])+".0.0"
			ip_16_set.add(ip_16)
		f.close()

		manager = multiprocessing.Manager()
		q = manager.Queue()
		pool = multiprocessing.Pool(multiprocessing.cpu_count() + 2)
		if "testing_data" in file:
			watcher = pool.apply_async(listener, (q,date,"whitelist",dataset,to_avoid,))
		else:
			watcher = pool.apply_async(listener, (q,date,"blacklist",dataset,to_avoid,))

		for ip_16 in ip_16_set:
			if ip_16 not in active_16:
				continue
			try:
				send_accuracy_scores=accuracy_scores[ip_16]
			except:
				send_accuracy_scores={}
			#(ip_16,reference_end_time,date,queue,dataset,send_accuracy_scores)
			job = pool.apply_async(run_process, (ip_16,date_sum,date,q,dataset,send_accuracy_scores,avoid_blacklists,to_avoid,))
			jobs.append(job)
		for job in jobs:
			job.get()
			done_count=done_count+1
			bar.update(done_count)
		q.put("kill")
		pool.close()
	bar.update(done_count)
	bar.finish()


f=open("mailinator_size_run/blacklists","r")
avoid_blacklists=[]
for line in f:
	data=line.strip().split(",")[0]
	if len(data)!=0:
		avoid_blacklists.append(line.strip().split(",")[0])
f.close()
total_length=len(avoid_blacklists)
start=0
end=int(0.5*0.1*total_length)
avoid_blacklists_set=set(avoid_blacklists[start:end])
print start,end,total_length,len(avoid_blacklists_set)
generate_pd("mailinator",avoid_blacklists_set,str(end))
for i in range(1,10):
	start=0
	end=int(i*0.1*total_length)
	avoid_blacklists_set=set(avoid_blacklists[start:end])
	print start,end,total_length,len(avoid_blacklists_set)
	generate_pd("mailinator",avoid_blacklists_set,str(end))

