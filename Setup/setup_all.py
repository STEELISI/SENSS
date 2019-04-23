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
import json
import subprocess
import time
import os

def init_database(nodes,is_client):
	cmd="sudo python ./init.py usc558l"
	result = subprocess.run(cmd.split(), stdout=subprocess.PIPE)
	print result
	if is_client==1:
		return
	for node,node_data in nodes.iteritems():
		cmd="sudo python ./insert_topo.py "+node+" "+node_data["links_to"]+" "+str(node_data["self"])
		result = subprocess.run(cmd.split(), stdout=subprocess.PIPE)

def add_client_entries(as_name,server_url,links_to,self):
	if links_to=="None":
		return
	cmd="sudo python ./insert_senss_client.py usc558l "+as_name+" "+server_url+" "+links_to+" "+self
	result = subprocess.run(cmd.split(), stdout=subprocess.PIPE)

def copy_files():
	cmd="sudo cp -rf Server/ /var/www/html/"
	result = subprocess.run(cmd.split(), stdout=subprocess.PIPE)

	cmd="sudo cp -rf Client/ /var/www/html/"
	result = subprocess.run(cmd.split(), stdout=subprocess.PIPE)


def install_dependencies():
	cmd="sh ./install_dependencies.sh"
	result = subprocess.run(cmd.split(), stdout=subprocess.PIPE)

	print "Installed dependencies"

#Need to modify this to be supportive for multiple elements
def start_monitor_flows(multiply,legit_address):
	cmd="screen -d -m sudo python /var/www/html/SENSS/UI_client_server/Server/monitor_flows.py "+str(multiply)+" "+str(legit_address)
	result = subprocess.run(cmd.split(), stdout=subprocess.PIPE)
	print "Started Monitoring flows controller"

def print_data(data):
	for item in data:
		print item.strip()

def copy_certificates(server_flag,node):
	print "Copying certificates"
	if server_flag==True:
        	cmd="sudo cp /proj/SENSS/SENSS_git/SENSS/UI_client_server/GenCertificates/certificates/rootcert.pem /var/www/html/SENSS/UI_client_server/Server/cert/rootcert.pem"
			result = subprocess.run(cmd.split(), stdout=subprocess.PIPE)
	else:
		certificate_to_copy=node+"cert.pem"
        cmd="sudo cp /proj/SENSS/SENSS_git/SENSS/UI_client_server/GenCertificates/certificates/"+certificate_to_copy+" /var/www/html/SENSS/UI_client_server/Client/cert/clientcert.pem"
		result = subprocess.run(cmd.split(), stdout=subprocess.PIPE)

def configure_nodes():
	nodes={}
	type=sys.argv[1]
	f=open("nodes_ddos_with_sig","r")
	for line in f:
		if "#" in line:
			continue
		node=line.strip().split(" ")[0]
		node_type=line.strip().split(" ")[1]
		server_url=line.strip().split(" ")[2]
		links_to=str(line.strip().split(" ")[3])
		self=int(line.strip().split(" ")[4])
		if node_type==type:
			nodes[node]={}
			nodes[node]["node_type"]=node_type
			nodes[node]["server_url"]=server_url
			nodes[node]["links_to"]=links_to
			nodes[node]["self"]=self
	f.close()

	for node in nodes:
		print "Node: ",node
		install_dependencies()

		if nodes[node]["node_type"]=="client":
			init_database(nodes,1)
		else:
			init_database(nodes,0)
		print "Initialised DB"

		if nodes[node]["node_type"]=="client":
			for node_1,values in nodes.iteritems():
				self="0"
				if values["node_type"]=="client":
					self="1"
				#print "Addding",values["asn"],values["server_url"],values["links_to"],self
				add_client_entries(values["asn"],values["server_url"],values["links_to"],self)
			print "Added client entries"

		#copy server/client files
		copy_files()

		cmd="sudo service apache2 restart"
		result = subprocess.run(cmd.split(), stdout=subprocess.PIPE)


if __name__ == '__main__':
	configure_nodes()
