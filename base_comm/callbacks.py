from gossip.callbacks import *

def print_params(state,params):
  """
  state:{
          version: int,
          timestamp: str,
          fromID: str,
          toID: str,
        }
  """
  print 'state',state
  print 'params',params
  return 'params called.{},{}'.format(state,params)
  
def on_join_peers(state,params):
  """
  when some other node ask for peer joining.
  """
  version = state['version']
  blocks = params['blocks']
  timestamp = state['timestamp']
  peerID = state['fromID']
  #toID = state['toID'] skip the message direction check
  

def on_peer_request(state,params):
  return "Hello params=" + params['content']




 