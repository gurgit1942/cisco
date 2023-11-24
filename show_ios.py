#!/usr/bin/python


##  SYNTAX:  python show_verV2.py 
from time import sleep
from datetime import datetime
import re
import netmiko
from netmiko import ConnectHandler
import getpass
import sys

now = datetime.now()
formatnow = now.strftime("%Y-%m-%d-%H-%M")
csv_header = "Host,Space,VLAN,MAC_Address,Type,age,Secure,NTFY,Ports,Device"
scriptname = sys.argv[0]
host_file = sys.argv[1]
#host_file = "./showhosts.txt"
csv_file = scriptname +"-" + formatnow + ".csv"

   
devtools = ""
username = raw_input('Enter login username: ')

#username = "xxxxx"    ## ENTER AD or SA USERNAME HERE  ** JUST username no suffix ex: kummarr2
#host_file = open("./showhosts.txt","r")
host_file = open(host_file,"r")
password = getpass.getpass()
#results = {'host': 'Result'}


 
 
##  NOTE:  MAKE SURE 
for host in host_file:
        try:
                
                host = host.strip()
                print (host)
                net_connect = ConnectHandler(device_type='cisco_ios',ip=host,username=username,password=password)
                prompt = net_connect.find_prompt()
                try:
                        ### ENTER CISCO COMMAND HERE
                        hostname_device = net_connect.send_command('show run | i hostname')
                        hostname = re.sub(r"hostname ","",hostname_device)
                        print(hostname + "\n")
                        output = net_connect.send_command('show mac address-table | i dynamic|static')
                        opfile = hostname + "-" + csv_file
                        #opfile = csv_file
                        with open(opfile, 'w') as csv:
                                csv.write(csv_header + "\n")
                                #print ("output return:", output)
                                list_csv1 = re.sub(r"[\n]","NEWLINE",output)
                                list_csv1 = re.sub(r"[\s]+",",",list_csv1)
                                list_csv1 = re.sub(r"NEWLINE","\n",list_csv1)
                                print(list_csv1)
                                csv.write(list_csv1 + "\n")
                        
                        
                except:
                        print ("Error in hostname %s", host)
        except:
                #Move on to the next switch 
        	print ("Moving on to next switch in the list ...")