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
                #print(lineno(),line)
                output_list.append(line)
    #
    #
    current_length_output_list_after_onedevice = len(output_list)
    no_of_entries_added = current_length_output_list_after_onedevice - current_length_output_list
    print (lineno(), "No of enties for current host:", str(command_pass), str(no_of_entries_added))
    #return output_list
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
                #print(lineno(),line)
                output_list.append(line)
    #
    #
    current_length_output_list_after_onedevice = len(output_list)
    no_of_entries_added = current_length_output_list_after_onedevice - current_length_output_list
    print (lineno(), "No of enties for current host:", str(command_pass), str(no_of_entries_added))
    #return output_list
###
#### nxos int desc function
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
            elem = re.sub(r"admin down","admin_down",elem)
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
            line = re.sub(r"[\s]+",",",elem)
            line_list = line.split(",")
            line = hostname + "," +  str(line_list[0]) + "," + ",".join(map(str,line_list[-5:]))
            #print(lineno(), line)
            output_list.append(line)
    #
    #
    current_length_output_list_after_onedevice = len(output_list)
    no_of_entries_added = current_length_output_list_after_onedevice - current_length_output_list
    print (lineno(), "No of enties for current host:", str(command_pass), str(no_of_entries_added))
    #return output_list
    
##
def nxos_ip_arp_list(hostname,output_list,net_connect):
    '''
    nxos format:Hostname,Address,Age,MAC Address,Interface,Flags
    nxos format:Hostname,Address,Age,MAC_Address,Interface,Flags
    ios format: Hostname,Protocol,Address,Age(min),Hardware_Addr,Type,Interface 
    drop "protocol" and "Type". "Lags" has no value for ios
    ios format: Hostname,Address,Age,MAC_Address,Interface,Flags
    '''
    ###get desc
    command_pass = 'show ip arp vrf all | egrep ^[0-9]'
    output = net_connect.send_command(command_pass)
    #
    output_list_p1 = []
    output_list_p1 = output.split("\n")
    current_length_output_list = len(output_list)
    #print(lineno(),current_length_output_list)
    #
    for elem in output_list_p1:
        if elem != "":
            line = re.sub(r"[\s]+",",",elem)
            line_list = line.split(",")
            line = hostname + "," + ",".join(map(str,line_list[:5]))
            #print(line)
            output_list.append(line)
    #
    #
    current_length_output_list_after_onedevice = len(output_list)
    no_of_entries_added = current_length_output_list_after_onedevice - current_length_output_list
    print (lineno(), "No of enties for current host:", str(command_pass), str(no_of_entries_added))
    #return output_list
    
##
##
def ios_ip_arp_list(hostname,output_list,net_connect):
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
            if "__Platform_iVRF" in elem:
                pass
            elif elem!="":
                vrf_name = re.sub(r"[\s]+",",",elem)
                #print(vrf_name + "\n")
                vrf_name_elem = vrf_name.split(",")[1]
                #print(vrf_name_elem + "\n")
                vrf_list.append(vrf_name_elem)
    print(lineno(), "vrf list is : ",  vrf_list)
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
        if elem != "":
            line = re.sub(r"[\s]+",",",elem)
            line_list = line.split(",")
            line = hostname + "," + ",".join(map(str,line_list[1:4])) + "," + str(line_list[-1])
            #print(line)
            output_list.append(line)
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
                if elem != "":
                    line = re.sub(r"[\s]+",",",elem)
                    line_list = line.split(",")
                    line = hostname + "," + ",".join(map(str,line_list[1:4])) + "," + str(line_list[-1])
                    #print(line)
                    output_list.append(line)
       
            
    #
    current_length_output_list_after_onedevice = len(output_list)
    no_of_entries_added = current_length_output_list_after_onedevice - current_length_output_list
    print (lineno(), "No of enties for current host (including global/vrf) :", str(command_pass), str(no_of_entries_added))
    #return output_list
    
