#!/usr/bin/python3
#!C:/Users/SinghGu/AppData/Local/Programs/Python/Python36/python.exe


###  SYNTAX:  python scriptname.py inputfilename log_dir
from time import sleep
from datetime import datetime
import re
import sys
import socket

now = datetime.now()
formatnow = now.strftime("%Y-%m-%d-%H-%M")
csv_header = "hostname_in_file,ip_in_file,dns_a_record,dns_ptr_record"
scriptname = sys.argv[0]
input_file = sys.argv[1]
log_dir = sys.argv[2]

input_file_h = open(input_file,"r")

def host_a(h_name):
    try:
        hname = socket.gethostbyname(h_name)
        return  hname
    except:
        hname ="No_A_Record"
        return  hname
 
def host_ptr(ip_addr):
    try:
        h_ptr = socket.gethostbyaddr(ip_addr)
        h_ptr = h_ptr[0]
        return  h_ptr
    except:
        h_ptr ="No_PTR_Record"
        return  h_ptr

op_file = log_dir + "/"+ scriptname + formatnow + ".txt"
#print(op_file + "\r\n")
 
with open(op_file, 'w') as txt: 
    txt.write(csv_header + "\r\n") 
    ##  STEP1: Loop through host,ip file
    for host in input_file_h:
        
        host = host.strip()
        host = host.split(",")
        hostname = str(host[0])
        print (hostname)
        
        dns_a = host_a(hostname)
        
        a_check_value = str(hostname) + ": have dns A record as :" + str(dns_a) + "\r\n"
        print (a_check_value)
        
        ipaddr = host[1]
        
        dns_ptr = host_ptr(ipaddr)
        
        ptr_check_value = str(hostname) + ": have dns PTR record as :" + str(dns_ptr) + "\r\n"
        print (ptr_check_value)
       
        output = str(hostname) + "," + str(ipaddr) + "," + str(dns_a) + "," + str(dns_ptr) + "\r\n"
        
        print(output)
        with open(op_file, 'a') as txt:
            txt.write(output)
            
    
txt.close()
