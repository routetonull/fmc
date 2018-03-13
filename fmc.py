import json
import requests
#Surpress HTTPS insecure errors for cleaner output
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
'''
Author: Gian Paolo Boarina - www.ifconfifg.it
Original repository: https://github.com/routetonull/fmc
License: CC BY-SA 4.0 https://creativecommons.org/licenses/by-sa/4.0/

TO DO
use dict.get()
https://docs.quantifiedcode.com/python-anti-patterns/correctness/not_using_get_to_return_a_default_value_from_a_dictionary.html
'''

class Fmc(object):

    def __init__(self,host,username,password):
        self.host = host 
        self.username = username   
        self.password = password
        self.server = "https://"+self.host
        self.base_api_path = "/api/fmc_config/v1/domain/"
        self.result = 0

    #connect to the FMC API and generate authentication token
    def connect (self):
        '''
        connects to FMC
        '''
        headers = {'Content-Type': 'application/json'}
        path = "/api/fmc_platform/v1/auth/generatetoken"
        server = "https://"+ self.host
        url = self.server + path
        result = 1
        try:
                r = requests.post(url, headers=headers, auth=requests.auth.HTTPBasicAuth(self.username,self.password), verify=False)
                auth_headers = r.headers
                token = auth_headers.get('X-auth-access-token', default=None)
                uuid = auth_headers.get('DOMAIN_UUID', default=None)
                if token == None:
                        result = "No Token found, I'll be back terminating...."
        except Exception as err:
                result = "Error in generating token --> "+ str(err)
                #sys.exit()
        headers['X-auth-access-token'] = token
        self.headers = headers
        self.uuid = uuid  
        return result
        #return headers,uuid,server

    def fmcPOST (self,api_path,post_data):
        '''
        generic POST
        '''
        api_path= self.base_api_path + self.uuid + api_path
        url = self.server+api_path
        try:
            r = requests.post(url, data=json.dumps(post_data), headers=self.headers, verify=False)
            status_code = r.status_code
            resp = r.text
            json_response = json.loads(resp)
            print("status code is: "+ str(status_code))
            if status_code == 201 or status_code == 202:
                    print("Post was sucessfull...")
            else:
                    r.raise_for_status()
                    print("error occured in POST -->"+resp)
        except requests.exceptions.HTTPError as err:
                print ("Error in connection --> "+str(err))
        finally:
                if r: r.close()
        self.result = json_response
        return json_response

    def fmcPUT (self,api_path,post_data):
        '''
        generic PUT - to be tested
        '''
        api_path= self.base_api_path + self.uuid + api_path
        url = self.server+api_path
        try:
            r = requests.put(url, data=json.dumps(post_data), headers=self.headers, verify=False)
            status_code = r.status_code
            resp = r.text
            json_response = json.loads(resp)
            print("status code is: "+ str(status_code))
            if status_code == 200 or status_code == 204:
                    print("Put was sucessfull...")
            else:
                    r.raise_for_status()
                    print("error occured in POST -->"+resp)
        except requests.exceptions.HTTPError as err:
                print ("Error in connection --> "+str(err))
        finally:
                if r: r.close()
        self.result = json_response
        return json_response

    def fmcGET (self, get_path):
        '''
        generic GET
        '''
        api_path= self.base_api_path + self.uuid + get_path
        url = self.server+api_path
        try:
            r = requests.get(url, headers=self.headers, verify=False)
            status_code = r.status_code
            resp = r.text
            json_response = json.loads(resp)
            #print("status code is: "+ str(status_code))
            if status_code == 200:
                    result = 1
                    #print("GET was sucessfull...")
            else:
                    r.raise_for_status()
                    #print("error occured in POST -->"+resp)
        except requests.exceptions.HTTPError as err:
                result = 0
                #print ("Error in connection --> "+str(err))
        finally:
                if r: r.close()
        self.result = json_response
        return json_response

    def fmcDELETE (self, get_path):
        api_path= self.base_api_path + self.uuid + get_path
        url = self.server+api_path
        try:
            r = requests.delete(url, headers=self.headers, verify=False)
            status_code = r.status_code
            resp = r.text
            json_response = json.loads(resp)
            #print("status code is: "+ str(status_code))
            if status_code == 200:
                    result = 1
                    #print("DELETE was sucessfull...")
            else:
                    r.raise_for_status()
                    #print("error occured in POST -->"+resp)
        except requests.exceptions.HTTPError as err:
                result = 0
                #print ("Error in connection --> "+str(err))
        finally:
                if r: r.close()
        self.result = json_response
        return json_response

    def addHost(self,name,ip,description='host object'):
        '''
        add host object
        '''
        if not self.findHost(name):
            post_data = {"name": name,"type": "Host","value": ip,"description": description}
            self.fmcPOST('/object/hosts',post_data)
            return 0
        else:
            return 1

    def delHost(self,objectID):
        '''
        delete host by objectID
        '''
        self.fmcDELETE('/object/hosts/'+objectID)
    
    def getHost(self,objectID):
        '''
        get host informtion by ojbectID
        '''
        return self.fmcGET('/object/hosts/'+objectID)

    def addNetwork(self,name,ip,description='host object'):
        '''
        create new network object
        ip format is: 10.0.0.1/24
        '''
        if not self.findHost(name):
            post_data = {
                "name": name,
                "type": "Network",
                "value": ip,
                "description": description
            }
            self.fmcPOST('/object/networks',post_data)
            return 0
        else:
            return 1

    def addNetworkGroup(self,name,members,description=''):
        '''
        create new network group
        member list cannot be empty
        '''
        toAdd=members
        members=[]
        for element in toAdd:
            isHost = self.findHost(element)    
            if isHost:
                members.append({'type':'Host','id':isHost[0]['id']})
            else:
                isNetwork = self.findNetwork(element)
                if isNetwork:
                    members.append({'type':'Network','id':isNetwork[0]['id']})
        post_data = {
            "name": name,
            "objects" : members,
            "type": "NetworkGroup",
        }
        group = self.findNetworkGroups(name)
        if self.findNetworkGroups(name):
            post_data['id']= group[0]['id']
            self.fmcPUT('/object/networkgroups/'+group[0]['id'],post_data)
        else:
            post_data['description']= description
            self.fmcPOST('/object/networkgroups',post_data)

    def getNetwork(self,objectID):
        '''
        get network by objectID
        '''
        return self.fmcGET('/object/networks/'+objectID)

    def delNetwork(self,objectID):
        '''
        delete network by objectID
        '''
        self.fmcDELETE('/object/networks/'+objectID)

    def getAllObjects(self,path):
        '''
        get list of all objects
        '''
        limit=100
        offset=0
        step=100
        result=[]
        objectsToRead = self.fmcGET(path+'?limit='+str(limit)+'&offset='+str(offset))
        while 'items' in objectsToRead:
            result.extend(objectsToRead['items'])
            offset+=step
            readpath=path+'?limit='+str(limit)+'&offset='+str(offset)
            objectsToRead = self.fmcGET(readpath)        
        return result

    def findObject(self,path,name):
        '''
        find object by name
        not to be used directly
        '''
        objects = self.getAllObjects(path)
        return list(filter(lambda o : o['name'] == name,objects))

    def findNetwork(self,name):
        '''
        find network by name
        '''
        return self.findObject('/object/networks',name)
        
    def findHost(self,name):
        '''
        find host by name
        '''
        return self.findObject('/object/hosts',name)

    def findNetworkGroups(self,name):
        '''
        find network group by name
        '''
        return self.findObject('/object/networkgroups',name)

    def showNetworkGroups(self,name=''):
        '''
        show network group by name
        '''
        if name:
           return self.findNetworkGroups(name)
        return self.getAllObjects('/object/networkgroups')

    def showNetworkGroupsMembers(self,name):
        '''
        show network group members
        '''
        group = self.findObject('/object/networkgroups',name)
        if 'name' in group[0]:
            id = group[0]['id']
            members = self.fmcGET('/object/networkgroups/'+id)
            return members['objects']
        return 0

    def showHosts(self,name=''):
        '''
        show host by name
        '''
        if name:
           return self.findHost(name)
        return self.getAllObjects('/object/hosts')

    def showNetworks(self,name=''):
        '''
        show network object by name
        '''
        if name:
           return self.findNetwork(name)
        return self.getAllObjects('/object/networks')

    def findHostNetwork(self,name):
        '''
        find object type host or network
        '''
        result = self.findObject('/object/hosts',name)
        if not result:
            result = self.findObject('/object/networks',name)
        return result

    def deployableDevices(self):
        path= "/deployment/deployabledevices"
        result=self.fmcGET(path)
        if 'items' in result:
            return result['items']
        return {}

    def deviceRecords(self):
        path= "/devices/devicerecords"
        result=[]
        devices=self.fmcGET(path)
        if 'items' in devices:
            for device in devices['items']:
                result.append(device['id'])
        return result

    def deploymentRequests(self):
        '''
        creates a deployment request i.e. only a message on FMC
        '''
        path='/deployment/deploymentrequests'
        post_data = {
            "type": "DeploymentRequest",
            "forceDeploy": True,
            "ignoreWarning": True,
            "version": str(int(time.time())),
            "deviceList": self.deviceRecords()
        }
        self.fmcPOST(path,post_data)
        return 0