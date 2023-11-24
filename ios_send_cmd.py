#!/usr/bin/python3


###  SYNTAX:  python scriptname.py hostfilename command_line
from time import sleep
from datetime import datetime
import re
import netmiko
from netmiko import ConnectHandler
import getpass
import sys

now = datetime.now()
formatnow = now.strftime("%Y-%m-%d-%H-%M-%S")
csv_header = "hostname,Protocol,Address,Age(min),Hardware_Addr,Type,Interface"

scriptname = sys.argv[0]
host_file = sys.argv[1]
command_line = sys.argv[2]

csv_file = scriptname +"-" + formatnow + ".csv"

###Line Number function
def lineno():
    import inspect
    '''Returns line number in program'''
    return 'Program line number is :{} '.format(inspect.currentframe().f_back.f_lineno)
###
   

username = raw_input('Enter login username: ')
host_file = open(host_file,"r")
password = getpass.getpass()

with open(csv_file, 'w') as csv:
    csv.write(csv_header + "\n")
 
 
##  STEP1: Loop through host file
for host in host_file:
    try:
            
        host = host.strip()
        host = host.split(",")[0]
        print(lineno() , host)
        net_connect = ConnectHandler(device_type='cisco_ios',ip=host,username=username,password=password)
        prompt = net_connect.find_prompt()
        #print(lineno() ,prompt)
        hostname = prompt.split("#")[0]
        #print(lineno() ,hostname)
        
     
 
        #get show run
        print("getting show output")
        command_pass = command_line
        output = net_connect.send_command(command_pass)
        
        print (output)
        
        list_csv1 = output
    
        #print(list_csv1)
        with open(csv_file, 'a') as csv:
            csv.write(list_csv1 + "\n")
            
        
        
        
        
    except NameError:
        print ("Error in hostname %s", host)
    except:
        #Move on to the next switch 
        print ("Moving on to next switch in the list ...")
