"""
Gossip base routing

"""

from flask import Flask,jsonify,request,render_template,url_for
import peer_controller as pctr
import exp_controller as expctr
import requests
import callbacks
import json
from utils import jsonpify
import actions



class ATTRS:
  #for version compability check
  BACKWARD = 0,
  EXACT = 1,
  UPWARD = 2,
  #for version definition
  DEFAULT_VERSION = 3,
  BETA_VERSION = 4,
  RELEASE_VERSION = 5,
  #for peer lookup
  FULL_LIST_FROM_CENTRAL = 6, # unified peer list
  LIST_FROM_INDEPENDENT_STORAGE = 7 # seperated peer list


class Communication:

  def __init__(self,app,configuration):
    #keep this instance in global state
    import global_states
    global_states.states['comm'] = self
    if 'peer_seek' not in configuration.keys():
      configuration['peer_seek'] = ATTRS.FULL_LIST_FROM_CENTRAL
    
    self.app = app
    self.configuration = configuration
    self.global_conf = None
    with open('configurations/global_conf.json') as f:
      self.global_conf = json.load(f)

    """
    Sub-functions
    """
    def __get_peers_from_central__():
      if self.check_expID_and_nodeID():
        names,urls,notes = pctr.get_all_peers(self.expID,self.nodeID,owner='global')
        return names,urls,notes

    def __get_peer_from_central__(peerID):
      if self.check_expID_and_nodeID():
        peerObj = pctr.find_peer(peerID,self.expID,owner='global')
        return peerObj

    def __get_peers_from_shared_local_storage__():
      if self.check_expID_and_nodeID():
        names,urls,notes = pctr.get_all_peers(peerID,self.expID,owner=self.nodeID)
        return names,urls,notes

    def __get_peer_from_individual__(peerID):
      if self.check_expID_and_nodeID():
        peerObj = pctr.find_peer(peerID,self.expID,owner=self.nodeID)
        return peerObj

    def __undefined_func__(*args,**kwargs):
      raise Exception('NOTIMPLEMENTED','This function is not implemented')


    """
    setup web-based control panel
    """
    self.setup_control_panel_routes()

    """
    Dynamic function binding
    """
    _peer_seek = self.configuration['peer_seek']
    if _peer_seek == ATTRS.FULL_LIST_FROM_CENTRAL:
      self.get_peers = __get_peers_from_central__
      self.get_single_peer = __get_peer_from_central__
    elif _peer_seek == ATTS.LIST_FROM_INDEPENDENT_STORAGE:
      self.get_peers = __get_peers_from_shared_local_storage__
      self.get_single_peer = __get_peer_from_individual__
    else:
      self.get_peers = __undefined_func__
      self.get_single_peer = __undefined_func__
      
    """
    Init members
    """
    self.note = None
    

  def set_attributes(self,attrs_dict):
    if type(attrs_dict) != dict:
      raise Exception('PARAMTYPEERROR','attrs_dict must be a dictionary')
    attrs = attrs_dict.keys()
    permitted_attr_list = ['nodeID','expID','user']
    if 'user' in attrs and 'expID' in attrs:
      expID = attrs_dict['expID']
      user = attrs_dict['user']
      if expctr.find_exp(expID.strip(),user.strip()):
        self.expID = expID.strip()
        self.user = user.strip()
      else:
        raise Exception('EXPIDERROR','expID {} by {} is not registered'.format(expID,user))
    if 'nodeID' in attrs:
      nodeID = attrs_dict['nodeID'].strip()
      if nodeID:
        self.nodeID = nodeID


      
    

    



  def check_expID_and_nodeID(self,enableException=False):
    if not hasattr(self,'nodeID'):
      if enableException:
        raise Exception('NONSETERROR','nodeID should be assigned beforehand')
      return False
    if not hasattr(self,'expID'):
      if enableException:
        raise Exception('NONSETERROR','expID should be assigned beforehand')
      return False
    return True


  def is_node_registered(self):
    if not self.check_expID_and_nodeID():
      return False
    _peer_seek = self.configuration['peer_seek']
    obj = None
    if _peer_seek == ATTRS.FULL_LIST_FROM_CENTRAL:
      obj = pctr.find_peer(self.nodeID,self.expID,owner='global')
    elif _peer_seek == ATTS.LIST_FROM_INDEPENDENT_STORAGE:
      obj = pctr.find_peer(self.nodeID,self.expID,owner=self.nodeID)
    return True if obj else False
    


  def send_ack(self,peerID,topic,secret_code):
    """
    Inform the ready state of the peer.
    """
    if not peerID:
      raise Exception('NOPARAMS','peerID should not be none')
    if not topic:
      raise Exception('NOPARAMS','topic should not be none')
    if not secret_code:
      raise Exception('NOPARAMS','secret_code should not be none')
    
    peerObj = self.get_single_peer(peerID)
    if not peerObj:
      raise Exception('PEERIDNOTFOUND','peerID {} cannot be found'.format(peerID))
    url = peerObj['url']
    ack_received_url = url + url_for('ack_received')
    jsonData = {
      'peerID':peerID,
      'topic':topic,
      'secret_code':secret_code
    }
    resp = requests.post(ack_received_url,json=jsonData)
    return resp.ok

  def send(self,peerID,callback,params=None):
    """
    send a general-purposed request.
    callback: the server-side function to be executed.
    params: the json-style params of the callback function.
    """
    from datetime import datetime
    resp = {}
    resp['callback'] = callback
    resp['state'] = {}
    resp['state']['fromID'] = self.nodeID
    now = datetime.now()
    timeformat = self.global_conf['timeformat']
    timestamp = datetime.strftime(now,timeformat)
    resp['state']['timestamp'] = timestamp
    resp['state']['fromID'] = self.nodeID
    resp['state']['toID'] = peerID
    
    if params:
      if type(params) == dict:
        params = json.dumps(params)
      elif type(params) == str:
        # to find out whether it is legal json 
        json.loads(params)
      else:
        raise Exception('ARGWRONGTYPE','params must be dict or json-str but got {}'.format(type(params)))
      resp['params'] = params
    peerObj = self.get_single_peer(peerID)
    if not peerObj:
      raise Exception('PEERIDNOTFOUND','peerID {} cannot be found'.format(peerID))
    else:
      url = peerObj['url']
      peerID = peerObj['peerName']
      request_url = url + '/recv'
      print 'request_url=',request_url
      print 'json=',resp
      r = requests.post(request_url,json=resp)
      if r.ok:
        ret = r.json()
        return ret['output']
      else:
        raise Exception('BADNETWORK','peerID {} does not give a correct reply. ErrorCode={}'.format(peerID,r.status_code))




  def setup_gossip_route(self):
    @self.app.route('/')
    def index():
      return 'Gossip Stack 1.1'

    @self.app.route('/set_address')
    def set_address():
      node_url = request.base_url
      node_url = node_url.replace('/set_address','')
      self.url = node_url
      return self.url

    @self.app.route('/init/node_id',methods=['GET','POST'])
    def set_node_id():
      node_id = request.values.get('nodeID')
      if node_id:
        if node_id.strip() != '':
          self.nodeID = node_id
          resp = {
            'success': True,
            'message': 'nodeID is set to {}'.format(self.nodeID)
            }
          return jsonify(resp)
      resp = {
        'success': False,
        'message': 'nodeID is not set'
      }
      return jsonify(resp)
    
    @self.app.route('/init/note',methods=['GET','POST'])
    def set_node_note():
      note = request.values.get('note')
      if note:
        if note.strip() != '':
          self.note = note
          resp = {
            'success': True,
            'message': 'note is set to {}'.format(self.note)
            }
          return jsonify(resp)
      resp = {
        'success': False,
        'message': 'note is not set'
      }
      return jsonify(resp)
       

    @self.app.route('/init/exp',methods=['GET','POST'])
    def init_exp():
      expID = request.values.get('expID')
      user = request.values.get('user')
      if expID and user:
        if expID.strip() != '' and user.strip() != '':
          exp_obj = expctr.find_exp(expID.strip(),user.strip())
          if exp_obj:
            self.expID = expID.strip()
            self.user = user.strip()
            response = {
              'success': True,
              'message': 'Exp ID {} by {} is assigned'.format(self.expID,self.user)
            }
            return jsonify(response) 
          else:
            response = {
              'success': False,
              'message': 'Exp ID {} by {} is not registered before use.'.format(expID.strip(),user.strip())
            }
            return jsonify(response) 
      response = {
        'success': False,
        'message': 'Exp ID {} by {} is missing.'.format(expID,user)
      }
      return jsonify(response)
          
      
    @self.app.route('/register_myself')
    def register_myself():
      jsonp = request.values.get('jsonp')
      if not self.check_expID_and_nodeID():
        resp = {
          'success':False,
          'message': 'expID and nodeID are not set.'
        }
        if jsonp:
          return jsonpify(jsonp,resp)
        return jsonify(resp)
      if self.configuration['peer_seek'] == ATTRS.FULL_LIST_FROM_CENTRAL:
        node_url = request.base_url
        node_url = node_url.replace('/register_myself','')
        success = pctr.add_peer(self.nodeID,node_url,self.expID,owner='global',note=self.note,new=False)
        
        resp = {
          'success':success,
          'message': 'registry is successful' if success else 'registry failed'
        }
        if jsonp:
          return jsonpify(jsonp,resp)
        return jsonify(resp)
      else:
        resp = {
          'success':False,
          'message': 'peer_seek method not supported'
        }
        if jsonp:
          return jsonpify(jsonp,resp)
        return jsonify(resp)

    



    @self.app.route('/peers')
    def show_all_peers():
      jsonp = request.values.get('jsonp')
      names,urls,notes = self.get_peers()
      resp = []
      for name,url,note in zip(names,urls,notes):
        info = {}
        info['name'] = name
        info['url'] = url
        info['note'] = note
        resp.append(info)
      if jsonp:
        return jsonpify(jsonp,resp)
      return jsonify(resp)

    @self.app.route('/self')
    def show_this_node():
      jsonp = request.values.get('jsonp')
      if not self.check_expID_and_nodeID():
        resp = {
          'success':False,
          'message': 'expID and nodeID are not set.'
        }
        if jsonp:
          return jsonpify(jsonp,resp)
        return jsonify(resp)
      resp = {}
      node_url = request.base_url
      node_url = node_url.replace('/self','')
      resp['success'] = True
      resp['name'] = self.nodeID
      resp['url'] = node_url
      resp['expID'] = self.expID
      resp['note'] = self.note
      
      
      if jsonp:
          return jsonpify(jsonp,resp)
      return jsonify(resp)


    @self.app.route('/request_for_join')
    def request_for_join():
      jsonp = request.values.get('jsonp')
      # receive request from an unknown node
      data = request.get_json()
      version = data['version']
      blocks = data['blocks']
      timestamp = data['timestamp']
      peerID = data['nodeID']

      # version compatibility check
      if self.configuration['compatiblility'] == ATTRS.BACKWARD:
        # as long as the version of this peer is not greater than mine, I will accept.
        if version <= self.configuration['version']:
          # accept
          print 'version accepted'
          

      _peer_seek = self.configuration['peer_seek']
      from_node = 'unknown'
      if _peer_seek == ATTRS.FULL_LIST_FROM_CENTRAL:
        # Add all peers from the central server
        # In this implementation, we don't replicate the peer information for space saving. No information is needed to store locally.
        from_node = 'global'
      elif _peer_seek == ATTRS.LIST_FROM_INDEPENDENT_STORAGE:
        # Add all peers to the exclusive shared storage
        # The peer list might be different from peer to peer. Every peer can only access his added peers.
        from_node = self.nodeID
      
      names,urls = self.get_peers()
      peers = []
      for name,url in zip(names,urls):
        info = {}
        info['name'] = name
        info['url'] = url
        peers.append(info)

         
      response = {
        'success': True,
        'from': from_node,
        'peers': peers
      }
      if jsonp:
          return jsonpify(jsonp,resp)
      return jsonify(response)
      
        

        


    @self.app.route('/ack_received',methods=['GET','POST'])
    def ack_received(self):
      # For http/https based implementation, ack is not necessary. However in order to simulate the communication process, we intentionally keep this feature.
      data = request.get_json()
      peerID = data['peerID']
      topic = data['topic']
      secret_code = data['secret_code']
      content = 'topic {} from {}-{} comfirmed'.format(topic,peerID,secret_code)

    @self.app.route('/recv',methods=['GET','POST'])
    def deal_received_message():
      """
      the received json should be of this format:
      {
        state:{
          version: int,
          timestamp: str,
          fromID: str,
          toID: str,
        }
        callback: str,
        params:{
          param1:...,
          param2:...,
          ...
        }
      }
      """
      jsonp = request.values.get('jsonp')
      data = request.get_json()
      callback = None
      state = None
      if 'callback' in data.keys():
        callback = data['callback']
      if 'state' in data.keys():
        state = data['state']
      print 'from /recv state=',state
      if not callback:
        message = 'Callback is not given. The message will not be processed furthermore.'
        resp = {
          'success': True,
          'message': message
        }
        if jsonp:
          return jsonpify(jsonp,resp)
        return jsonify(resp)
      method_to_call = getattr(callbacks, callback)
      if not method_to_call:
        message = 'Cannot find the callback {}. The message is ignored.'.format(callback)
        resp = {
          'success': False,
          'message': message
        }
        if jsonp:
          return jsonpify(jsonp,resp)
        return jsonify(resp)
      if 'params' in data.keys():
        params = data['params']
        params = json.loads(params)
        output = method_to_call(state,params)
        resp = {
          'output':output
        }
      else:
        output = method_to_call(state)
        resp = {
          'output':output
        }
      if jsonp:
          return jsonpify(jsonp,resp)
      return jsonify(resp)

    

  def setup_control_panel_routes(self):
    @self.app.route('/action_list')
    def get_action_list():
      import inspect
      jsonp = request.values.get('jsonp')
      methods = []
      reload(actions)
      print 'actions',dir(actions)
      for name in dir(actions):
       if name.startswith('__'):
         continue
       obj = getattr(actions, name)
       if inspect.isclass(obj):
          print '{} is a class'.format(obj)
          members = inspect.getmembers(obj, predicate=inspect.ismethod)
          for (func_name,func) in members:
            if func_name.startswith('__'):
              continue
            func_str = str(func)
            if '<bound' in func_str:
              # this is an bound method,process
              method_obj = {}
              method_obj['method_name'] = name+"."+func_name
              method_obj['args'] = inspect.getargspec(func)
              method_obj['doc'] = inspect.getdoc(func)
              methods.append(method_obj)
       elif (inspect.ismethod(obj) or inspect.isfunction(obj)):
          print '{} is a function'.format(obj)
          method_obj = {}
          method_obj['method_name'] = name
          method_obj['args'] = inspect.getargspec(obj)
          method_obj['doc'] = inspect.getdoc(obj)
          methods.append(method_obj)
      #dynamic_action_map = actions.Actions.__get_dynamic_function_dict__()
      #print 'dynamic_links=',dynamic_action_map.keys()
      #methods = methods + dynamic_action_map.values()

      resp = {
              'success':True,
              'methods':methods
      }
      if jsonp:
        return jsonpify(jsonp,resp)
      return jsonify(resp)
      
  
    def get_params_of_actions(request):
      content = request.get_json()
      resp = None
      if not content:
        content = {}
        method_arg = request.values.get('method')
        params_arg = request.values.get('params')
        if method_arg:
          content['method'] = method_arg
        if params_arg:
          try:
            _params = json.loads(str(params_arg))
            content['params'] = _params
            print 'params=',_params,'type=',type(_params)
          except:
            resp = {
              'success':False,
              'message':'params should be json type.',
              'output':None
            }
      return {'content':content, 'resp':resp}
    
    def action_response(jsonp,resp):
      if jsonp:
        return jsonpify(jsonp,resp)
      return jsonify(resp)
  
    def get_normal_method(content):
      if not hasattr (actions, content['method']):
        resp = {
          'success':False,
          'message':'method {} is not defined in the actions.'.format(content['method']),
          'output':None
        }
        return {'method':None,'resp':resp}
      else:
        # this function is found
        method_to_call = getattr(actions,content['method'])
        return {'method':method_to_call,'resp':None}
        
       

    @self.app.route('/actions',methods=['POST','GET'])
    def invoke_action():
      import inspect
      def call_without_params(method):
        try:
          output = method_to_call(self)
          resp = {
            'success':True,
            'output':output,
            'message':None
          }
          return action_response(jsonp,resp)
        except Exception as e:
          resp = {
            'success':False,
            'output': None,
            'message':str(e)
          }
          return action_response(jsonp,resp)
      
      def call_with_params(method,params):
        try:
          params = content['params']
          output = method_to_call(self,**params)
          resp = {
            'success':True,
            'output':output,
            'message':None
          }
          return action_response(jsonp,resp)
        except Exception as e:
          resp = {
            'success':False,
            'output':None,
            'message':str(e)
          }
          return action_response(jsonp,resp)
      param_obj = get_params_of_actions(request)
      jsonp = request.values.get('jsonp')
      if param_obj['resp']:
        # error found
        return action_response(jsonp,param_obj['resp'])
      else:
        content = param_obj['content']
      if 'method' not in content.keys():
        resp = {
          'success':False,
          'message':'method is not specified.',
          'output': None
        }
        return action_response(jsonp,resp)
      if '.' not in content['method']:
        obj = get_normal_method(content)
        if obj['resp']:
          return action_response(jsonp,obj['resp'])
        method_to_call = obj['method']
        
        if 'params' not in content.keys():
          print "'params' not in content.keys()"
          return call_without_params(method_to_call)
        else:
          print "'params' exist"
          params = content['params']
          return call_with_params(method_to_call,params)
          
      else:
        class_name,method = content['method'].split('.')
        if not hasattr (actions, class_name):
          resp = {
            'success':False,
            'message':'class {} is not defined in the actions.'.format(class_name),
            'output':None
          }
          return action_response(jsonp,resp)
        else:
          # this obj is found in actions.py
          action_class = getattr(actions,class_name)
          if not inspect.isclass(action_class):
            # this obj is not a class  
            resp = {
              'success':False,
              'message':'{} is not a class in the actions.'.format(action_class),
              'output':None
            }
            return action_response(jsonp,resp)
          else:
            # this obj is a class
            #dynamic_func_table = actions.Actions.__get_dynamic_function_dict__()
            if hasattr(action_class,method):
              print "getattr:",action_class,method
              method_to_call = getattr(action_class,method)
              if 'params' not in content.keys():
                return call_without_params(method_to_call)
              else:
                params = content['params']
                return call_with_params(method_to_call,params)
            else:
              resp = {
                'success':False,
                'message':'{} is not a defined in the class {}.'.format(method,action_class),
                'output':None
              }
              return action_response(jsonp,resp)
          
      
    
      
      
        

    @self.app.route('/actionexist')
    def check_action_exist():
      jsonp = request.values.get('jsonp')
      method = request.values.get('method')
      exist = hasattr(actions.Actions,method)
      resp = {
        'method': method,
        'existing':exist
      }
      return action_response(jsonp,resp)

        




      
