#!/usr/bin/python


##  SYNTAX:  python show_verV2.py 

import netmiko
from netmiko import ConnectHandler
import getpass
devtools = ""
#username = raw_input('Enter login username: ')

username = "xxxxx"    ## ENTER AD or SA USERNAME HERE  ** JUST username no suffix ex: kummarr2
host_file = open("./showhosts.txt","r")
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
                	platform = net_connect.send_command('show mac address-table ')    ### ENTER CISCO COMMAND HERE
			#platform2 = platform.splitlines()
			#ver = platform2[1].split()	
			##plat = platform2[1].split()
	                print ("Platform|Version|Model:", platform)	
                        print ("\n==============================================================================\n")
                	#if 'REDI00' in prompt:
                        #    hostname = net_connect.send_command('show run | incl hostname')
                        #    print ("Hostanme is: ", hostname)
                         #   ipint = net_connect.send_command('show ip int br | exclude unassigned')
                        #   print ("Output : ", ipint )
   	
                      
                except:
                       print ("Error in hostname %s", host)
        except:
                #Move on to the next switch 
        	print ("Moving on to next switch in the list ...")