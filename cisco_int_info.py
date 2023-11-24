###  SYNTAX:  python scriptname.py host_filename
## combine info from mac, arp , desc and status outputs 
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

def nxos_int_desc_list(hostname,output_list,net_connect,devi_type):
    '''
    nxos format:Hostname,Port,Type,Speed,Description
    nxos format format :Hostname,Port/Interface,Description
    ios format: hostname,Interface,Status,Protocol Description
    ios format modified: Hostname,Port/Interface,Description
    '''
    ###get desc
    command_pass = 'sh int desc | egrep invert-match "Interface|Port|------------------"'
    output = net_connect.send_command(command_pass)
    #print(lineno(), output)
    #
    output_list_p1 = []
    output_list_p1 = output.split("\n")
    current_length_output_list = len(output_list)
    #print(lineno(),current_length_output_list)
    #print(lineno(), len(output_list_p1))
    
    #
    for elem in output_list_p1:
        #print(lineno(), elem)
        if elem != "":
            line = ",,"
            if devi_type == "cisco_nxos":
                if re.search("^Po|^mgmt0|^Vlan|^Lo|^fc|^san", elem):
                    line = re.sub(r"[\s]+",",",elem,1)
                    line_list = line.split(",",1)
                    line = hostname + "," +  str(line_list[0]) + "," + str(line_list[-1])
                    #print(lineno(),line)
                else:
                    line = re.sub(r"[\s]+",",",elem,3)
                    line_list = line.split(",",3)
                    line = hostname + "," +  str(line_list[0]) + "," + str(line_list[3])
                    #print(lineno(),line)
            else:
                    line = re.sub(r"[\s]+",",",elem,3)
                    line_list = line.split(",",3)
                    line = hostname + "," +  str(line_list[0]) + "," + str(line_list[3])
                    #print(lineno(),line)
            #print(lineno(),line)
            output_list.append(line)
    #
    #
    current_length_output_list_after_onedevice = len(output_list)
    no_of_entries_added = current_length_output_list_after_onedevice - current_length_output_list
    print (lineno(), "No of enties for current host:", str(command_pass), str(no_of_entries_added))
    #return output_list
    
##
#### nxos int desc function
def ios_int_desc_list(hostname,output_list,net_connect,devi_type):
    '''
    nxos format:Hostname,Port,Type,Speed,Description
    nxos format format :Hostname,Port/Interface,Description
    ios format: hostname,Interface,Status,Protocol Description
    ios format modified: Hostname,Port/Interface,Description
    '''
    ###get desc
    command_pass = 'sh int desc | ex "Interface|Port|------------------"'
    output = net_connect.send_command(command_pass)
    #print(lineno(), output)
    #
    output_list_p1 = []
    output_list_p1 = output.split("\n")
    current_length_output_list = len(output_list)
    #print(lineno(),current_length_output_list)
    #print(lineno(), len(output_list_p1))
    
    #
    for elem in output_list_p1:
        #print(lineno(), elem)
        if elem != "":
            line = ",,"
            if devi_type == "cisco_nxos":
                if re.search("^Po|^mgmt0|^Vlan|^Lo", elem):
                    line = re.sub(r"[\s]+",",",elem,1)
                    line_list = line.split(",",1)
                    line = hostname + "," +  str(line_list[0]) + "," + str(line_list[-1])
                    #print(lineno(),line)
                else:
                    line = re.sub(r"[\s]+",",",elem,3)
                    line_list = line.split(",",3)
                    line = hostname + "," +  str(line_list[0]) + "," + str(line_list[3])
                    #print(lineno(),line)
            else:
                    line = re.sub(r"[\s]+",",",elem,3)
                    line_list = line.split(",",3)
                    line = hostname + "," +  str(line_list[0]) + "," + str(line_list[3])
                    #print(lineno(),line)
            #print(lineno(),line)
            output_list.append(line)
    #
    #
    current_length_output_list_after_onedevice = len(output_list)
    no_of_entries_added = current_length_output_list_after_onedevice - current_length_output_list
    print (lineno(), "No of enties for current host:", str(command_pass), str(no_of_entries_added))
    #return output_list
    
##
def nxos_int_status_list(hostname,output_list,net_connect):
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
##
def ios_int_status_list(hostname,output_list,net_connect):
    '''
    name dropped as it is not full and truncated
    nxos format:Hostname,Port,Name,Status,Vlan,Duplex,Speed,Type
    nxos format:Hostname,Port,Status,Vlan,Duplex,Speed,Type
    ios format: Hostname,Port,Name,Status,Vlan,Duplex,Speed,Type
    ios format: Hostname,Port,Status,Vlan,Duplex,Speed,Type
    '''
    ###get desc
    command_pass = 'sh int status | ex "Interface|Port|------------------"'
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
    
if __name__ == '__main__':
    
    now = datetime.now()
    formatnow = now.strftime("%Y-%m-%d-%H-%M-%S")
    csv_header = "hostname,Space,vlan,mac-address,type,learn,age,Secure,NTFY,ports,Status,Vlan,Duplex,Speed,Type,Description,IP"

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
        
        ##cross linked and refered list and dicitionary
        port_desc_dict = {}
        port_status_dict = {}
        
        #
        
        #
        ##show commands individual lists
        
        show_int_desc =[]
        show_int_status = []
        
        #
        for host in host_file:
            try:
                host = host.strip()
                host = host.split(",")[0]
                print(lineno() , host)
                
                net_connect = ConnectHandler(device_type='cisco_ios',ip=host,username=username,password=password)
                prompt = net_connect.find_prompt()
                #print(lineno() ,prompt)
                hostname = prompt.split("#")[0]
                #print(lineno() ,hostname)
                
                devi_type=dev_type(net_connect)
                print(lineno(), hostname,devi_type)
                #
                net_connect = ConnectHandler(device_type=devi_type,ip=host,username=username,password=password)
                prompt = net_connect.find_prompt()
                hostname = prompt.split("#")[0]
                ##get mac table
                if devi_type == "cisco_nxos":
                    
                    nxos_int_desc_list(hostname,show_int_desc,net_connect,devi_type)
                    print(lineno())
                    nxos_int_status_list(hostname,show_int_status,net_connect)
                    print(lineno())
                    
                else:
                    
                    ios_int_desc_list(hostname,show_int_desc,net_connect,devi_type)
                    print(lineno())
                    ios_int_status_list(hostname,show_int_status,net_connect)
                    print(lineno())
                    
                #print(hostname)
                #print (lineno() , "No of enties for mac_list :" , len(show_int_status))
                
                
            except NameError:
                print ("Error while login ", host)
            except:
                #Move on to the next switch 
                print ("Moving on to next switch in the list ...")
        
        with open(csv_file, 'a') as csv:
            csv.write("\n".join(map(str,show_int_desc)))
            csv.write("\n")
            csv.write("\n".join(map(str,show_int_status)))
            
        
    