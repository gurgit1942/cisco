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