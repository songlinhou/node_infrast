import requests
import json
import os

#appId = "S5KA3LxWxrgyz0VN6ghbAHXV-gzGzoHsz"
#key = "nRjAAmtjBPlswOwtXwUdxy0x"

#mail login

#"lean_app_id": "S5KA3LxWxrgyz0VN6ghbAHXV-gzGzoHsz",
#"lean_pwd": "nRjAAmtjBPlswOwtXwUdxy0x"


class LeanCloud:
  def __init__(self):
    file_path = os.path.dirname(os.path.realpath(__file__))
    credential_path = os.path.join(file_path,'credential.json')
    with open(credential_path) as credential:
      lean_info = json.load(credential)
      self.appId = lean_info['lean_app_id']
      self.key = lean_info['lean_pwd']

  def lean_cloud_get(self,route):
    request_url = 'https://' + self.appId[0:8] +'.api.lncld.net/1.1' + route
    headers = {'X-LC-Id':self.appId,'X-LC-Key':self.key,"Content-Type":"text/plain;charset=UTF-8"}
    s = requests.Session()
    r = s.get(request_url,headers=headers)
    print '[GET]'+request_url
    return r

  def lean_cloud_post(self,route,data):
    request_url = 'https://' + self.appId[0:8] +'.api.lncld.net/1.1' + route
    s = requests.Session()
    headers = {'X-LC-Id':self.appId,'X-LC-Key':self.key,"Content-Type":"application/json;charset=UTF-8"}
    r = s.post(request_url,data=json.dumps(data),headers=headers)
    return r

  def lean_cloud_put(self,class_name,objectId,data):
    route = class_name + "/" + objectId
    request_url = 'https://' + self.appId[0:8] +'.api.lncld.net/1.1/classes/' + route 
    s = requests.Session()
    headers = {'X-LC-Id':self.appId,'X-LC-Key':self.key,"Content-Type":"application/json;charset=UTF-8"}
    r = s.post(request_url,data=json.dumps(data),headers=headers)
    return r

  def lean_cloud_delete(self,class_name,objectId):
    request_url = 'https://' + self.appId[0:8] +'.api.lncld.net/1.1/classes/' + class_name + '/' + objectId
    s = requests.Session()
    headers = {'X-LC-Id':self.appId,'X-LC-Key':self.key,"Content-Type":"application/json;charset=UTF-8"}
    r = s.delete(request_url,headers=headers)
    return r


