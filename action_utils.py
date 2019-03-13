import inspect
from base_comm.actions import Actions

def before_method():
  print "before"

def after_method():
  print "after"

def comm(method_type,type_table=None):
  def _comm(function):
      def wrapper(*args, **kwargs):
        before_method()
        something_with_argument(argument)
        result = function(*args, **kwargs)
        after_method()
        return result
      return wrapper
  return _comm


def send_to_peer(peerID,type_table=None):
  def _send_to_peer(function):
    from global_states import states
    def wrapper(*args, **kwargs):
      #before_invoking
      argspec = inspect.getargspec(function)
      print 'argspec=',argspec
      #invoking
      result = function(*args, **kwargs)
      #after_invoking
      print 'sending'
      return result
    return wrapper
  return _send_to_peer

""" 
def action(function):
  def wrapper(*args,**kwargs):
    argspec = inspect.getargspec(function)
    result = function(*args,**kwargs)
    Actions.register(hello_here)
    return result
  return wrapper
"""