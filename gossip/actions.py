"""
Define gossip related routing rules.

The first two parameters should be always defined.
"""
#from base_comm.actions import Actions
import json

def send_ask_for_peer_request(comm,peerID,content):
  """
  {
    "peerID":"string",
    "content":"string"
  }
  """
  callback = 'on_peer_request'
  params = json.dumps({"content":content})
  output = comm.send(peerID,callback,params)
  return output

def send_ping_request(comm,peerID):
  """
  {
    "peerID":"string"
  }
  """
  callback = 'reply_ping_with_pong'
  output = comm.send(peerID,callback)
  return output

def hello_here(comm,content):
  print 'hello',content
  return 'hello_here'+str(content)


def Hime(comm,content):
    print 'hime',content
    return 'hime' + content


def register_actions():
  #Actions.register(send_ask_for_peer_request)
  #Actions.register(hello_here)
  pass

