from storage.lean_cloud import LeanCloud
import json



cloud = LeanCloud()

def add_peer(peerName,url,experimentId,owner='global',note=None,new=False):
  data = {'peerName':peerName,'url':url,'experimentId':experimentId,"note":note}
  if not new:
    peerObj = find_peer(peerName,experimentId)
    if peerObj:
      objectId = peerObj['objectId']
      if objectId:
        print 'duplicated peer found. peer won\'t be added to central server'
        return True
  resp = cloud.lean_cloud_post("/classes/PeerTable",data)
  if resp.ok:
    print 'peer added to central node successfully'
    return True
  else:
    print 'failed to add peer to central node'
    return False

def modify_peer_url(peerName,url,experimentId,owner='global'):
  peerObj = find_peer(peerName,experimentId,owner)
  objectId = peerObj['objectId']
  data = {'url':url}
  if objectId:
    resp = cloud.lean_cloud_put('PeerTable',objectId,data)
    if resp.ok:
      print 'previous peer url modified'
    else:
      print 'previous peer url not modified'
  


def get_all_peers(experimentId,current_node_id,owner='global'):
  url = "/classes/PeerTable"
  url += ('?where=' + json.dumps({'experimentId':experimentId,'owner':owner}))
  resp = cloud.lean_cloud_get(url)
  resp_data = resp.json()
  if 'results' not in resp_data.keys():
    print 'no exp is found'
    return None
  peer_info = resp_data['results']
  name_list = []
  url_list = []
  note_list = []
  for peer_data in peer_info:
    if peer_data['peerName'] == current_node_id:
      continue
    name_list.append(peer_data['peerName'])
    url_list.append(peer_data['url'])
    note_list.append(peer_data['note'])

  return name_list,url_list,note_list


def find_peer(peerName,experimentId,owner='global'):
  url = "/classes/PeerTable"
  url += ('?where=' + json.dumps({'peerName':peerName,'experimentId':experimentId,'owner':owner}))
  resp = cloud.lean_cloud_get(url)
  resp_data = resp.json()
  if 'results' not in resp_data.keys():
    print 'no peer is found'
    return None
  peer_info = resp_data['results']
  peerObj = None
  if len(peer_info) == 1:
    peerObj = peer_info[0]
  else:
    print str(len(peer_info))+' peers info found'
  print 'peerObj',peerObj
  return peerObj
  
def delete_peer(peerName,experimentId,owner='global'):
  peerInfo = find_peer(peerName,experimentId,owner)
  objectId = peerInfo['objectId']
  if objectId:
    resp = cloud.lean_cloud_delete('PeerTable',objectId)
    return resp
  else:
    print 'peer {} owned by {} not found'.format(peerName,owner)