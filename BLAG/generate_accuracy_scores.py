import glob
datasets=["mailinator","mirai","darknet"]
for dataset in datasets:
	print dataset
	contributions={}
	#contributions_mailinator
	file_list=glob.glob("contributions/contributions_"+dataset+"/*")
	for file in file_list:
		date=file.split("/")[-1]
		f=open(file,"r")
		for line in f:
			ip_24=line.strip().split(",")[0]
			bl=line.strip().split(",")[1]
			count=int(line.strip().split(",")[2])
			if ip_24 not in contributions:
				contributions[ip_24]={}
			if bl not in contributions[ip_24]:
				contributions[ip_24][bl]=0
			contributions[ip_24][bl]=contributions[ip_24][bl]+count
		f.close()
	false_positives={}
	file_list=glob.glob("false_positives/"+dataset+"_false_positives/*")
	for file in file_list:
		date=file.split("/")[-1]
		f=open(file,"r")
		for line in f:
			ip_24=line.strip().split(",")[0]
			bl=line.strip().split(",")[1]
			count=int(line.strip().split(",")[2])
			if ip_24 not in false_positives:
				false_positives[ip_24]={}
			if bl not in false_positives[ip_24]:
				false_positives[ip_24][bl]=0
			false_positives[ip_24][bl]=false_positives[ip_24][bl]+count
		f.close()
	
	scores={}
	for ip_24,data in contributions.iteritems():
		for bl,count in data.iteritems():
			try:
				false_positives_count=false_positives[ip_24][bl]
			except:
				continue
			accuracy_score=false_positives_count/float(count)
			if ip_24 not in scores:
				scores[ip_24]={}
			scores[ip_24][bl]=accuracy_score

	fw=open("accuracy_scores/"+dataset,"w")
	for ip_24,bl_data in scores.iteritems():
		for bl,count in bl_data.iteritems():
			fw.write(ip_24+","+bl+","+str(count)+"\n")
	fw.close()

