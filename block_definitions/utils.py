from datetime import datetime
import json

def is_non_empty_str(content):
  if type(content) != str:
    return False
  content = content.strip()
  if content == '':
    return False
  return True

def get_timestamp_from_str(timestr):
  if type(timestr) != str:
    return None
  with open('configurations/global_conf.json') as f:
    global_conf = json.load(f)
  try:
    timestamp = datetime.strptime(tstr,global_conf['timeformat'])
    return timestamp
  except:
    return None

def is_non_negative_int(number):
  if type(number) != int:
    return False
  if number < 0:
    return False
  return True