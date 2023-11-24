###  SYNTAX:  python scriptname.py host_filename new_old_sw_mappingfile
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
def portmappings(mapping_file_in,curr_fut_sw_port):
    # Read input mapping file and create dictionary
    
    with open(mapping_file_in,"r") as map_file:
        for line in map_file:
            line = line.strip()
            line_list = line.split(",")
            item3 = line_list[3]
            item3 = re.sub(r"e","Eth",item3)
            #create key = fut_sw - fut_port , value - curr_sw.curr_port
            k = str(line_list[2]) + "-" + str(item3)
            v = str(line_list[0]) + "," + str(line_list[1])
            print(lineno(), k, v)
            curr_fut_sw_port[k] = [v]
##
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
def cisco_int_status_list(hostname,output_list,net_connect):
    '''
    name dropped as it is not full and truncated
    nxos format:Hostname,Port,Name,Status,Vlan,Duplex,Speed,Type
    nxos format:Hostname,Port,Status,Vlan,Duplex,Speed,Type
    ios format: Hostname,Port,Name,Status,Vlan,Duplex,Speed,Type
    ios format: Hostname,Port,Status,Vlan,Duplex,Speed,Type
    '''
    ###get desc
    command_pass = 'sh int status | egrep invert-match "Interface|Port|------------------"'
    output = net_connect.send_command(command_pass)
    #
    output_list_p1 = []
    output_list_p1 = output.split("\n")
    current_length_output_list = len(output_list)
    #print(lineno(),current_length_output_list)
    #
    for elem in output_list_p1:
        if elem != "":
            if re.search("QSFP-100G40G-BIDI", elem):
                line = re.sub(r"[\s]+",",",elem)
                line_list = line.split(",")
                line = hostname + "," +  str(line_list[0]) + "," + ",".join(map(str,line_list[-5:]))
                #print(lineno(), line)
                output_list.append(line)
            else:
                line = re.sub(r"[\s]+",",",elem)
                line_list = line.split(",")
                line = hostname + "," +  str(line_list[0]) + "," + ",".join(map(str,line_list[-6:-1]))
                #print(lineno(), line)
                output_list.append(line)
    #
    #
    current_length_output_list_after_onedevice = len(output_list)
    no_of_entries_added = current_length_output_list_after_onedevice - current_length_output_list
    print (lineno(), "No of enties for current host:", str(command_pass), str(no_of_entries_added))
    #return output_list
    
##
#### nxos mac table function
def cisco_int_desc_list(hostname,output_list,net_connect,devi_type):
    '''
    nxos format:Hostname,Port,Type,Speed,Description
    nxos format format :Hostname,Port/Interface,Description
    ios format: hostname,Interface,Status,Protocol Description
    ios format modified: Hostname,Port/Interface,Description
    '''
    ###get desc
    command_pass = 'sh int desc | egrep invert-match "Interface|Port|------------------"'
    output = net_connect.send_command(command_pass)
    #
    output_list_p1 = []
    output_list_p1 = output.split("\n")
    current_length_output_list = len(output_list)
    #print(lineno(),current_length_output_list)
    #
    for elem in output_list_p1:
        if elem != "":
            line = ",,"
            if devi_type == "cisco_nxos":
                if re.search("^Po|^mgmt0|^Vlan|^Lo", elem):
                    line = re.sub(r"[\s]+",",",elem,1)
                    line_list = line.split(",",1)
                    line = hostname + "," +  str(line_list[0]) + "," + str(line_list[-1])
                else:
                    line = re.sub(r"[\s]+",",",elem,3)
                    line_list = line.split(",",3)
                    line = hostname + "," +  str(line_list[0]) + "," + str(line_list[3])
            else:
                    line = re.sub(r"[\s]+",",",elem,3)
                    line_list = line.split(",",3)
                    line = hostname + "," +  str(line_list[0]) + "," + str(line_list[3])
            #print(lineno(),line)
            output_list.append(line)
    #
    #
    current_length_output_list_after_onedevice = len(output_list)
    no_of_entries_added = current_length_output_list_after_onedevice - current_length_output_list
    print (lineno(), "No of enties for current host:", str(command_pass), str(no_of_entries_added))
    return output_list
    
