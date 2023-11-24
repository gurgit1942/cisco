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
#### nxos mac table function
def dev_type(net_connect):
    ###get os type
    command_pass = "show ver | i nxos"
    output = net_connect.send_command(command_pass)
    #
    if output:
        devi_type ="cisco_nxos"
    else:
        devi_type ="cisco_ios"
    print(lineno(), devi_type)
    return devi_type

#### nxos mac table function
def nxos_mac_list(hostname,output_list,net_connect):
    '''
    nxos format:Hostname,Space,VLAN,MAC_Address,Type,age,Secure,NTFY,Ports
    nxos format format :Hostname,Space,VLAN,MAC_Address,Type,"LEARN",age,Secure,NTFY,Ports
    ios format: hostname,Space,vlan,mac-address,type,learn,age,ports
    ios format modified: hostname,Space,vlan,mac-address,type,learn,age,"Secure","NTFY",ports
    '''
    ###get mac table
    command_pass = "show mac address-table dynamic | i dynamic"
    output = net_connect.send_command(command_pass)
    #
    output_list_p1 = []
    output_list_p1 = output.split("\n")
    current_length_output_list = len(output_list)
    #print(lineno(),current_length_output_list)
    #
    for elem in output_list_p1:
        if elem != "":
            if re.search("dynamic|static", elem):
                line = ""
                line_list = []
                line = re.sub(r"[\s]+",",",elem)
                line_list = line.split(",",4)
                line = hostname + "," +  ",".join(map(str,line_list[:4]))+ ",," + str(line_list[4])
                #print(line)
                output_list.append(line)
    #
    #
    current_length_output_list_after_onedevice = len(output_list)
    no_of_entries_added = current_length_output_list_after_onedevice - current_length_output_list
    print (lineno(), "No of enties for current host:", str(command_pass), str(no_of_entries_added))
    return output_list
#### ios mac table function
def ios_mac_list(hostname,output_list,net_connect):
    '''
    nxos format:Hostname,Space,VLAN,MAC_Address,Type,age,Secure,NTFY,Ports
    nxos format format :Hostname,Space,VLAN,MAC_Address,Type,"LEARN",age,Secure,NTFY,Ports
    ios format: hostname,Space,vlan,mac-address,type,learn,age,ports
    ios format modified: hostname,Space,vlan,mac-address,type,learn,age,"Secure","NTFY",ports
    '''
    ###get mac table
    command_pass = "show mac address-table dynamic | i dynamic"
    output = net_connect.send_command(command_pass)
    #
    output_list_p1 = []
    output_list_p1 = output.split("\n")
    current_length_output_list = len(output_list)
    #print(lineno(),current_length_output_list)
    #
    for elem in output_list_p1:
        if elem != "":
            if re.search("dynamic|static", elem):
                line = ""
                line_list = []
                line = re.sub(r"[\s]+",",",elem)
                line_list = line.split(",",6)
                line = hostname + "," +  ",".join(map(str,line_list[:6]))+ ",,," + str(line_list[6])
                #print(line)
                output_list.append(line)
    #
    #
    current_length_output_list_after_onedevice = len(output_list)
    no_of_entries_added = current_length_output_list_after_onedevice - current_length_output_list
    print (lineno(), "No of enties for current host:", str(command_pass), str(no_of_entries_added))
    return output_list

    
##
if __name__ == '__main__':
    
    now = datetime.now()
    formatnow = now.strftime("%Y-%m-%d-%H-%M-%S")
    csv_header = "Hostname,Space,VLAN,MAC_Address,Type,Learn,age,Secure,NTFY,Ports"

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
        
        show_op_mac=[]
        for host in host_file:
            try:
                host = host.strip()
                host = host.split(",")[0]
                print(lineno() , host)
                
                net_connect = ConnectHandler(device_type='cisco_ios',ip=host,username=username,password=password)
                prompt = net_connect.find_prompt()
                print(lineno() ,prompt)
                hostname = prompt.split("#")[0]
                print(lineno() ,hostname)
                
                devi_type=dev_type(net_connect)
                print(lineno(), hostname,devi_type)
                #
                net_connect = ConnectHandler(device_type=devi_type,ip=host,username=username,password=password)
                prompt = net_connect.find_prompt()
                hostname = prompt.split("#")[0]
                ##
                if devi_type == "cisco_nxos":
                    nxos_mac_list(hostname,show_op_mac,net_connect)
                else:
                    ios_mac_list(hostname,show_op_mac,net_connect)
                #print(hostname)
                #print (lineno() , "No of enties for mac_list :" , len(show_op_mac))
                #print(lineno(),"\n".join(map(str,show_op_mac)))  
            except NameError:
                print ("Error in hostname %s", host)
            except:
                #Move on to the next switch 
                print ("Moving on to next switch in the list ...")
        with open(csv_file, 'a') as csv:
            csv.write("\n".join(map(str,show_op_mac)))
    