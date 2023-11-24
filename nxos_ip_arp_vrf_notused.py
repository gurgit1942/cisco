#!/usr/bin/python3
######

##  SYNTAX:  python scriptname.py hostfilename logdir
from time import sleep
from datetime import datetime
import re
import netmiko
from netmiko import ConnectHandler
import getpass
import sys

now = datetime.now()
formatnow = now.strftime("%Y-%m-%d-%H-%M")
csv_header = "hostname,Address,Age,MAC_Address,Interface,Flags"

scriptname = sys.argv[0]
host_file = sys.argv[1]
log_dir = sys.argv[2]
csv_file = log_dir + "/"+ scriptname +"-" + formatnow + ".csv"

   

username = raw_input('Enter login username: ')
host_file = open(host_file,"r")
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
        
        #get hostname
        hostname_device = net_connect.send_command('show run | i hostname')
        hostname = re.sub(r"hostname ","",hostname_device)
        print(hostname + "\n")
        #get vrf list
        vrf_str = net_connect.send_command('sh vrf | exclude VRF-Name')
        
        #print(vrf_str )
        
        vrflist_n=[]
        vrflist_n =  vrf_str.split("\n")
        #print(vrflist_n)
        
        vrf_list = []
        for elem in vrflist_n:
            #print(elem)
            vrf_name = re.sub(r"[\s]+",",",elem)
            #print(vrf_name + "\n")
            vrf_name_elem = vrf_name.split(",")[0]
            #print(vrf_name_elem + "\n")
            vrf_list.append(vrf_name_elem)
        #print(vrf_list)
            
            
 
        #get ip arp from global table
        print("getting show from global table")
        command_pass = "show ip arp | beg Address"
        output = net_connect.send_command(command_pass)
            
        #print ("output return:", output)
        
        list_csv1 = (hostname + "," + re.sub(r"[\n]","NEWLINE" + hostname +"," ,output))
        list_csv1 = re.sub(r"[\s]+",",",list_csv1)
        list_csv1 = re.sub(r"NEWLINE","\n",list_csv1)
    
        #print(list_csv1)
        with open(csv_file, 'a') as csv:
            csv.write(list_csv1 + "\n")
            
        #get arp table from vrfs
        for elem in vrf_list:
            print("getting show from vrf %s" ,elem )
            command_pass = "show ip arp vrf" + " " + elem + "| beg Address"
            output = net_connect.send_command(command_pass)
                
            #print ("output return:", output)
            
            list_csv1 = (hostname + "," + re.sub(r"[\n]","NEWLINE" + hostname +"," ,output))
            list_csv1 = re.sub(r"[\s]+",",",list_csv1)
            list_csv1 = re.sub(r"NEWLINE","\n",list_csv1)
        
            #print(list_csv1)
            with open(csv_file, 'a') as csv:
                csv.write(list_csv1 + "\n")
        
    except NameError:
        print ("Error in hostname %s", host)
    except:
        #Move on to the next switch 
        print ("Moving on to next switch in the list ...")
csv.close()