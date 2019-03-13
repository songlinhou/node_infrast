"""
The actions shown here will be displayed in control panel.

Only define active functions here.

The first parameter must be comm module.

NOTE: How to import functions from other files.

(1)from PYTHONFILE import FUNCTIONNAME: import specific function
(2)from PYTHONFILE import *: import all functions

"""
import importlib
import types
import inspect
import json
import os,threading
import logging
from global_states import states
from gossip.gossip import *


logging.basicConfig(level=logging.DEBUG,format='(%(threadName)-9s) %(message)s',)
# for threading safety in io operations
io_lock = threading.RLock()

def hello_world(comm,content):
  """
  A test function.
  """
  print 'hello_world',content
  return 'hello_world!' + str(content) 


def test_sum(comm,a,b,c):
  """
  {
    "a":"int",
    "b":"int",
    "c":"int"
  }
  """
  return a+b+c

def hi_new(comm,content):
  """
  hi new one
  """
  return "Hi" + str(content)





class Actions(object):
    dynamic_func_folder_name = 'dynamic_func_def'
    func_file_name_rule = '{}.def'
    @classmethod
    def unregister(cls, name):
        #global dynamic_actions
        #dynamic_actions[name]
        return delattr(cls, name)

    @classmethod
    def register(cls, func):
        Actions.__save_dynamic_function__(func)
        print "{} is registered".format(func.__name__)
        #print "registered keys",dynamic_actions.keys()
        return setattr(cls, func.__name__, types.MethodType(func, cls))

    @classmethod
    def __get_dynamic_function_dict__(cls):
        file_path = os.path.realpath(__file__)
        comm_dir = os.path.realpath(os.path.join(file_path,'..'))
        func_def_dir = os.path.join(comm_dir,Actions.dynamic_func_folder_name)
        function_dict = {}
        if not os.path.exists(func_def_dir):
          logging.debug('folder {} is missing'.format(Actions.dynamic_func_folder_name))
          return function_dict
        logging.debug('io lock is acquired')
        io_lock.acquire()
        try:
          files = os.listdir(func_def_dir)
          ext = Actions.func_file_name_rule.format('')
          for file_name in files:
            if not file_name.endswith(ext):
              logging.debug('skip file {}'.format(file_name))
              continue
            full_path = os.path.join(func_def_dir,file_name)
            function_name = file_name[0:len(file_name)-len(ext)]
            with open(full_path) as f:
              func_json = json.load(f)
              function_dict[function_name] = func_json
        except Exception as e:
          logging.error('Error is found in getting dynamic functions definitions: {}'.format(e))
        finally:
          logging.debug('io lock is released')
          io_lock.release()
          return function_dict
        return function_dict
        

    @classmethod
    def __save_dynamic_function__(cls,func):
        file_path = os.path.realpath(__file__)
        comm_dir = os.path.realpath(os.path.join(file_path,'..'))
        func_def_dir = os.path.join(comm_dir,Actions.dynamic_func_folder_name)
        #states[]
        

        #create object
        method_obj = {}
        method_obj['method_name'] = "Actions."+func.__name__
        method_obj['args'] = inspect.getargspec(func)
        method_obj['doc'] = inspect.getdoc(func)
        logging.debug('method_obj={}'.format(method_obj))
        #io operations
        try:
          logging.debug('io lock is acquired')
          io_lock.acquire()
          if not os.path.exists(func_def_dir):
            os.makedirs(func_def_dir)
          files = os.listdir(func_def_dir)
          target_file_name = Actions.func_file_name_rule.format(func.__name__)
          full_target_path = os.path.join(func_def_dir,target_file_name)
          if target_file_name in files:
            # an existing file found
            os.remove(full_path)
          with open(full_target_path,'w') as f:
            json.dump(method_obj,f)
        except Exception as e:
          logging.error('Error is found in saving dynamic function: {}'.format(e))
        finally:
          io_lock.release()
          logging.debug('io lock is released')

