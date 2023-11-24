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
    csv_header = "Hostname,IP_Address,Age,MAC_Address,Interface,Flags"

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
        show_ip_arp=[]
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
                print(lineno(), "get arp table all vrfs")
                command_pass = "show ip arp vrf all"
                output_arp = net_connect.send_command(command_pass)
                #print (lineno() , "output_mac return:", output_mac)
                '''
                nxos format:Hostname,IP_Address,Age,MAC_Address,Interface/Vlan,Flags
                nxos format format :Hostname,IP_Address,Age,MAC_Address,Interface,Flags
                ios format: 
                ios format modified: 
                '''
                
                show_ip_arp_p1 = []
                show_ip_arp_p1 = output_arp.split("\n")
                #
                for elem in show_ip_arp_p1:
                    if elem != "":
                        if re.search("^[0-9]", elem):
                            line = ""
                            line = hostname + "," + re.sub(r"[\s]+",",",elem)
                            show_ip_arp.append(line)
                #
                print (lineno() , "No of enties:", len(show_ip_arp))
                #print(lineno(),"\n".join(map(str,show_ip_arp)))             
                
                      
                
                      
                
            except NameError:
                print ("Error in hostname %s", host)
            except:
                #Move on to the next switch 
                print ("Moving on to next switch in the list ...")
        with open(csv_file, 'a') as csv:
            csv.write("\n".join(map(str,show_ip_arp)))
    