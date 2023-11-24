#!/usr/bin/python3


###  SYNTAX:  python scriptname.py hostfilename commandsfile log_dir
from time import sleep
from datetime import datetime
import re
import netmiko
from netmiko import ConnectHandler
import getpass
import sys
import inspect

def lineno():
    '''Returns line number in program'''
    return inspect.currentframe().f_back.f_lineno

now = datetime.now()
formatnow = now.strftime("%Y-%m-%d-%H-%M")

scriptname = sys.argv[0]
host_file_in = sys.argv[1]
commands_file = sys.argv[2]
log_dir = sys.argv[3]

host_file = open(host_file_in,"r")


username = raw_input('Enter login username: ')
password = getpass.getpass()



 
 
##  STEP1: Loop through host file
for host in host_file:
    try:
        host = host.strip()
        host = host.split(",")[0]
        print ("program line :" + str(lineno()) + "," + host)
        net_connect = ConnectHandler(device_type='cisco_ios',ip=host,username=username,password=password)
        prompt = net_connect.find_prompt()
        
        try:
            #get hostname
            hostname_device = net_connect.send_command('show run | i hostname')
            print("program line :" + str(lineno())+ "," + hostname_device)
            hostname = hostname_device.split(" ")[1]
            hostname = re.sub(r"\n","",hostname)
            #hostname = re.sub(r"hostname ","",hostname_device)
            print("program line :" + str(lineno())+ "," + hostname + "\n")
            
            op_file = log_dir + "/"+ hostname + "-" + scriptname + "-" + formatnow + ".txt"
            print("program line :" + str(lineno())+ "," + op_file + "\n")
            #op_file =  hostname + "-" + scriptname + "-" + formatnow + ".txt"
            
            with open(op_file, 'w') as txt:
                with open(commands_file,"r") as commands:
                    #print("program line :" + str(lineno())+ "," + commands)
                    for comm in commands:        
                        #get show commands output
                        comm = comm.strip()
                        #print("program line :" + str(lineno())+ "," + comm + "\n")
                        #print("getting show from commands list")
                        #command_pass = comm
                        print("getting output of show :" + comm)
                        output = net_connect.send_command(comm)
                        output = re.sub(r"\n","\r\n",output)
                        #print ("program line :" + str(lineno())+ "," + "output return:", output)
                            
                        with open(op_file, 'a') as txt:
                            txt.write("output of command :" + comm + "\n")
                            txt.write(output + "\n")
                commands.close()    
                
            txt.close()
            
            
            
        except NameError:
            print ("Error in hostname : ", host)
    except:
        #Move on to the next switch 
        print ( "program line :" + str(lineno())+ "," + " Moving on to next switch in the list ...")