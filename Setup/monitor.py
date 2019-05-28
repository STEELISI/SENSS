import time
import os
import subprocess
import MySQLdb
import sys
password=sys.argv[1]
db=MySQLdb.connect(host="localhost",port=3306,user="root",passwd=password)
cur=db.cursor()

while True:
	db.commit()
	cur.execute("USE SENSS_CLIENT")
	cur.execute("SELECT * from CLIENT_PROCESSES")
	amon_pid=0
	for item in cur.fetchall():
		process_name=item[1]
		status=int(item[2])
		interface=item[3]
		change_status=int(item[4])
		pid=int(item[5])
		print ("Checking",status,change_status)
		if change_status!=status:
			#Kill the process
			if change_status==0:
				print "Killing process",pid
				os.system("kill -9 "+str(pid))
				os.system("kill -9 "+str(pid+1))
				os.system("kill -9 "+str(pid+2))
				os.system("kill -9 "+str(pid+3))
				os.system("kill -9 "+str(pid+4))
				cur.execute("UPDATE CLIENT_PROCESSES SET pid=%d,status=%d WHERE process_name='%s'" % (amon_pid, change_status, process_name))
				db.commit()
			#Start the process
			if change_status==1:
				proc = subprocess.Popen(['sudo as -r '+interface], shell=True)
				amon_pid=proc.pid
				cur.execute("UPDATE CLIENT_PROCESSES SET pid=%d,status=%d WHERE process_name='%s'" % (amon_pid, change_status, process_name))
				db.commit()
				print "Starting process",amon_pid
	time.sleep(5)
