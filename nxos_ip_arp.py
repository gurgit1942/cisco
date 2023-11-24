#!/usr/bin/python


##  SYNTAX:  python scriptname.py host_filename log_dir
from time import sleep
from datetime import datetime
import re
import netmiko
from netmiko import ConnectHandler
import getpass
import sys

now = datetime.now()
formatnow = now.strftime("%Y-%m-%d-%H-%M")
csv_header = "hostname,Address,Age(min),Hardware_Addr,Type,Interface"

scriptname = sys.argv[0]
host_file_in = sys.argv[1]
log_dir = sys.argv[2]
csv_file = log_dir + "/"+ scriptname +"-" + formatnow + ".csv"


   

username = raw_input('Enter login username: ')
host_file = open(host_file_in,"r")
password = getpass.getpass()

with open(csv_file, 'w') as csv:
    csv.write(csv_header + "\n")
 
 
##  STEP1: Loop through host file
for host in host_file:
    try:
            
        host = host.strip()
        print (host)
        net_connect = ConnectHandler(device_type='cisco_ios',ip=host,username=username,password=password)
        prompt = net_connect.find_prompt()
        
        ### ENTER CISCO COMMAND HERE
        hostname_device = net_connect.send_command('show run | i hostname')
        hostname = re.sub(r"hostname ","",hostname_device)
        print(hostname + "\n")
        output = net_connect.send_command('show ip arp vrf all | beg Address')
                
        #print ("output return:", output)
        
        show_op=[]
        show_op = output.split("\n")
        #pop fisrt line as it is artifact way we get ouput and have no information
        show_op.pop(0)
        #print(show_op)
        hostname = re.sub(r"\n","", hostname)
        
        for elem in show_op:
            #print(elem)
            line= re.sub(r"[\s]+",",",elem)
            #print(line + "\n")
            
            with open(csv_file, 'a') as csv:
                csv.write(hostname + "," + line + "\n")
                print(hostname + "," + line + "\n")
            
        #print(show_op)
           
        
        
        
    except NameError:
        print ("Error in hostname %s", host)
    except:
        #Move on to the next switch 
        print ("Moving on to next switch in the list ...")
csv.close()
