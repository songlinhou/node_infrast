states = {}

def get_item(key):
  if key in states.keys():
    return states[key]
  return None

