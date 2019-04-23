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

def init_database(nodes,db_password):
	cmd="sudo python ./init.py "+db_password
	os.system(cmd)

def add_client_entries(as_name,server_url,links_to,self,db_password):
	if links_to=="None":
		return
	cmd="sudo python ./insert_senss_client.py "+db_password+" "+as_name+" "+server_url+" "+links_to+" "+self
	os.system(cmd)

def copy_files():
	cmd="sudo cp -rf ../Server /var/www/html/"
	os.system(cmd)

	cmd="sudo cp -rf ../Client /var/www/html/"
	os.system(cmd)

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

def copy_certificates(server_flag,node):
	print "Copying certificates"
	if server_flag==True:
	    	cmd="sudo cp /proj/SENSS/SENSS_git/SENSS/UI_client_server/GenCertificates/certificates/rootcert.pem /var/www/html/SENSS/UI_client_server/Server/cert/rootcert.pem"
		os.system(cmd)
	else:
		certificate_to_copy=node+"cert.pem"
		cmd="sudo cp /proj/SENSS/SENSS_git/SENSS/UI_client_server/GenCertificates/certificates/"+certificate_to_copy+" /var/www/html/SENSS/UI_client_server/Client/cert/clientcert.pem"
		os.system(cmd)

def configure_nodes():
	nodes={}
	f=open("nodes","r")
	for line in f:
		if "#" in line:
			continue
		node=line.strip().split(" ")[0]
		node_type=line.strip().split(" ")[1]
		server_url=line.strip().split(" ")[2]
		links_to=str(line.strip().split(" ")[3])
		if node_type=="client":
			self=1
		else:
			self=0
		nodes[node]={}
		nodes[node]["as_name"]=node
		nodes[node]["node_type"]=node_type
		nodes[node]["server_url"]=server_url
		nodes[node]["links_to"]=links_to
		nodes[node]["self"]=self
	f.close()


	type=raw_input("Setup for? (client or server): ")
	type=type.strip()
	db_password=getpass.getpass(prompt="Enter root password for mysql:")

	install_dependencies()
	init_database(nodes,db_password)
	print "Initialised DB"
	copy_files()

	for node in nodes:
		print "Node: ",node
		if nodes[node]["node_type"]=="client":
			for node_1,values in nodes.iteritems():
				self="0"
				if values["node_type"]=="client":
					self="1"
				add_client_entries(values["as_name"],values["server_url"],values["links_to"],self,db_password)
			print "Added client entries"

		#copy server/client files
	cmd="sudo service apache2 restart"
	os.system(cmd)

if __name__ == '__main__':
	configure_nodes()
