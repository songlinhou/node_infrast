from storage.lean_cloud import LeanCloud
import json

baseURL = '/classes/Experiments'
cloud = LeanCloud()

def add_expID(ID,user,comment,new=False):
  data = {'ID':ID,'user':user,'comment':comment}
  if not new:
    objectId = find_exp(ID,user)
    if objectId:
      print 'duplicated exp found. this exp won\'t be added to central server'
      return
  resp = cloud.lean_cloud_post(baseURL,data)
  if resp.ok:
    print 'expID added to central node successfully'
  else:
    print 'failed to add expID to central node'

def modify_exp(expID,user,newID,newUser,newComment):
  objectId = find_exp(expID,user)
  data = {}
  if newID:
    data['ID'] = newID
  if newUser:
    data['user'] = newUser
  if newComment:
    data['comment'] = newComment
  if data == {}:
    return 'no argument is passed'
  if objectId:
    resp = cloud.lean_cloud_put('Experiments',objectId,data)
    if resp.ok:
      print 'exp modified'
    else:
      print 'exp not modified'
  else:
    print 'cannot find the exp'
  


def get_all_exp(user):
  url = baseURL
  if user:
    url += ('?where=' + json.dumps({'user':user}))
  resp = cloud.lean_cloud_get(url)
  exp_info = (resp.json())['results']
  ID_list = []
  comment_list = []
  for exp_data in exp_info:
    ID_list.append(exp_data['ID'])
    comment_list.append(exp_data['comment'])

  return ID_list,comment_list


def find_exp(expID,user):
  _url = baseURL
  _url = _url + ('?where=' + json.dumps({'ID':expID,'user':user}))
  resp = cloud.lean_cloud_get(_url)
  print '_url=',_url
  resp_data = resp.json()
  print 'resp_data=',resp_data
  if 'results' not in resp_data.keys():
    print 'no exp is found'
    return None
  exp_info = (resp.json())['results']
  objectId = None
  if len(exp_info) >= 1:
    objectId = exp_info[0]['objectId']
    print 'objectId',objectId
    return objectId
  else:
    print 'no exp is found'
    return None
  
  
def delete_exp(expID,user):
  objectId = find_exp(expID,user)
  if objectId:
    resp = cloud.lean_cloud_delete('Experiments',objectId)
    return resp
  else:
    print 'exp {} by {} not found'.format(expID,user)