##
##
def processed_dict(show_int_status,show_int_desc,port_status_dict,port_desc_dict):
    # step1: create dict with hostname-Port as key and description as value for "sh int desc" output
    #
    for line in show_int_desc:
        print(lineno(), line)
        item = line.split(",")
        k = item[0] + "-" + item[1]
        v = item[2]
        port_desc_dict[k] = [v]
        #print(lineno(),str(k) + ":" + str(v))
    # step2: create dict with hostname-Port as key and all other fields as value as value for "sh int status" output
    #
    for line in show_int_status:
        item = line.split(",")
        k = item[0] + "-" + item[1]
        v = ",".join(item[2:])
        port_status_dict[k] = [v]
        #print(lineno(),str(k) + ":" + str(v))
##
def generate_op_list(show_int_status,port_desc_dict,curr_fut_sw_port,generated_list):
    for line in show_int_status:
        item = line.split(",")
        #key1 - hostname-interface
        k1 = str(item[0]) + "-" + str(item[1])
        #print(lineno(), k1)
        
        # get status string from dict
        int_desc_str = ""
        if k1 in port_desc_dict:
            int_desc_str = ",".join(map(str,port_desc_dict[k1]))
        else:
            int_desc_str = ""
        #print(lineno(), int_desc_str)
        # get desc string from dict
        # get current_sw and port from dict
        int_curr_sw_str = ""
        if k1 in curr_fut_sw_port:
            int_curr_sw_str  = ",".join(map(str,curr_fut_sw_port[k1]))
        else:
            int_curr_sw_str  = ",,"
        #print(lineno(), int_curr_sw_str)
        # get desc string from dict
        
        op = line + "," + str(int_desc_str) + "," +str(int_curr_sw_str)
        print(lineno(), op)
        generated_list.append(op)
##  
if __name__ == '__main__':
    
    now = datetime.now()
    formatnow = now.strftime("%Y-%m-%d-%H-%M-%S")
    csv_header = "Hostname,Port,Status,Vlan,Duplex,Speed,Type,Desc"

    scriptname = sys.argv[0]
    host_file_in = sys.argv[1]
    mapping_file_in = sys.argv[2]
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
    # Read input mapping file and create dictionary
    curr_fut_sw_port = {}
    portmappings(mapping_file_in,curr_fut_sw_port)
    
    ##  loop through hosts
    with open(host_file_in,"r") as host_file :
        ##cross linked and refered list and dicitionary
        port_desc_dict = {}
        port_status_dict = {}
        #
        generated_list = []
        #
        ##show commands individual lists
        show_int_desc =[]
        show_int_status = []
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
                ##get show op
                if devi_type == "cisco_nxos":
                    #
                    cisco_int_status_list(hostname,show_int_status,net_connect)
                    cisco_int_desc_list(hostname,show_int_desc,net_connect,devi_type)
                    #print(lineno(),hostname,"show_ip_stat",net_connect)
                else:
                    #
                    cisco_int_status_list(hostname,show_int_status,net_connect)
                    cisco_int_desc_list(hostname,show_int_desc,net_connect,devi_type)
                    #print(lineno(),hostname,"show_ip_stat",net_connect)
                
                print (lineno() , "No of enties are :" , len(show_int_status))
                #print(lineno(),"\n".join(map(str,show_int_status)))
                
            except NameError:
                print ("Error while login ", host)
            except:
                #Move on to the next switch 
                print ("Moving on to next switch in the list ...")
        print (lineno(), 'No. of entries  are :{} '.format(len(show_int_status)))
        #
        processed_dict(show_int_status,show_int_desc,port_status_dict,port_desc_dict)
        #
        generate_op_list(show_int_status,port_desc_dict,curr_fut_sw_port,generated_list)
        print (lineno(), 'No. of entries  are :{} '.format(len(generated_list)))
        with open(csv_file, 'a') as csv:
            csv.write("\n".join(map(str,generated_list)))
        