##
def processed_dict(show_op_mac,show_int_desc,show_int_status,show_ip_arp,port_desc_dict,port_status_dict,port_mac_dict,port_arp_dict):
    # step1: create dict with hostname-Port as key and description as value for "sh int desc" output
    #
    for line in show_int_desc:
        #print(lineno(),line)
        item = line.split(",")
        k = item[0] + "-" + item[1]
        v = item[2]
        port_desc_dict[k] = [v]
        #print(lineno(),str(k) + ":" + str(v))
    # step2: create dict with hostname-Port as key and all other fields as value as value for "sh int status" output
    #
    for line in show_int_status:
        #print(lineno(),line)
        item = line.split(",")
        k = item[0] + "-" + item[1]
        v = ",".join(item[-5:])
        port_status_dict[k] = [v]
        #print(lineno(),str(k) + ":" + str(v))
    # step3: create dict with hostname-mac-Port as key and all other fields as value as value for "sh mac address" output
    #
    for line in show_op_mac:
        item = line.split(",")
        k = str(item[0]) + "-" + str(item[3]) + "-" + str(item[9])
        v = ",".join(item[2:])
        port_mac_dict[k] = [v]
        #print(lineno(),str(k) + ":" + str(v))
    # step4: create dict with mac-Port as key and  value  as IP_addr ( ip address is list and can have muliple values)for "sh ip arp" output
    #
    local_list = []
    for line in show_ip_arp:
        #print(lineno(), line )
        line = re.sub(r"port-channel","Po",line)
        line = re.sub(r"Vlan","",line)
        line = re.sub(r"TenGigabitEthernet","Te",line)
        line = re.sub(r"GigabitEthernet","Gi",line)
        line = re.sub(r"Ethernet","Eth",line)
        item = line.split(",")
        k1 = item[3] + "-" + item[4]
        # create list of all keys with value as empty list
        port_arp_dict[k1] = []
        #print(lineno(),str(k1) )
        v1 = item[1]
        local_list.append(k1 + "," + v1)
        #print(lineno(),str(k1)+ "," + v1 )
    #
    '''
    for k, v in port_arp_dict.items():
        print(lineno(), k , ":" , v)
    '''
    for elem in local_list:
        elem = elem.split(",")
        k = elem[0]
        v = elem[1]
        #print(lineno(), k , v)
        port_arp_dict[k].append(v)
        #print(lineno(),str(k) + ":" + v)
    '''
    for k, v in port_arp_dict.items():
        print(lineno(), k , ":" , v)
    '''

def generate_op_list(show_op_mac,port_desc_dict,port_status_dict,port_mac_dict,port_arp_dict,generated_list):
    for line in show_op_mac:
        item = line.split(",")
        #key1 - hostname-interface
        k1 = str(item[0]) + "-" + str(item[9])
        #print(lineno(), k1)
        #key 2 - mac-vlan
        k2 = str(item[3]) + "-" + str(item[2])
        #print(lineno(), k2)
        # get status string from dict
        int_status_str = ""
        if k1 in port_status_dict:
            int_status_str = ",".join(map(str,port_status_dict[k1]))
        else:
            int_status_str = ",,,,"
        #print(lineno(), int_status_str)
        # get desc string from dict
        int_desc_str = ""
        if k1 in port_desc_dict:
            int_desc_str = ",".join(map(str,port_desc_dict[k1]))
        else:
            int_desc_str = ","
        #print(lineno(), int_desc_str)
        # get ip used by mac
        ip_str = ""
        if k2 in port_arp_dict:
            ip_str = ",".join(map(str,port_arp_dict[k2]))
        else:
            ip_str = ","
        op = line + "," +  int_status_str + "," + int_desc_str + "," + ip_str
        #print(lineno(), op)
        generated_list.append(op)
        
    
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
        port_mac_dict = {}
        port_arp_dict = {}
        #
        generated_list = []
        #
        ##show commands individual lists
        show_op_mac=[]
        show_int_desc =[]
        show_int_status = []
        show_ip_arp = []
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
                ##
                if devi_type == "cisco_nxos":
                    nxos_mac_list(hostname,show_op_mac,net_connect)
                    print(lineno())
                    nxos_int_desc_list(hostname,show_int_desc,net_connect,devi_type)
                    print(lineno())
                    nxos_int_status_list(hostname,show_int_status,net_connect)
                    print(lineno())
                    nxos_ip_arp_list(hostname,show_ip_arp,net_connect)
                    print(lineno())
                else:
                    ios_mac_list(hostname,show_op_mac,net_connect)
                    print(lineno())
                    ios_int_desc_list(hostname,show_int_desc,net_connect,devi_type)
                    print(lineno())
                    ios_int_status_list(hostname,show_int_status,net_connect)
                    print(lineno())
                    ios_ip_arp_list(hostname,show_ip_arp,net_connect)
                    print(lineno())
                #print(hostname)
                #print (lineno() , "No of enties for mac_list :" , len(show_op_mac))
                #print(lineno(),"\n".join(map(str,show_op_mac)))
                ##
                #print(lineno(),"\n".join(map(str,show_int_desc)))
                
                #
                '''
                for elem in [port_desc_dict,port_status_dict,port_mac_dict,port_arp_dict]:
                    for k, v in port_desc_dict.items():
                        print(lineno(),k,v)
                #
                '''
    
                
            except NameError:
                print ("Error while login ", host)
            except:
                #Move on to the next switch 
                print ("Moving on to next switch in the list ...")
        #print("\n".join(map(str,show_int_desc)))
        processed_dict(show_op_mac,show_int_desc,show_int_status,show_ip_arp,port_desc_dict,port_status_dict,port_mac_dict,port_arp_dict)
        
        generate_op_list(show_op_mac,port_desc_dict,port_status_dict,port_mac_dict,port_arp_dict,generated_list)
        
        with open(csv_file, 'a') as csv:
            csv.write("\n".join(map(str,generated_list)))
        '''
        with open(csv_file, 'a') as csv:
            csv.write("\n".join(map(str,show_op_mac)))
            csv.write("\n".join(map(str,show_int_desc)))
            csv.write("\n".join(map(str,show_int_status)))
            csv.write("\n".join(map(str,show_ip_arp)))
        '''
    