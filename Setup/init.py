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

import MySQLdb
import sys

password=sys.argv[1]
interface=sys.argv[2]
type=sys.argv[3]

db=MySQLdb.connect(host="localhost",port=3306,user="root",passwd=password)
cur=db.cursor()

if type=="server":
	try:
		cur.execute("CREATE DATABASE SENSS")
		print "Database SENSS created"
	except:
		print "Database SENSS already exists"

	cur.execute("USE SENSS")

	try:
		cur.execute("CREATE TABLE `CLIENT_LOGS` (`id` bigint(20) NOT NULL AUTO_INCREMENT, `as_name` varchar(45) NOT NULL, `log_type` varchar(45) NOT NULL, `match_field` text, `packet_count` bigint(20) DEFAULT NULL, `byte_count` bigint(20) DEFAULT NULL, `speed` varchar(45) DEFAULT NULL, `flag` int(1) DEFAULT 0, `active` int(1) DEFAULT NULL, `frequency` int(11) DEFAULT 0, `end_time` int(15) DEFAULT 0,`threshold` int(15) DEFAULT 10, PRIMARY KEY (`id`))")
		print "Table CLIENT_LOGS created"
	except Exception as e:
		print e
		print "Table CLIENT_LOGS already exists"
		cur.execute("DROP TABLE CLIENT_LOGS")
		cur.execute("CREATE TABLE `CLIENT_LOGS` (`id` bigint(20) NOT NULL AUTO_INCREMENT, `as_name` varchar(45) NOT NULL, `log_type` varchar(45) NOT NULL, `match_field` text, `packet_count` bigint(20) DEFAULT NULL, `byte_count` bigint(20) DEFAULT NULL, `speed` varchar(45) DEFAULT NULL, `flag` int(1) DEFAULT 0, `active` int(1) DEFAULT NULL, `frequency` int(11) DEFAULT 0, `end_time` int(15) DEFAULT 0,`threshold` int(15) DEFAULT 10, PRIMARY KEY (`id`))")
		print "Table CLIENT_LOGS created"



	try:
		cur.execute("CREATE TABLE `SERVER_LOGS` (`id` bigint(20) NOT NULL AUTO_INCREMENT, `request_type` varchar(45) NOT NULL,`as_name` varchar(45) NOT NULL, `match_field` text, `packet_count` bigint(20) DEFAULT NULL, `end_time` int(15) DEFAULT 0,`byte_count` bigint(20) DEFAULT NULL,valid_request INT DEFAULT NULL,prefix_allowed varchar(45) DEFAULT NULL, speed varchar(25) DEFAULT NULL,PRIMARY KEY (`id`))")
		print "Table SERVER_LOGS created"
	except Exception as e:
		print e
		print "Table SERVER_LOGS already exists"
		cur.execute("DROP TABLE SERVER_LOGS")
		cur.execute("CREATE TABLE `SERVER_LOGS` (`id` bigint(20) NOT NULL AUTO_INCREMENT, `request_type` varchar(45) NOT NULL,`as_name` varchar(45) NOT NULL, `match_field` text, `packet_count` bigint(20) DEFAULT NULL, `end_time` int(15) DEFAULT 0,`byte_count` bigint(20) DEFAULT NULL,valid_request INT DEFAULT NULL,prefix_allowed varchar(45) DEFAULT NULL, speed varchar(25) DEFAULT NULL,PRIMARY KEY (`id`))")
		print "Table SERVER_LOGS created"


	try:
		cur.execute("CREATE TABLE `CONSTANTS` (`id` int(11) NOT NULL AUTO_INCREMENT, `as_name` varchar(45) NOT NULL, `controller_url` VARCHAR(250) NOT NULL, `rule_capcity` INT NOT NULL, PRIMARY KEY (`id`))")
		print "Table CONSTANTS created"
	except Exception as e:
		print e
		print "Table CONSTANTS already exists"
		cur.execute("DROP TABLE CONSTANTS")
		cur.execute("CREATE TABLE `CONSTANTS` (`id` int(11) NOT NULL AUTO_INCREMENT, `as_name` varchar(45) NOT NULL, `controller_url` VARCHAR(250) NOT NULL, `rule_capacity` INT NOT NULL, PRIMARY KEY (`id`))")
		print "Table CONSTANTS created"

	try:
		cur.execute("CREATE TABLE `THRESHOLDS` (`as_name` varchar(45) NOT NULL, `used_filter_requests` INT NOT NULL, `max_filter_requests` INT NOT NULL, `used_monitoring_requests` INT NOT NULL, `max_monitoring_requests` INT NOT NULL, `fair_sharing` INT NOT NULL,`block_monitoring` INT NOT NULL, `block_filtering` INT NOT NULL, PRIMARY KEY (`as_name`))")
		print "Table THRESHOLDS created"
	except:
		print "Table THRESHOLDS already exists"
		cur.execute("DROP TABLE THRESHOLDS")
		cur.execute("CREATE TABLE `THRESHOLDS` (`as_name` varchar(45) NOT NULL, `used_filter_requests` INT NOT NULL, `max_filter_requests` INT NOT NULL, `used_monitoring_requests` INT NOT NULL, `max_monitoring_requests` INT NOT NULL, `fair_sharing` INT NOT NULL,`block_monitoring` INT NOT NULL, `block_filtering` INT NOT NULL, PRIMARY KEY (`as_name`))")
		print "Table THRESHOLDS created"

	cur.close()
	cur=db.cursor()

