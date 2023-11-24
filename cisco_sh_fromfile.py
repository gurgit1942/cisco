#!/usr/bin/python3


###  SYNTAX:  python scriptname.py hostfilename commandsfile log_dir
from time import sleep
from datetime import datetime
import re
import netmiko
from netmiko import ConnectHandler
import getpass
import sys

now = datetime.now()
formatnow = now.strftime("%Y-%m-%d-%H-%M")

scriptname = sys.argv[0]
host_file = sys.argv[1]
commands_file = sys.argv[2]
log_dir = sys.argv[3]

host_file = open(host_file,"r")

###Line Number function
def lineno():
    import inspect
    '''Returns line number in program'''
    return 'Program line number is :{} '.format(inspect.currentframe().f_back.f_lineno)
###

username = raw_input('Enter login username: ')
password = getpass.getpass()

##  STEP1: Loop through host file
for host in host_file:
    try:
        host = host.strip()
        host = host.split(",")[0]
        print (lineno(),host)
        net_connect = ConnectHandler(device_type='cisco_ios',ip=host,username=username,password=password)
        #print(net_connect)
        prompt = net_connect.find_prompt()
        hostname = prompt.split("#")[0]
        print(lineno(),hostname)
                    
        op_file = log_dir + "/"+ hostname + "-" + scriptname + "-" + formatnow + ".txt"
        print(lineno(), op_file + "\n")
        #op_file =  hostname + "-" + scriptname + "-" + formatnow + ".txt"
    
        
        with open(op_file, 'w') as txt:
            with open(commands_file,"r") as commands:
                #print(commands)
                for comm in commands:        
                    #get show commands output
                    comm = comm.strip()
                    #print(comm + "\n")
                    #print(lineno(),"getting show from commands list")
                    #command_pass = comm
                    print(lineno(),"getting output of show : ", comm)
                    output = net_connect.send_command(comm)
                    output = re.sub(r"\n","\r\n",output)
                    
                    #print (lineno(),"output return:", output)
                        
                    with open(op_file, 'a') as txt:
                        txt.write("output of command :" + comm + "\n")
                        txt.write(output + "\n")
    except NameError:
        print (lineno(),"Error in hostname : ", host)
    except:
        #Move on to the next switch 
        print (lineno(),"Moving on to next switch in the list ...")