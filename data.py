import json
from typing import Any

loadedSaves = {}

def saveAll(): [json.dump(loadedSaves[file],open(f'saves/{file}.json','w+'),indent=2) for file in loadedSaves]

defaultServer = {
	"config": {
		"enableAutoResponses": True,
		"enableTalkingStick": False,
		"enableDadBot": True,
		"enableBirthdays": False,
		"enableQOTD": False,
		"enableQuotes": False,
		"maxRoll": 8192
	},
	"ignore": [],
	"activeMembers": [],
	"tsLeaderboard": {},
	"messageLeaderboard": {},
	"activities": {},
	"channels": {
		"talkingStick": 0,
		"birthdays": 0,
		"quotes": 0,
		"qotd": 0
	},
	"roles": {
		"talkingStick": 0,
		"birthdays": 0
	},
	"currentStick": 0}
defaultUser = {
    "messages": 0,
    "birthday": None,
    "ricePurityScore": None,
		"config": {
			"ignored": False}}

class load():
	def __init__(self,filename):
		self.filename = filename
		if filename in loadedSaves: self.file = loadedSaves[filename] # loads data from pre-loaded variable if data has already been loaded
		else:
			try: self.file = json.loads(open(f'saves/{filename}.json','r').read())
			except: self.file = {} # sets load file to blank dictionary if file does not exist or load error occurs
			loadedSaves[filename] = self.file

	def reload(self,save:bool=False):
		if save: self.save()
		try: loadedSaves[self.filename] = json.loads(open(f'saves/{self.filename}.json','r').read())
		except: return False
		return True

	def save(self): json.dump(self.file,open(f'saves/{self.filename}.json','w+'),indent=2); return True

	def read(self,path:list=[]):
		if path == []: return self.file
		try:
			res = self.file[path[0]]
			for i in [p for p in path if p != path[0]]: res = res[i]
		except KeyError as key:
			load.new(self,str(key)[1:-1])
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
		if isinstance(value,str): eval(f'self.file{path}.{action}("{value}")'); return True
		if isinstance(value,int): eval(f'self.file{path}.{action}({value})'); return True
		return False

	def math(self,operator:str,value:int|float,path:list,roundNum:bool=False,roundVal:int=0):
		path = "['" + "']['".join(path) + "']"
		if roundNum and isinstance(value,(int,float)): exec(f'self.file{path} = round(self.file{path}{operator}{value},{roundVal})'); return True
		if isinstance(value,(int,float)): exec(f'self.file{path} {operator}= {value}'); return True
		return False
	
	def new(self,id):
		match self.filename:
			case 'servers': self.file.update({id:defaultServer}); return True
			case 'users': self.file.update({id:defaultUser}); return True
			case _: return 'unknown filename'