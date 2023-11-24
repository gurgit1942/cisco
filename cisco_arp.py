###  SYNTAX:  python scriptname.py host_filename
## arp output in csv format
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
#### Custom create directory function
def dir_create(dpath): 
    # chsck if directory is present and create if not
    try:  
        if os.path.isdir(dpath):
            print(lineno(), "existing directory will be  used and will overwrite files in directory")
        else:
            os.mkdir(dpath)  
    except OSError as error:  
        print(lineno() + error)
#### nxos mac table function
def dev_type(net_connect):
    ###get os type
    command_pass = "show ver | i Nexus"
    output = net_connect.send_command(command_pass)
    #
    if output:
        devi_type ="cisco_nxos"
    else:
        devi_type ="cisco_ios"
    print(lineno(), devi_type)
    return devi_type
###
def nxos_ip_arp_list(hostname,output_list,net_connect):
    import re
    '''
    nxos format:Hostname,IP_Address,Age,MAC Address,Interface,Flags
    nxos format:Hostname,IP_Address,Age,MAC_Address,Interface,Flags
    ios format: Hostname,Protocol,IP_Address,Age(min),Hardware_Addr,Type,Interface 
    drop "protocol" and "Type". "Lags" has no value for ios
    ios format: Hostname,IP_Address,Age,MAC_Address,Interface,Flags
    '''
    ###get arp table
    command_pass = 'show ip arp vrf all | egrep ^[0-9]'
    output = net_connect.send_command(command_pass)
    #
    output_list_p1 = []
    output_list_p1 = output.split("\n")
    current_length_output_list = len(output_list)
    #print(lineno(),current_length_output_list)
    #
    for elem in output_list_p1:
        if "INCOMPLETE" in elem:
            pass
        elif elem != "":
            line = re.sub(r"[\s]+",",",elem)
            line_list = line.split(",")
            line = hostname + "," + ",".join(map(str,line_list[:5]))
            #print(lineno(), line)
            output_list.append(line)
        else:
            pass
            
    #
    #
    current_length_output_list_after_onedevice = len(output_list)
    no_of_entries_added = current_length_output_list_after_onedevice - current_length_output_list
    print (lineno(), 'Number of enties for host "{}" and command "{}" are : "{}" '.format((hostname), str(command_pass), str(no_of_entries_added)))
    #return output_list
    
##
##
def ios_ip_arp_list(hostname,output_list,net_connect):
    import re
    '''
    nxos format:Hostname,Address,Age,MAC Address,Interface,Flags
    nxos format:Hostname,Address,Age,MAC_Address,Interface,Flags
    ios format: Hostname,Protocol,Address,Age(min),Hardware_Addr,Type,Interface 
    drop "protocol" and "Type". "Lags" has no value for ios
    ios format: Hostname,Address,Age,MAC_Address,Interface,Flags
    '''
    ###get vrf list
    command_pass = 'sh ip vrf detail | i default VPNID'
    output = net_connect.send_command(command_pass)
    #
    vrflist_n=[]
    vrflist_n =  output.split("\n")
    #print(lineno(), vrflist_n)
    
    vrf_list = []
    if len(vrflist_n) >0:
        for elem in vrflist_n:
            #print(elem)
            if elem!="":
                vrf_name = re.sub(r"[\s]+",",",elem)
                #print(vrf_name + "\n")
                vrf_name_elem = vrf_name.split(",")[1]
                #print(vrf_name_elem + "\n")
                vrf_list.append(vrf_name_elem)
    #print(lineno(), "vrf list is : ",  vrf_list)
    #
    #get ip arp from global table
    #print("getting show from global table")
    command_pass = "show ip arp | i [0-9]"
    output = net_connect.send_command(command_pass)
    output_list_p1 = []
    output_list_p1 = output.split("\n")
    current_length_output_list = len(output_list)
    #print(lineno(),current_length_output_list)
    #
    for elem in output_list_p1:
        if "Incomplete" in elem:
            pass
        elif elem != "":
            
            line = re.sub(r"[\s]+",",",elem)
            line_list = line.split(",")
            line = hostname + "," + ",".join(map(str,line_list[1:4])) + "," + str(line_list[-1])
            #print(line)
            output_list.append(line)
        else:
            pass
    #
    #get arp table from vrfs
    for elem in vrf_list:
        if elem!="":
            command_pass = "show ip arp vrf" + " " + elem + " | i [0-9]"
            output = net_connect.send_command(command_pass)
            output_list_p1 = []
            output_list_p1 = output.split("\n")
            current_length_output_list = len(output_list)
            #print(lineno(),current_length_output_list)
            #
            for elem in output_list_p1:
                if "Incomplete" in elem:
                    pass
                elif elem != "":
                
                    line = re.sub(r"[\s]+",",",elem)
                    line_list = line.split(",")
                    line = hostname + "," + ",".join(map(str,line_list[1:4])) + "," + str(line_list[-1])
                    #print(line)
                    output_list.append(line)
                else:
                    pass
       
            
    #
    current_length_output_list_after_onedevice = len(output_list)
    no_of_entries_added = current_length_output_list_after_onedevice - current_length_output_list
    print (lineno(), 'Number of enties (including vrfs) for host "{}" and command "{}" are : "{}" '.format((hostname), str(command_pass), str(no_of_entries_added)))
    #return output_list
    
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
        
        ##show commands individual lists
        show_ip_arp = []
        #
        for host in host_file:
            try:
                host = host.strip()
                host = host.split(",")[0]
                print(lineno() ,"info from input host file:", host)
                
                net_connect = ConnectHandler(device_type='cisco_ios',ip=host,username=username,password=password)
                prompt = net_connect.find_prompt()
                #print(lineno() ,prompt)
                hostname = prompt.split("#")[0]
                print(lineno() ,hostname)
                
                devi_type=dev_type(net_connect)
                print(lineno(), hostname,devi_type)
                #
                net_connect = ConnectHandler(device_type=devi_type,ip=host,username=username,password=password)
                prompt = net_connect.find_prompt()
                hostname = prompt.split("#")[0]
                print(lineno() ,hostname)
                ##get mac table
                if devi_type == "cisco_nxos":
                    #
                    nxos_ip_arp_list(hostname,show_ip_arp,net_connect)
                    #print(lineno(),hostname,"show_ip_arp",net_connect)
                else:
                    #
                    ios_ip_arp_list(hostname,show_ip_arp,net_connect)
                    #print(lineno(),hostname,"show_ip_arp",net_connect)
                
                print (lineno() , "No of enties are :" , len(show_ip_arp))
                #print(lineno(),"\n".join(map(str,show_ip_arp)))
                #
            except NameError:
                print ("Error while login ", host)
            except:
                #Move on to the next switch 
                print ("Moving on to next switch in the list ...")
        print (lineno(), 'No. of entries in arp table list are :{} '.format(len(show_ip_arp)))
        with open(csv_file, 'a') as csv:
            csv.write("\n".join(map(str,show_ip_arp)))
        