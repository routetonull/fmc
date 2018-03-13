#!/usr/bin/python3
import textfsm
import fmc
import ipaddress
import re
import getpass

templatefilename = input("textfsm template:\t")
template = open(templatefilename, 'r')

asaconfigfilename = input("asa config:\t")
filetoread = open(asaconfigfilename,'r')
text = filetoread.read()

re_table = textfsm.TextFSM(template)
data = re_table.ParseText(text)

# connect to FCM
#reload(fmc)
ip = input("FMC IP:\t")
user = input("FMC username:\t")
password = getpass.getpass("FMC password:\t")
f = fmc.Fmc(ip,user,password)
print ("CONNECTING TO FMC...")
f.connect()

print ("ADDING OBJECTS...")
h = 0
n = 0
for d in data:
    # if it is an host use /32 subnet
    if d[0] == 'network' and d[2]:
        print ("ADD HOST\t"+str(d))
        f.addHost(d[1],d[2],d[5])
        h+=1
    if d[0] == 'network' and d[3]:
        print ("ADD NETWORK\t"+str(d))
        # convert to prefixlen - fmc does not support subnet mask
        network=ipaddress.IPv4Network(re.sub("\s","/",d[3])).with_prefixlen
        f.addNetwork(d[1],network,d[5])
        n+=1
print ("TOTAL HOSTS\t"+str(h))
print ("TOTAL NETWORKS\t"+str(n))
print ("TOTAL OBJECTS\t"+str(h+n))

# textfsm template header
# ['type', 'name', 'host', 'subnet', 'service', 'description']