if type=="client":
	try:
		cur.execute("CREATE DATABASE SENSS_CLIENT")
		print "Database SENSS_CLIENT created"
	except:
		print "Database SENSS_CLIENT already exists"

	cur.execute("USE SENSS_CLIENT")

	try:
		cur.execute("CREATE TABLE `AS_URLS` (`id` int(11) NOT NULL AUTO_INCREMENT, `as_name` varchar(45) NOT NULL, `server_url` varchar(255) NOT NULL, `links_to` text, `self` int(1) DEFAULT 0, PRIMARY KEY (`id`))")
		print "Table AS_URLS created"
	except Exception as e:
		print e
		print "Table AS_URLS already exists"
		cur.execute("DROP TABLE AS_URLS")
		cur.execute("CREATE TABLE `AS_URLS` (`id` int(11) NOT NULL AUTO_INCREMENT, `as_name` varchar(45) NOT NULL, `server_url` varchar(255) NOT NULL, `links_to` text, `self` int(1) DEFAULT 0, PRIMARY KEY (`id`))")
		print "Table AS_URLS created"


	try:
		cur.execute("CREATE TABLE `CLIENT_PROCESSES` (`id` int(11) NOT NULL AUTO_INCREMENT, `process_name` varchar(45) NOT NULL, `status` INT NOT NULL, `change_status` INT NOT NULL, `interface` varchar(45) NOT NULL, `pid` INT NOT NULL, PRIMARY KEY (`id`))")
		print "Table CLIENT_PROCESSES created"
	except Exception as e:
		print e
		print "Table CLIENT_PROCESSES already exists"
		cur.execute("DROP TABLE CLIENT_PROCESSES")
		cur.execute("CREATE TABLE `CLIENT_PROCESSES` (`id` int(11) NOT NULL AUTO_INCREMENT, `process_name` varchar(45) NOT NULL, `status` INT NOT NULL, `interface` VARCHAR(25) NOT NULL,`change_status` INT NOT NULL, `pid` INT NOT NULL, PRIMARY KEY (`id`))")
		print "Table CLIENT_PROCESSES created"


	if interface!="None":
		cmd="INSERT INTO `CLIENT_PROCESSES` (`id`, `process_name`,`status`,`change_status`,`interface`, `pid`) VALUES (%s,'%s',%d,%d,'%s',%d)" % (0,"AMON SENSS",0,0, interface, 0)
	else:
		cmd="INSERT INTO `CLIENT_PROCESSES` (`id`, `process_name`,`status`, `change_status`, `pid`) VALUES (%s,'%s',%d,%d)" % (0,"AMON SENSS",0,0,0)


	cur.execute(cmd)
	db.commit()

	try:
		cur.execute("CREATE TABLE `MONITORING_RULES` (`id` int(11) NOT NULL AUTO_INCREMENT, `as_name` varchar(45) NOT NULL, `match_field` text, `frequency` int(5) DEFAULT 0, `end_time` int(15) DEFAULT 0, `monitor_id` bigint(20) DEFAULT 0,`type` text,`message` text,  PRIMARY KEY (`id`))")
		print "Table MONITORING_RULES created"
	except Exception as e:
		print e
		print "Table MONITORING_RULES already exists"
		cur.execute("DROP TABLE MONITORING_RULES")
		cur.execute("CREATE TABLE `MONITORING_RULES` (`id` int(11) NOT NULL AUTO_INCREMENT, `as_name` varchar(45) NOT NULL, `match_field` text, `frequency` int(5) DEFAULT 0, `end_time` int(15) DEFAULT 0, `monitor_id` bigint(20) DEFAULT 0,`type` text,`message` text,  PRIMARY KEY (`id`))")
		print "Table MONITORING_RULES created"


	try:
		cur.execute("CREATE TABLE `AMON_SENSS` (`id` int(11) NOT NULL AUTO_INCREMENT, `as_name` varchar(45) NOT NULL, `match_field` text, `frequency` int(5) DEFAULT 0, `monitor_duration` int(15) DEFAULT 0,`type` text, PRIMARY KEY (`id`))")
		print "Table MONITORING_RULES created"
	except Exception as e:
		print e
		print "Table MONITORING_RULES already exists"
		cur.execute("DROP TABLE AMON_SENSS")
		cur.execute("CREATE TABLE `AMON_SENSS` (`id` int(11) NOT NULL AUTO_INCREMENT, `as_name` varchar(45) NOT NULL, `match_field` text, `frequency` int(5) DEFAULT 0, `monitor_duration` int(15) DEFAULT 0,`type` text, PRIMARY KEY (`id`))")
		print "Table MONITORING_RULES created"

	try:
		cur.execute("CREATE TABLE `CLIENT_LOGS` (`id` bigint(20) NOT NULL AUTO_INCREMENT, `request_type` varchar(45) NOT NULL,`as_name` varchar(45) NOT NULL, `match_field` text, `packet_count` bigint(20) DEFAULT NULL, `time` varchar(45) DEFAULT 0,`byte_count` bigint(20) DEFAULT NULL, speed varchar(2500) DEFAULT NULL,monitor_id int(5), PRIMARY KEY (`id`))")
		print "Table CLIENT_LOGS created"
	except Exception as e:
		print e
		print "Table CLIENT_LOGS already exists"
		cur.execute("DROP TABLE CLIENT_LOGS")
		cur.execute("CREATE TABLE `CLIENT_LOGS` (`id` bigint(20) NOT NULL AUTO_INCREMENT, `request_type` varchar(45) NOT NULL,`as_name` varchar(45) NOT NULL, `match_field` text, `packet_count` bigint(20) DEFAULT NULL, `time` varchar(45) DEFAULT 0,`byte_count` bigint(20) DEFAULT NULL, speed varchar(2500) DEFAULT NULL,monitor_id int(5), PRIMARY KEY (`id`))")
		print "Table CLIENT_LOGS created"
	try:
		cur.execute("CREATE DATABASE SENSS_PROXY")
		print "Database SENSS_PROXY created"
	except:
		print "Database SENSS_PROXY already exists"
	cur.execute("USE SENSS_PROXY")

	try:
		cur.execute("CREATE TABLE `NONCES` (`id` bigint(20) NOT NULL AUTO_INCREMENT, `ip` text NOT NULL, `nonce` text NOT NULL, PRIMARY KEY (`id`))")
		print "Table nonces created"
	except Exception as e:
		print e
		print "Table NONCES already exists"
		cur.execute("DROP TABLE NONCES")
		cur.execute("CREATE TABLE `NONCES` (`id` bigint(20) NOT NULL AUTO_INCREMENT, `ip` text NOT NULL, `nonce` text NOT NULL, PRIMARY KEY (`id`))")
		print "Table NONCES created"
