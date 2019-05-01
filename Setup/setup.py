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
import sys
import getpass
import json
import subprocess
import time
import os

def init_database(db_password):
	cmd="sudo python ./init.py "+db_password
	os.system(cmd)

def add_client_entries(as_name,server_url,links_to,self,db_password):
	if links_to=="None":
		return
	cmd="sudo python ./insert_senss_client.py "+db_password+" "+as_name+" "+server_url+" "+links_to+" "+self
	os.system(cmd)

def copy_files(type,location):
	if type=="server":
		cmd="sudo cp -rf ../Server "+location
		os.system(cmd)
	if type=="client":
		cmd="sudo cp -rf ../Client "+location
		os.system(cmd)
		os.system("sudo chown -R www-data /var/www/html/Client/exps/cert")

def install_dependencies():
	cmd="sh ./install_dependencies.sh"
	os.system(cmd)
	print "Installed dependencies"

#Need to modify this to be supportive for multiple elements
def start_monitor_flows(multiply,legit_address):
	cmd="screen -d -m sudo python /var/www/html/SENSS/UI_client_server/Server/monitor_flows.py "+str(multiply)+" "+str(legit_address)
	os.system(cmd)
	print "Started Monitoring flows controller"

def print_data(data):
	for item in data:
		print item.strip()

def configure_nodes():
	type=raw_input("Setup for? (client or server): ")
	type=type.strip()

	location=raw_input("Enter location of web server: ")
	location=location.strip()


	db_password=getpass.getpass(prompt="Enter root password for mysql:")

	install_dependencies()
	init_database(db_password)
	print "Initialised DB"
	#location="/var/www/html/"
	copy_files(type,location)

	cmd="sudo service apache2 restart"
	os.system(cmd)

	if type=="client":
		print "Open SENSS client at Client/exps/client.php"
	if type=="server":
		print "Open SENSS server at Client/exps/server.php"
if __name__ == '__main__':
	configure_nodes()
