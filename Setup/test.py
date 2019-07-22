import MySQLdb
import sys

password=sys.argv[1]

db=MySQLdb.connect(host="localhost",port=3306,user="root",passwd=password)
cur=db.cursor()
cur.execute("USE SENSS")
cur.execute("INSERT INTO SERVER_LOGS (as_name,request_type) VALUES ('%s','%s')" % ("USC","Add filter"))
cur.execute("INSERT INTO SERVER_LOGS (as_name,request_type) VALUES ('%s','%s')" % ("USC","Add filter"))
cur.execute("INSERT INTO SERVER_LOGS (as_name,request_type) VALUES ('%s','%s')" % ("USC","Add filter"))
cur.execute("INSERT INTO SERVER_LOGS (as_name,request_type) VALUES ('%s','%s')" % ("USC","Remove filter"))
cur.execute("INSERT INTO SERVER_LOGS (as_name,request_type) VALUES ('%s','%s')" % ("UCLA","Add filter"))
db.commit()
