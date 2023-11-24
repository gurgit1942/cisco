#!/usr/bin/python


##  SYNTAX:  python scriptname.py hostfilename
from time import sleep
from datetime import datetime
import re
import netmiko
from netmiko import ConnectHandler
import getpass
import sys

now = datetime.now()
formatnow = now.strftime("%Y-%m-%d-%H-%M")
csv_header = "hostname,Protocol,Address,Age(min),Hardware_Addr,Type,Interface"

scriptname = sys.argv[0]
host_file_in = sys.argv[1]

csv_file = scriptname +"-" + formatnow + ".csv"

   

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
        output = net_connect.send_command('show ip arp | beg Address')
                
        #print ("output return:", output)
            
        list_csv1 = (hostname + "," + re.sub(r"[\n]","NEWLINE" + hostname +"," ,output))
        list_csv1 = re.sub(r"[\s]+",",",list_csv1)
        list_csv1 = re.sub(r"NEWLINE","\n",list_csv1)
        
        print(list_csv1)
        with open(csv_file, 'a') as csv:
            csv.write(list_csv1 + "\n")
        
    except NameError:
        print ("Error in hostname %s", host)
    except:
        #Move on to the next switch 
        print ("Moving on to next switch in the list ...")
csv.close()