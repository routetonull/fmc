#!/usr/bin/python3

'''
Author: Gian Paolo Boarina (gp DOT boarina AT gmail DOT com)
Website: https://www.ifconfig.it
License: CC BY-SA https://creativecommons.org/licenses/by-sa/4.0/
DISCLAIMER: use at your own risk, author takes no responsibility of any damage caused by the script

The script converts network objects from CISCO ASA to FORTINET FORTIGATE.

Template filename is: asa_object_textfsm_template

ASA config file must be provided.

'''

import textfsm
import ipaddress
import re
import getpass

print("*"*60)
print("*   CONVERT OBJECTS FROM ASA TO FORTIGATE")
print("*"*60)

templatefilename = "asa_object_textfsm_template"
template = open(templatefilename, 'r')

asaconfigfilename = input("asa config:\t")
filetoread = open(asaconfigfilename,'r')
text = filetoread.read()

re_table = textfsm.TextFSM(template)
data = re_table.ParseText(text)

print ("*   READING OBJECTS...")
h = 0
n = 0
for d in data:
    # if it is an host use /32 subnet
    subnet = ''
    #print(d)
    if d[0] == 'network' and d[2]:
        subnet = '255.255.255.255'
        h+=1
        print("edit \"{}\"\nset subnet {} {}\nnext".format(d[1].strip(),d[2],subnet))
    if d[0] == 'network' and d[3]:
        network=ipaddress.IPv4Network(re.sub("\s","/",d[3])).with_prefixlen
        n+=1
        print("edit \"{}\"\nset subnet {} {}\nnext".format(d[1].strip(),d[3],subnet))
    
print("*"*60)
print ("*   TOTAL HOSTS\t"+str(h))
print ("*   TOTAL NETWORKS\t"+str(n))
print ("*   TOTAL OBJECTS\t"+str(h+n))
print("*"*60)