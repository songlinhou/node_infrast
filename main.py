from flask import Flask
from flask_cors import CORS
from base_comm.comm import Communication,ATTRS
from base_comm import actions
from gossip import gossip



"""
To resolve the potential problem of db crashing in the process of peer list modification, we use a central cloud server to store peer list for every node. 
"""
gossip.register_actions()

app = Flask('app')
CORS(app, expose_headers='Authorization') # for cross origin access

@app.route('/register_actions')
def register_actions():
  gossip.register_actions()
  return "registered"


comm_configuration = {
  'version':ATTRS.DEFAULT_VERSION,
  'compatiblility': ATTRS.EXACT,
  'peer_seek':ATTRS.FULL_LIST_FROM_CENTRAL
}

node_info = {
  'nodeID':'miniCat',
  'expID':'happyZoo',
  'user':'ray'
}

comm = Communication(app,comm_configuration)

comm.setup_gossip_route()

comm.set_attributes(node_info)


app.run(host='0.0.0.0', port=8082)