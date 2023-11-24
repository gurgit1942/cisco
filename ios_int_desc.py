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
csv_header = "hostname,Port,Type/Status,Speed/Protocol,Description"

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
        
        #STEPS2: get hostname
        hostname_device = net_connect.send_command('show run | i hostname')
        hostname = re.sub(r"hostname ","",hostname_device)
        print(hostname + "\n")
        #STEPS3: get interface description
        #
        print("getting show from ", hostname)
        command_pass = "show int desc | beg P"
        output = net_connect.send_command(command_pass)
            
        #print ("output return:", output)
        
        show_op=[]
        show_op = output.split("\n")
        #pop first line as it is artifact way we get ouput and have no information
        show_op.pop(0)
        #print(show_op)
        '''
        for i in show_op:
            print(i + "n")
        '''
        
        for elem in show_op:
            #print(elem)
            line1 = re.sub(r"[\s]+",",",elem)
            #print(line1 + "\n")
            line_list =[]
            line_list = line1.split(",")
            #print(line_list)
            #pop list 3 times to get description field
            line = line_list[0] + "," + line_list[1] + "," + line_list[2] + ","
            #print(line + "\n")
            line_list.pop(0)
            line_list.pop(0)
            line_list.pop(0)
            line_add = ""
            for elem in line_list:
                line_add += elem + " "
                #print(line_add)
            line = line + line_add
            #print(line + "\n")
            
            with open(csv_file, 'a') as csv:
                csv.write(hostname + "," + line + "\n")
                print(hostname + "," + line )
            
           
      
            
        
        
    except NameError:
        print ("Error in hostname %s", host)
    except:
        #Move on to the next switch 
        print ("Moving on to next switch in the list ...")
csv.close()