"""
Define gossip related routing rules.

The first two parameters should be always defined.
"""
#from base_comm.actions import Actions

def send_ask_for_peer_request(comm,peerID):
  """
  {
    "peerID":"string"
  }
  """
  callback = 'on_peer_request'
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

