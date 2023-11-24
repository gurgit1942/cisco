###  SYNTAX:  python scriptname.py host_filename
from time import sleep
from datetime import datetime
import re
import netmiko
from netmiko import ConnectHandler
import getpass
import sys

import os
import socket

###Line Number function
def lineno():
    import inspect
    '''Returns line number in program'''
    return 'Program line number is :{} '.format(inspect.currentframe().f_back.f_lineno)
###
#print(lineno())
#### Custom create directory function
def dir_create(dpath): 
    # path
    try:  
        if os.path.isdir(dpath):
            print(lineno(), "existing directory will be  used")
        else:
            os.mkdir(dpath)  
    except OSError as error:  
        print(lineno() + error) 
####
##
if __name__ == '__main__':
    
    now = datetime.now()
    formatnow = now.strftime("%Y-%m-%d-%H-%M-%S")
    csv_header = "Hostname,Port,Name,Status,Vlan,Duplex,Speed,Type"

    scriptname = sys.argv[0]
    host_file_in = sys.argv[1]
    log_dir = scriptname + "-" + formatnow
    log_dir = re.sub(r"\|/","",log_dir)
    dir_create(log_dir)
    #print(lineno() , ": " , "Log Directory name is :", log_dir)
    csv_file = log_dir + "/"+ scriptname +"-" + formatnow + ".csv"
    
    username = raw_input('Enter login username: ')
    password = getpass.getpass()
    #
    with open(csv_file, 'w') as csv:
        csv.write(csv_header + "\n")
    ##initilize list for all outputs from show commands
    
    
    ##  loop through hosts
    with open(host_file_in,"r") as host_file :
        show_int_stat=[]
        for host in host_file:
            try:
                host = host.strip()
                host = host.split(",")[0]
                print(lineno() , host)
                net_connect = ConnectHandler(device_type='cisco_nxos',ip=host,username=username,password=password)
                prompt = net_connect.find_prompt()
                ##
                hostname = prompt.split("#")[0]
                print(lineno(), hostname)
                ##get mac table
                print(lineno(), "get int status")
                command_pass = "sh int status | exclude Port|------------"
                output_ints = net_connect.send_command(command_pass)
                #print (lineno() , "output_mac return:", output_mac)
                '''
                nxos format:Hostname,Port,Name,Status,Vlan,Duplex,Speed,Type
                nxos format format :Hostname,Port,Name,Status,Vlan,Duplex,Speed,Type
                ios format: 
                ios format modified: 
                '''
                
                show_int_stat_p1 = []
                show_int_stat_p1 = output_ints.split("\n")
                #
                for elem in show_int_stat_p1:
                    if elem != "":
                        if re.search("^Po|^mgmt|^Vlan|^Lo", elem):
                            elem_list = []
                            elem_list = elem.split()
                            line_p1 = ",".join(map(str,elem_list[:1]))
                            line_p3 = ",".join(map(str,elem_list[-5:]))
                            line_p2 = " ".join(map(str,elem_list[1:-5]))
                            line = hostname + "," + line_p1 + "," + line_p2 + "," + line_p3
                            show_int_stat.append(line)
                #
                print (lineno() , "No of enties:", len(show_int_stat))
                #print(lineno(),"\n".join(map(str,show_int_stat)))             
                
                      
                
                      
                
            except NameError:
                print ("Error in hostname %s", host)
            except:
                #Move on to the next switch 
                print ("Moving on to next switch in the list ...")
        with open(csv_file, 'a') as csv:
            csv.write("\n".join(map(str,show_int_stat)))
    