#!/usr/bin/python3


###  SYNTAX:  python scriptname.py inputdevicefile templatefile  log_dir
from time import sleep
from datetime import datetime
import re
import sys

now = datetime.now()
formatnow = now.strftime("%Y-%m-%d-%H-%M")

scriptname = sys.argv[0]
host_file_in = sys.argv[1]
template_file_h = sys.argv[2]
log_dir = sys.argv[3]

host_file = open(host_file_in,"r")
 
##  STEP1: Loop input device file
for host in host_file:
    try:
        host = host.strip()
        host = host.split(",")
        hostname = host[0]
        print (hostname)
        odd = host[1]
        print(odd)
        even = host[2]
        print(even)
        op_file = log_dir + "/"+ hostname + "-Span-Po-Vlan-" + formatnow + ".txt"
        print(op_file + "\n")
        
        with open(op_file, 'w') as txt:
            with open(template_file_h,"r") as template_file:
                #print(commands)
                for line in template_file:        
                    line = re.sub(r"ODD", odd , line)
                    line = re.sub(r"EVEN", even , line)
                    line = re.sub(r"\n", "\r\n" , line)
                        
                    with open(op_file, 'a') as txt:
                        txt.write(line)
                        
            template_file.close()    
                
        txt.close()
            
            
            
    except NameError:
            print ("Error in hostname : ", host)
    except:
        #Move on to the next switch 
        print ("Moving on to next switch in the list ...")