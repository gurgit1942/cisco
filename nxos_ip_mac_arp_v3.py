###  SYNTAX:  python scriptname.py host_filename log_dir
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
def dir_create(path): 
    # path
    try:  
        os.mkdir(path)  
    except OSError as error:  
        print(lineno() + error) 
####
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
##
if __name__ == '__main__':
    
    now = datetime.now()
    formatnow = now.strftime("%Y-%m-%d-%H-%M")
    csv_header = "Hostname,Space,VLAN,MAC_Address,Type,age,Secure,NTFY,Ports,misc_info,Type/Status,Speed/Protocol,Description,Address,DNS_Name"

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
    mac_port_list = []
    port_desc_list = []
    arp_mac_list = []
    ##  loop through hosts
    with open(host_file_in,"r") as host_file :
        for host in host_file:
            try:
                host = host.strip()
                host = host.split(",")[0]
                print(lineno() , host)
                net_connect = ConnectHandler(device_type='cisco_ios',ip=host,username=username,password=password)
                prompt = net_connect.find_prompt()
                ##
                hostname = prompt.split("#")[0]
                ##get mac table
                print(lineno(), "get mac table")
                #command_pass = "show mac address-table dynamic | beg "
                command_pass = "show mac address-table dynamic | beg VLAN"
                output_mac = net_connect.send_command(command_pass)
                #print (lineno() , "output_mac return:", output_mac)
                
                show_op_mac=[]
                show_op_mac_p1 = []
                show_op_mac_p1 = output_mac.split("\n")
                prefix_ports = []
                for elem in show_op_mac_p1:
                    if re.search("vlan|------+-----", elem):
                        #print(lineno(), "Junk removed " + elem +"\n")
                        pass
                    else:
                        if re.search("dynamic|static", elem):
                            show_op_mac.append(elem)
                        else:
                            pass
                print (lineno() , "No of enties:", len(show_op_mac))        
                #print(lineno(),"\n".join(map(str,show_op_mac)))
                
                ##get description table
                print(lineno(), "get description table")
                command_pass = 'sh int desc | exclude "Interface|Port|------------------"'
                output_desc = net_connect.send_command(command_pass)
                #print (lineno() , "output_desc return:", output_desc)
                show_op_desc=[]
                show_op_desc = output_desc.split("\n")
                print (lineno() , "No of enties:", len(show_op_desc))
                #print(show_op_desc)
                #print(lineno(),"\n".join(map(str,show_op_desc)))
                ###
                #get ip arp from global table
                print(lineno(), "get ip arp from global table")
                
                command_pass = "show ip arp vrf all"
                output_arp = net_connect.send_command(command_pass)
                #print (lineno(), "output return:", output_arp)
                show_op_arp=[]
                if output_arp != "":
                    show_op_arp = output_arp.split("\n")
                    print (lineno() , "No of enties:", len(show_op_arp))
                    #print (show_op_arp)
                    #
                    for elem in show_op_arp:
                        #print(lineno(),elem)
                        line = ""
                        if elem !="":
                            line= re.sub(r"[\s]+",",",elem)
                            #print(lineno(),line + "\n")
                            arp_mac_list.append(hostname + "," + line)
                    ####
                print (lineno() , "No of enties:", len(arp_mac_list))
                print (arp_mac_list[0])
                 
                leftside_line_list = ""    
                for elem in show_op_mac:
                    if elem != "":
                        #print(lineno(),elem)
                        line = re.sub(r"[\s]+",",",elem)
                        #print(lineno(),line)
                        line_list = []
                        line_list = line.split(",")
                        #print(lineno(),line_list)
                        port_list = []
                        port_list = line_list[7:]
                        #print(lineno(),port_list)
                        
                        leftside_line_list_curr = ""
                        leftside_line_list_curr = ",".join(line_list[:6])
                        if leftside_line_list_curr != "":
                            leftside_line_list =  leftside_line_list_curr
                        else:
                            leftside_line_list = leftside_line_list
                        for i in port_list:
                            line = ""
                            line = leftside_line_list + "," + i
                            #print(lineno(),line + "\n")
                            mac_port_list.append(hostname + "," + line)
                            #print(lineno(),hostname + "," + line )
                '''            
                for elem in show_op_desc:
                    #print(lineno(),elem)
                    line= re.sub(r"[\s]+",",",elem,3)
                    #print(lineno(),line + "\n")
                    port_desc_list.append(hostname + "," + line)
                '''
                for elem in show_op_desc:
                    if re.search("-------------", elem):
                        pass
                    elif re.search("^Po|^mgmt0|^Vlan|^Lo", elem):
                        #print(elem)
                        line = ""
                        line = re.sub(r"[\s]+",",,,",elem,1)
                        #print(lineno(),line + "\n")
                        port_desc_list.append(hostname + "," + line)
                    else:
                        #print(elem)
                        line = ""
                        line= re.sub(r"[\s]+",",",elem,3)
                        #print(lineno(),line + "\n")
                        port_desc_list.append(hostname + "," + line)
                    
            except NameError:
                print ("Error in hostname %s", host)
            except:
                #Move on to the next switch 
                print ("Moving on to next switch in the list ...")
    #
    #print(lineno(),"\n".join(map(str,mac_port_list)))
  
    #
    with open(csv_file, 'a') as csv:
        csv.write("\n".join(map(str,mac_port_list)))
    #print(lineno())
    ###
    #print("\n".join(map(str,port_desc_list)))
    with open(csv_file, 'a') as csv:
        csv.write("\n".join(map(str,port_desc_list)))
        ###
    #print("\n".join(map(str,port_desc_list)))
    with open(csv_file, 'a') as csv:
        csv.write("\n".join(map(str,arp_mac_list)))
   
    ##create dict for reference of all outputs
    
    port_desc_dict = {}
    arp_mac_dict = {}
    #
    for line in port_desc_list:
        item = line.split(",")
        k = item[0] + "-" + item[1]
        v = ",".join(item[2:])
        port_desc_dict[k] = [v]
        #print(str(k) + ":" + str(v))
    '''
    #
    for k, v in port_desc_dict.items():
        print(k,v)
    #
    '''
    for line in arp_mac_list:
        item = line.split(",")
        #print(lineno(), item)
        item4 = ""
        item4 = re.sub(r"port-channel","Po",item[4])
        item4 = re.sub(r"Vlan","",item4)
        item4 = re.sub(r"Ethernet","Eth",item4)
        # k = hostname+ mac_addr+ port
        # v = ip_addr
        k = item[0] + "-" + str(item[3]) + "-" + str(item4)
        v = item[1]
        arp_mac_dict[k] = [v]
        #print(str(k) + ":" + str(v))
    '''
    #
    for k, v in arp_mac_dict.items():
        print(k,v)
    #
    '''
    ###
    for item in mac_port_list:
        line = item.split(",")
        #print(line)
        
        k1 = str(line[0]) + "-" + str(line[7])
        #print(k1)
        k2 = str(line[0]) + "-" + str(line[3]) + "-"+ str(line[2])
        #print(k2)
        op_line = ""
        if k1 in  port_desc_dict:
            v1 = port_desc_dict[k1]
            v1_str = ",".join(v1)
            op_line = item + "," + str(v1_str)
        else:
            v1 = "NA1,NA1,NA1"
            op_line = item + "," + str(v1)
        #
        if k2 in  arp_mac_dict:
            v2 = arp_mac_dict[k2]
            v2_str = ",".join(v2)
            dns_ptr = host_ptr(v2_str)
            op_line = op_line + "," + str(v2_str) + "," + str(dns_ptr)
        else:
            v2 = "NA2"
            op_line = op_line + "," + str(v2) + "," + "no_ptr_record"
        #print(op_line + "\n")
        with open(csv_file, 'a') as csv:
                    csv.write(op_line + "\n")
        
 