import json

def jsonpify(function_name,content):
  content = json.dumps(content)
  return "{func}({content})".format(func=function_name,content=content)