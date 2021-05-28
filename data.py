import json
from typing import Any

dataF = json.loads(open('save.json','r').read())

def save(): json.dump(dataF,open('save.json','w+'),indent=2); return True

def read(path:list):
  res = dataF[path[0]]
  for i in [p for p in path if p != path[0]]: res = res[i]
  return res

def write(value:Any,path:list):
  path = "['" + "']['".join(path) + "']"
  if isinstance(value,str): exec(f'dataF{path} = "{value}"'); return True
  if isinstance(value,(int,list,dict)): exec(f'dataF{path} = {value}'); return True
  return False

def action(action:str,value:Any,path:list):
  path = "['" + "']['".join(path) + "']"
  if isinstance(value,str): exec(f'dataF{path}.{action}("{value}")'); return True
  if isinstance(value,int): exec(f'dataF{path}.{action}({value})'); return True
  return False

def math(operator:str,value:int|float,path:list):
  path = "['" + "']['".join(path) + "']"
  if isinstance(value,int): exec(f'dataF{path} {operator}= {value}'); return True
  return False