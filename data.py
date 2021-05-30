import json
from typing import Any

loadedSaves = {}

class load():
	def __init__(self,filename):
		self.filename = filename
		if filename in loadedSaves: self.file = loadedSaves[filename]
		else:
			self.file = json.loads(open(f'saves/{filename}.json','r').read())
			loadedSaves[filename] = self.file
	
	def save(self): json.dump(self.file,open(f'saves/{self.filename}.json','w+'),indent=2); return True

	def read(self,path:list):
		res = self.file[path[0]]
		for i in [p for p in path if p != path[0]]: res = res[i]
		return res

	def write(self,value:Any,path:list):
		path = "['" + "']['".join(path) + "']"
		if isinstance(value,str): exec(f'self.file{path} = "{value}"'); return True
		if isinstance(value,(int,list,dict)): exec(f'self.file{path} = {value}'); return True
		return False

	def action(self,action:str,value:Any,path:list):
		path = "['" + "']['".join(path) + "']"
		if isinstance(value,str): exec(f'self.file{path}.{action}("{value}")'); return True
		if isinstance(value,int): exec(f'self.file{path}.{action}({value})'); return True
		return False

	def math(self,operator:str,value:int|float,path:list):
		path = "['" + "']['".join(path) + "']"
		if isinstance(value,(int,float)): exec(f'self.file{path} {operator}= {value}'); return True
		return False