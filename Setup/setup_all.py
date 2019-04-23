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
import paramiko
import getpass
import socket
import urllib2
import subprocess
import time
import os

def init_database(ssh,nodes,is_client):
	stdin, stdout, stderr = ssh.exec_command("sudo python ./init.py usc558l")
	data=stdout.readlines()
	if is_client==1:
		return
	for node,node_data in nodes.iteritems():
		stdin, stdout, stderr = ssh.exec_command("sudo python ./insert_topo.py "+node+" "+node_data["links_to"]+" "+str(node_data["self"]))
		data=stdout.readlines()

def add_client_entries(ssh,as_name,server_url,links_to,self):
	if links_to=="None":
		return
	stdin, stdout, stderr = ssh.exec_command("sudo python ./insert_senss_client.py usc558l "+as_name+" "+server_url+" "+links_to+" "+self)
	data=stdout.readlines()

def copy_files(ssh):
	stdin, stdout, stderr = ssh.exec_command("sudo cp -rf Server/ /var/www/html/")
	data=stdout.readlines()
	stdin, stdout, stderr = ssh.exec_command("sudo cp -rf Client/ /var/www/html/")
	data=stdout.readlines()

def install_dependencies(ssh):
	stdin, stdout, stderr = ssh.exec_command("sh ./install_dependencies.sh")
	data=stdout.readlines()
	print "Installed dependencies"

#Need to modify this to be supportive for multiple elements
def start_monitor_flows(ssh,multiply,legit_address):
	stdin, stdout, stderr = ssh.exec_command("screen -d -m sudo python /var/www/html/SENSS/UI_client_server/Server/monitor_flows.py "+str(multiply)+" "+str(legit_address))
	data=stdout.readlines()
	print "Started Monitoring flows controller"

def print_data(data):
	for item in data:
		print item.strip()

def copy_certificates(server_flag,node,ssh):
	print "Copying certificates"
	if server_flag==True:
        	stdin, stdout, stderr = ssh.exec_command("sudo cp /proj/SENSS/SENSS_git/SENSS/UI_client_server/GenCertificates/certificates/rootcert.pem /var/www/html/SENSS/UI_client_server/Server/cert/rootcert.pem")
        	data=stdout.readlines()
	else:
		certificate_to_copy=node+"cert.pem"
        stdin, stdout, stderr = ssh.exec_command("sudo cp /proj/SENSS/SENSS_git/SENSS/UI_client_server/GenCertificates/certificates/"+certificate_to_copy+" /var/www/html/SENSS/UI_client_server/Client/cert/clientcert.pem")
        data=stdout.readlines()

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
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(node,username=user, password=password, timeout=3)
		ip_1,ip_2,first_octet=return_ips(node)
		controller_ip=socket.gethostbyname(node)
		print "Node: ",node
		install_dependencies(ssh)

		if nodes[node]["node_type"]=="client":
			init_database(ssh,nodes,1)
		else:
			init_database(ssh,nodes,0)
		print "Initialised DB"

		if nodes[node]["node_type"]=="client":
			for node_1,values in nodes.iteritems():
				self="0"
				if values["node_type"]=="client":
					self="1"
				#print "Addding",values["asn"],values["server_url"],values["links_to"],self
				add_client_entries(ssh,values["asn"],values["server_url"],values["links_to"],self)
			print "Added client entries"

		#copy server/client files
		copy_files(ssh)

		stdin, stdout, stderr = ssh.exec_command("sudo service apache2 restart")
		data=stdout.readlines()

		if nodes[node]["node_type"]=="client" and (attack_type=="proxy" or attack_type=="amon_proxy"):
			stdin, stdout, stderr = ssh.exec_command("sudo rm /var/www/html/SENSS/UI_client_server/Client/constants.php")
			data=stdout.readlines()
			string_to_write="<?php\n"
			string_to_write=string_to_write+'const PROXY_URL="http://'+proxy_ip+'/SENSS/UI_client_server/Proxy/api.php?action=proxy_info";\n'
			stdin, stdout, stderr = ssh.exec_command("echo '"+string_to_write+"' | sudo tee -a /var/www/html/SENSS/UI_client_server/Client/constants.php")
			data=stdout.readlines()


if __name__ == '__main__':
	configure_nodes()
