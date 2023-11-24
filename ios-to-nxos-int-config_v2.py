###  SYNTAX:  python scriptname.py inputfilename mappinginputfile keeplinesfile
from time import sleep
from datetime import datetime
import re
import sys
import inspect

now = datetime.now()
formatnow = now.strftime("%Y-%m-%d-%H-%M")

scriptname = sys.argv[0]
input_file = sys.argv[1]
#csv file for interface mappings
mapping_file = sys.argv[2]
###Line Number function
def lineno():
    '''Returns line number in program'''
    return inspect.currentframe().f_back.f_lineno

###
#print(lineno())
#### Custom create directory function
  
import os  
def dir_create(path): 
    # path  
    try:  
        os.mkdir(path)  
    except OSError as error:  
        print(error) 
####
log_dir = scriptname + "-" + formatnow
log_dir = re.sub(r"\|/","",log_dir)
dir_create(log_dir)
print(lineno() , ": " , "Log Directory name is :", log_dir)

###

c_switch  = ""
with open(input_file,"r") as f:
    for line in f:
        if re.search("hostname", line):
            c_switch = line.split(" ")[1]
            c_switch = c_switch.strip()
            print(str(lineno()) + ":" + c_switch)
            break
        else:
            continue
f.close()        
###



###
keep_line_file = sys.argv[3]
#Covert keep_lines file to list

keep_line_list = []
with open(keep_line_file,"r") as f:
    for line in f:
        line = line.strip()
        keep_line_list.append(line)
#print(keep_line_list)
###
def lineno():
    '''Returns line number in program'''
    return inspect.currentframe().f_back.f_lineno



###bring input file to list

input_file_list = []
with open(input_file,"r") as f:
    for line in f:
        line = line.strip()
        input_file_list.append(line)
###
#First pass to cleanup
input_file_list_pass1 = []
for line in input_file_list:
    for pattern in keep_line_list:
        if re.search(pattern, line):
            if re.search("switchport port-security", line):
                continue
            else:
                #print(line)
                input_file_list_pass1.append(line) 
            break
        else:
            #print("next line ")
            continue

print("first pass done" + "\r\n")
#2nd pass to cleanup
input_file_list_pass2 =[]
#loop through file replace interface names with short name e.g.Gix/x
for line in input_file_list_pass1:
    line = re.sub(r"interface GigabitEthernet","int Gi",line)
    line = re.sub(r"interface TenGigabitEthernet","int Te",line)
    line = re.sub(r"interface Port-channel","int Po",line)
    line = re.sub(r"switchport capture","#switchport capture",line)
    line = re.sub(r"switchport nonegotiate","#switchport nonegotiate",line)
    line = re.sub(r"switchport trunk encapsulation dot1q","#switchport trunk encapsulation dot1q",line)
    #print(line)
    input_file_list_pass2.append(line)
    
print("2nd pass done")
#3rd Pass per interface
input_file_list_pass3 =[]

str_input_file_list_pass2 = ""
s = "-;;;-"
str_input_file_list_pass2 = s.join(input_file_list_pass2)
#print(str_input_file_list_pass2)

input_file_list_pass3 = str_input_file_list_pass2.split("!")
#print(input_file_list_pass3)
int_dict = {}

for line in input_file_list_pass3:
    if re.search("^-;;;-int ", line):
        line = re.sub(r"-;;;-int ","int ",line)
        #print(line)
        line_list = line.split("-;;;-")
        k = line_list[0]
        u = line_list[1:]
        v = "\n" + "\n".join(u)
    
        #print(k)
        #print(v)
        int_dict[k] = [v]
        
        #
    else:
        continue
    
#print(int_dict)
print("3rd pass done")
#process mappimg file to get op switch and port info
future_switch_list = []
map_dict = {}
with open(mapping_file,"r") as f:
    for line in f:
        line = line.strip()
        Current_Switch = line.split(",")[0]
        Current_Port = line.split(",")[1]
        Future_Switch = line.split(",")[2]
        Future_Port = line.split(",")[3]
        k = Current_Switch + " int " + Current_Port
        v = Future_Switch + "," + "int " + Future_Port
        future_switch_list.append(Future_Switch)
        #print("key is : " + k)
        #print("value is " + v)
        map_dict[k] = [v]
        
#print(map_dict)
   
###

#Output configs


for k,v in int_dict.items():
    check_k = c_switch + " " + k
    
    #print(check_k)
    if check_k in map_dict:
        f_switch_a_port = map_dict[check_k]
        #print(f_switch_a_port)
        f_switch = f_switch_a_port[0].split(",")[0]
        f_port = f_switch_a_port[0].split(",")[1]
        #print("current switch is :" + c_switch + " Future Switch is : " + f_switch)
        #print("current port is :" + k + " Future Switch is : " + f_port)
        #print(f_port)
        sw_config = "".join(v)
        sw_config = re.sub(r"\-;;;-", "\r\n" , sw_config)
        #print(sw_config)
        sw = f_switch
        with open(log_dir + "/" + c_switch + "-" + f_switch + "-" + formatnow  + ".txt", 'a') as swtxt:
            swtxt.write(f_port)
            swtxt.write(sw_config)
        
    else:
        #print("key not present")
        f_switch = "OTHER"
        f_switch_a_port = k
        #print(f_switch)
        #print(f_switch_a_port)
        
        sw_config = "".join(v)
        sw_config = re.sub(r"\-;;;-", "\r\n" , sw_config)
        #print(sw_config)
       
        with open(log_dir + "/" + c_switch + "-" + f_switch + "-" + formatnow  + ".txt", 'a') as swtxt:
            swtxt.write(f_switch_a_port)
            swtxt.write(sw_config)