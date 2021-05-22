import os,re,json,logging,discord,asyncio,requests
from discord.ext.commands.core import guild_only
from discord_slash.utils.manage_commands import create_option
from mcrcon import MCRcon
from random import randint
from shutil import copytree
from time import time,sleep
from datetime import datetime
from dotenv import load_dotenv
from mcstatus import MinecraftServer
from discord.ext import commands
from discord_slash import cog_ext,SlashCommand,SlashContext
from discord.ext.commands import *

def setupLogger(name,log_file,level=logging.WARNING):
	logger = logging.getLogger(name)
	formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] %(message)s','%d/%m/%Y %H:%M:%S')
	fileHandler = logging.FileHandler(log_file, mode='a',encoding='utf-8')
	fileHandler.setFormatter(formatter)
	logger.setLevel(level)
	logger.addHandler(fileHandler)
	return logger
load_dotenv()
try: data = json.loads(open('save.json','r').read())
except: data = json.loads(open('save.json.default','r').read())
serverStarted=False
sizes={2:'MBs',3:'GBs'}
mainDirectory = os.getcwd()
testingServer=[844127424526680084]
hypixelKey=os.getenv('hypixelKey')
serverQuery=os.getenv('serverQuery')
servers=json.loads(open('servers.json','r').read())
outputLog=setupLogger('output log','logs/output.log')
sentLog=setupLogger('sent log','logs/messages/sent.log')
editedLog=setupLogger('edited log','logs/messages/edited.log')
deletedLog=setupLogger('deleted log','logs/messages/deleted.log')
valueConverter={'True':True,'False':False,'true':True,'false':False}
bannedVariables=['__file__','qa','userqa','godqa','fileqa','hypixelKey','servers','bannedVariables']
splitters=["I'm ","i'm "," im ",' Im ',"i am ","I am ","I'M "," IM ","I AM "]
qa=json.loads(open('qa.json','r').read()); userqa = qa['userqa']; godqa = qa['godqa']; fileqa = qa['fileqa']
mc=MCRcon(os.getenv('mcRconHost'),os.getenv('mcRconPassword'),int(os.getenv('mcRconPort')))
client=commands.Bot(command_prefix=('reginald!','reg!','r!'),case_insensitive=True,help_command=None,owner_id=250797109022818305,intents=discord.Intents.all())
slash=SlashCommand(client)

def adminOrOwner():
	async def perms(ctx):
		if ctx.author.id == client.owner_id or ctx.author.guild_permissions.administrator: return True
		raise Exception('You are not an admin.')
	return check(perms)
def modOrOwner():
	async def perms(ctx):
		if ctx.author.id == client.owner_id or ctx.author.guild_permissions.manage_server: return True
		raise Exception('You are not an admin.')
	return check(perms)
def save(): json.dump(data,open('save.json','w+'),indent=2)

class serverMcstarter(commands.Cog):
	def __init__(self,client): self.client = client
	@cog_ext.cog_subcommand(base='minecraft',name='start',description='starts a minecraft server.')
	async def start(self,ctx:SlashContext,server):
		if serverStarted: return
		try: os.chdir(servers[server]['directory'])
		except: await ctx.send('server name error')
		os.startfile('botStart.bat')
		os.chdir(mainDirectory)
		await ctx.send('okay, it\'s starting.')
		for i in range(data['servers'][str(ctx.guild.id)]['config']['maxServerStartTime']):
			try: MinecraftServer.lookup(serverQuery).query().players.online; break
			except: sleep(1)
		else: await ctx.send('error starting server.'); return
		await ctx.send('it should be up.')
		general.logOutput(f'starting server {server}',ctx)
	@cog_ext.cog_subcommand(base='minecraft',name='stop',description='stops active minecraft server. (\'-f\' requires admin)')
	async def stop(self,ctx:SlashContext,args=None):
		if MinecraftServer.lookup(serverQuery).query().players.online > 0:
			if not (args == '-f' and adminOrOwner()): await ctx.send('no, fuck you, there are people online.'); return
		try: mc.connect(); mc.command('stop'); mc.disconnect(); serverStarted = False; await client.change_presence(activity=discord.Game('Server Stopped')); await ctx.send('stopping server.')
		except: await ctx.send('failed to shutdown server.'); return
		general.logOutput(f'stopping server',ctx)
	@cog_ext.cog_subcommand(base='minecraft',name='cmd',description='runs command on the active minecraft server.')
	@is_owner()
	async def cmd(self,ctx:SlashContext,command):
		try: mc.connect(); response = mc.command(command); mc.disconnect()
		except: await ctx.send('failed to send command'); return
		try: await ctx.send(re.sub('§.','',response))
		except: pass
		general.logOutput(f'command {command} run',ctx)
	@cog_ext.cog_subcommand(base='minecraft',name='info',description='lists info on given minecraft server.')
	async def list_info(self,ctx:SlashContext,server):
		info = []
		try:
			for i in servers[server]:
				if i=='directory' or i=='isModded' or i=='mods': continue
				info.append(f'{i}: {servers[server][i]}')
		except: await ctx.send('server name error')
		info.append('modpack: vanilla') if servers[server]['isModded']==False else info.append(f'modpack: https://mods.nutt.dev/{server}')
		info.append(f'size: {serverMcstarter.getServerSize(server)}')
		await ctx.send(embed=discord.Embed(title=f'{server} info:',description='\n'.join(info),color=0x69ff69))
		general.logOutput(f'info about server {server} requested',ctx)
	@cog_ext.cog_subcommand(base='minecraft',name='online',description='returns list of players online.')
	async def online(self,ctx:SlashContext):
		try: players = MinecraftServer.lookup(serverQuery).query().players.names
		except: await ctx.send('cannot connect to server. is it online?'); return
		if players == []: await ctx.send('no one is online.'); return
		await ctx.send(embed=discord.Embed(title='Players Online:',description='\n'.join(players),color=0x69ff69))
		general.logOutput(f'online players requested',ctx)
	@cog_ext.cog_subcommand(base='minecraft',name='servers',description='lists all minecraft servers')
	async def list_servers(self,ctx:SlashContext): await ctx.send(embed=discord.Embed(title='Minecraft Servers:',description='\n'.join(servers),color=0x69ff69))
	def getServerSize(server):
		size = 0; sizeType = 0
		for path, dirs, files in os.walk(servers[server]['directory']):
			for f in files: fp = os.path.join(path, f); size += os.path.getsize(fp)
		while size/1024 > 1: size = size/1024; sizeType += 1
		return f'{round(size,3)} {sizes[sizeType]}'
class theDisciplineSticc(commands.Cog):
	def __init__(self,client): self.client = client
	async def sticcLoop():
		await client.wait_until_ready()
		while client.is_ready:
				await asyncio.sleep(60)
				if datetime.now().strftime("%H:%M") == '09:00':
					for guild in data['servers']:
						if (data['servers'][guild]['tsRole'] == 0 or data['servers'][guild]['tsChannel'] == 0) and data['servers'][guild]['config']['enableTalkingStick']:
							server = await client.fetch_guild(int(guild))
							await (await server.fetch_member(server.owner_id)).send(f'error in talking stick. please redo setup in {server.name}.')
							continue
						if data['servers'][guild]['config']['enableTalkingStick']: await theDisciplineSticc.rollTalkingStick(guild)
					copytree(f'{os.getcwd()}\\logs',f'{os.getcwd()}\\backups\\logs\\{datetime.fromtimestamp(time()).strftime("%d.%m.%Y %H.%M.%S")}')
	@cog_ext.cog_subcommand(base='sticc',name='setup',description='setup the discipline sticc. (requires admin)')
	@adminOrOwner()
	async def setup(self,ctx:SlashContext,role:discord.Role,channel:discord.TextChannel):
		if not data['servers'][str(ctx.guild.id)]['config']['enableTalkingStick']: await ctx.send(embed=discord.Embed(title='The Talking Stick is not enabled on this server.',color=0x69ff69)); return
		data['servers'][str(ctx.guild.id)]['tsRole'] = role.id
		data['servers'][str(ctx.guild.id)]['tsChannel'] = channel.id
		await ctx.send(embed=discord.Embed(title='Setup Complete.',description=f'role: <@&{role.id}>\n\nchannel: <#{channel.id}>',color=0x69ff69))
		general.logOutput(f'talking stick setup',ctx)
	@cog_ext.cog_subcommand(base='sticc',name='reroll',description='reroll the talking sticc. (requires admin)')
	@adminOrOwner()
	async def reroll(self,ctx:SlashContext):
		if not data['servers'][str(ctx.guild.id)]['config']['enableTalkingStick']: await ctx.send(embed=discord.Embed(title='The Talking Stick is not enabled on this server.',color=0x69ff69)); return
		await theDisciplineSticc.rollTalkingStick(str(ctx.guild.id))
		await ctx.send('reroll successful.')
		general.logOutput(f'talking stick reroll',ctx)
	@cog_ext.cog_subcommand(base='leaderboard',name='sticcs',description='leaderboard of how many times someone has had the talking sticc')
	async def leaderboard_sticcs(self,ctx:SlashContext):
		if not data['servers'][str(ctx.guild.id)]['config']['enableTalkingStick']: await ctx.send(embed=discord.Embed(title='The Talking Stick is not enabled on this server.',color=0x69ff69)); return
		data['servers'][str(ctx.guild.id)]['tsLeaderboard'] = {key: value for key, value in sorted(data['servers'][str(ctx.guild.id)]['tsLeaderboard'].items(), key=lambda item: item[1],reverse=True)}
		names = []
		index = 1
		await ctx.defer()
		for member in data['servers'][str(ctx.guild.id)]['tsLeaderboard']:
			if member not in data['variables']['idNameCache']: data['variables']['idNameCache'][member] = (await client.fetch_user(member)).name
			rank = str(index)+("th" if 4<=index%100<=20 else {1:"st",2:"nd",3:"rd"}.get(index%10, "th")); index += 1
			names.append(f"{rank} - {data['variables']['idNameCache'][member]}: {data['servers'][str(ctx.guild.id)]['tsLeaderboard'][member]}")
		await ctx.send(embed=discord.Embed(title='Sticc Leaderboard:',description='\n'.join(names),color=0x69ff69))
		general.logOutput(f'stick leaderboard requested',ctx)
	@cog_ext.cog_subcommand(base='sticc',name='active',description='lists members who have been active in the past day.')
	async def list_active(self,ctx:SlashContext):
		if not data['servers'][str(ctx.guild.id)]['config']['enableTalkingStick']: await ctx.send(embed=discord.Embed(title='The Talking Stick is not enabled on this server.',color=0x69ff69)); return
		active = []
		await ctx.defer()
		for member in data['servers'][str(ctx.guild.id)]['activeMembers']:
			if member not in data['variables']['idNameCache']: data['variables']['idNameCache'][member] = (await client.fetch_user(member)).name
			active.append(data['variables']['idNameCache'][member])
		await ctx.send(embed=discord.Embed(title='Active Members:',description='\n'.join(active),color=0x69ff69))
		general.logOutput(f'active users requested',ctx)
	async def rollTalkingStick(guild):
		tsRole = discord.Object(data['servers'][guild]['tsRole'])
		server = await client.fetch_guild(guild)
		while True:
			try: rand = data['servers'][guild]['activeMembers'][randint(0,len(data['servers'][guild]['activeMembers'])-1)]
			except ValueError: return 
			if int(rand) in data['servers'][guild]['ignore']: continue
			try: oldStik = await server.fetch_member(data['servers'][guild]['currentStik'])
			except discord.errors.NotFound: oldStik = None
			newStik = await server.fetch_member(rand)
			try:
				if not (rand == data['servers'][guild]['currentStik'] or (newStik.bot and oldStik.bot)): break
			except AttributeError:
				if not rand == data['servers'][guild]['currentStik']: break
		if oldStik != None: await oldStik.remove_roles(tsRole)
		await newStik.add_roles(tsRole)
		await (await client.fetch_channel(data['servers'][guild]['tsChannel'])).send(f'congrats <@!{rand}>, you have the talking stick.')
		data['servers'][guild]['currentStik'] = rand
		srand = str(rand)
		if srand in data['servers'][guild]['tsLeaderboard']: data['servers'][guild]['tsLeaderboard'][srand] += 1
		else: data['servers'][guild]['tsLeaderboard'].update({srand:1})
		data['servers'][guild]['activeMembers'] = []
		log = f'stick rerolled to {newStik.name} in {server.name}'
		outputLog.warning(log)
		if data['botConfig']['stickToConsole']: print(log)
		save()
class command(commands.Cog):
	def __init__(self,client): self.client = client
	@cog_ext.cog_subcommand(base='reginald',name='hello',description='have reginald say hi.')
	async def hello_reginald(self,ctx:SlashContext):
		await ctx.send(file=discord.File('reginald.png'))
		general.logOutput(f'said hi to reginald',ctx)
	@cog_ext.cog_slash(name='clearidcache',description='clears ID cache variable')
	@is_owner()
	async def clearIDcache(self,ctx:SlashContext):
		data['variables']['idNameCache'] = {}
		await ctx.send('successfully cleared ID cache')
		save()
		general.logOutput(f'idNameCache cleared',ctx)
	@cog_ext.cog_subcommand(base='config',subcommand_group='bot',name='set',description='set variables for the bot',options=[create_option('variable','see current value with /config bot list',3,True,list(data['botConfig'].keys())),create_option('value','bool or int',5,True)])
	@is_owner()
	async def config_bot_set(self,ctx:SlashContext,variable,value):
		data['botConfig'][variable] = value
		await ctx.send(f"successfully set {variable} to {data['botConfig'][variable]}")
		save()
		general.logOutput(f'bot config {variable} set to {str(value)}',ctx)
	@cog_ext.cog_subcommand(base='config',subcommand_group='server',name='set',description='set variables for the bot. (requires admin)',options=[create_option('variable','see current value with /config server list',3,True,list(data['defaultServer']['config'].keys())),create_option('value','bool or int',3,True)])
	@adminOrOwner()
	async def config_server_set(self,ctx:SlashContext,variable,value):
		if variable == 'maxRolls' and int(value) > 32768: await ctx.send('maxRolls cannot be higher than 32768!'); return
		if value in valueConverter: value = valueConverter[value]
		else:
			try: value = int(value)
			except: await ctx.send('value error'); return
		if type(data['servers'][str(ctx.guild.id)]['config'][variable]) == type(value): data['servers'][str(ctx.guild.id)]['config'][variable] = value
		else: await ctx.send('type error'); return
		await ctx.send(f"successfully set {variable} to {data['servers'][str(ctx.guild.id)]['config'][variable]}")
		if variable == 'enableTalkingStick' and value in valueConverter: await ctx.send('remember to do /sticc setup to enable the talking sticc.')
		save()
		general.logOutput(f'server config {variable} set to {str(value)}',ctx)
	@cog_ext.cog_slash(name='reload',description='reloads save files')
	@is_owner()
	async def reloadSaves(self,ctx:SlashContext):
		global qa,userqa,godqa,fileqa,servers
		qa = json.loads(open('qa.json','r').read()); userqa = qa['userqa']; godqa = qa['godqa']; fileqa = qa['fileqa']
		servers = json.loads(open('servers.json','r').read())
		await ctx.send('reload successful.')
		general.logOutput(f'reloaded saves',ctx)
	@cog_ext.cog_subcommand(base='config',subcommand_group='bot',name='list',description='list config variables.')
	@is_owner()
	async def config_bot_list(self,ctx:SlashContext):
		await ctx.send(embed=discord.Embed(title='Config:',description='\n'.join([f"{i}:{data['botConfig'][i]}" for i in data['botConfig']]),color=0x69ff69))
		general.logOutput(f'bot config list requested',ctx)
	@cog_ext.cog_subcommand(base='config',subcommand_group='server',name='list',description='list config variables. (requires moderator)')
	@modOrOwner()
	async def config_server_list(self,ctx:SlashContext):
		await ctx.send(embed=discord.Embed(title='Config:',description='\n'.join([f"{i}:{data['servers'][str(ctx.guild.id)]['config'][i]}" for i in data['servers'][str(ctx.guild.id)]['config']]),color=0x69ff69))
		general.logOutput(f'server config list requested',ctx)
	@cog_ext.cog_slash(name='exec',description='execute any python command on host computer.')
	@is_owner()
	async def execute(self,ctx:SlashContext,function):
		await ctx.send(str(eval(function)),hidden=True)
		general.logOutput(f'{function} executed',ctx)
	@cog_ext.cog_slash(name='roll',description='roll with modifiers')
	async def roll(self,ctx:SlashContext,dice:int,sides:int,modifiers:int=0):
		try: maxRoll = data['servers'][str(ctx.guild.id)]['config']['maxRoll']
		except: maxRoll = 16384
		await ctx.defer()
		if dice > maxRoll or sides > maxRoll or dice < 0 or sides < 0: await ctx.send(f'rolls must be between 0 and {maxRoll}!'); return
		result = modifiers
		rolls = []
		for i in range(dice): roll = randint(1,sides); rolls.append(str(roll)); result+=roll
		try: await ctx.send(embed=discord.Embed(title=f'roll: {dice}d{sides}+{modifiers}' if modifiers>0 else f'roll: {dice}d{sides}',color=0x69ff69).add_field(name='rolls:',value=f'[{",".join(rolls)}]',inline=False).add_field(name='Result:',value=result,inline=False))
		except: await ctx.send(embed=discord.Embed(title=f'roll: {dice}d{sides}+{modifiers}' if modifiers>0 else f'roll: {dice}d{sides}',color=0x69ff69).add_field(name='rolls:',value='total rolls above character limit.',inline=False).add_field(name='Result:',value=result,inline=False))
		general.logOutput(f'roll {dice}d{sides}+{modifiers} requested',ctx)
	@cog_ext.cog_subcommand(base='leaderboard',name='messages',description='leaderboard of total messages sent.')
	async def leaderboard_messages(self,ctx:SlashContext):
		data['variables']['messages'] = {key: value for key, value in sorted(data['variables']['messages'].items(), key=lambda item: item[1],reverse=True)}
		names = []
		index = 1
		await ctx.defer()
		for member in data['variables']['messages']:
			if member not in data['variables']['idNameCache']: data['variables']['idNameCache'][member] = (await client.fetch_user(member)).name
			rank = str(index)+("th" if 4<=index%100<=20 else {1:"st",2:"nd",3:"rd"}.get(index%10, "th")); index += 1
			names.append(f"{rank} - {data['variables']['idNameCache'][member]}: {data['variables']['messages'][member]}")
		await ctx.send(embed=discord.Embed(title='Messages:',description='\n'.join(names),color=0x69ff69))
		general.logOutput(f'message leaderboard requested',ctx)
	@cog_ext.cog_subcommand(base='get',name='avatar',description='returns the avatar of given user')
	async def get_avatar(self,ctx:SlashContext,user:discord.User,resolution=512):
		if isinstance(user,int): user = await client.fetch_user(user)
		await ctx.send(embed=discord.Embed(title=f'{user.name}\'s avatar',color=0x69ff69).set_image(url=str(user.avatar_url_as(format="png",size=int(resolution)))))
		general.logOutput(f'avater of {user.name} requested',ctx)
	@cog_ext.cog_subcommand(base='get',name='guild',description='returns guild name from id')
	async def get_guild(self,ctx:SlashContext,guild):
		await ctx.send((await client.fetch_guild(int(guild))).name)
		general.logOutput(f'guild {guild} requested',ctx)
	@cog_ext.cog_subcommand(base='get',name='name',description='returns user name from id')
	async def get_name(self,ctx:SlashContext,user):
		await ctx.send((await client.fetch_user(int(user))).name)
		general.logOutput(f'name of {user} requested',ctx)
	@cog_ext.cog_subcommand(base='get',name='variable',description='returns variable')
	@is_owner()
	async def get_variable(self,ctx:SlashContext,variable:str):
		if variable in bannedVariables: await ctx.send('no, fuck you.'); return
		try: variable = globals()[variable]
		except: await ctx.send('unknown variable name.'); return
		await ctx.send(f'```{type(variable)}\n{variable}```')
		general.logOutput(f'variable {variable} requested',ctx)
	@cog_ext.cog_subcommand(base='reginald',name='info',description='lists info on reginald.')
	async def reginald_info(self,ctx:SlashContext):
		embed = discord.Embed(title='Reginald Info:',description="""a mash up of the server mcstarter, the discipline sticc, and the mcfuck.\n
		please submit any issues using /reginald issue\n
		and if you have any suggestions, you can use /reginald suggest\n
		you can follow development here: https://discord.gg/4mteVXBDW7\n
		thank you, all hail reginald.""",color=0x69ff69)
		await ctx.send(embed=embed)
		general.logOutput(f'reginald info requested',ctx)
	@cog_ext.cog_subcommand(base='reginald',name='ignore',description='adds or removes user to reginald ignore list. (requires admin)',
	options=[create_option('mode','mode',3,True,['add','remove']),create_option('user','user',6,True)])
	@adminOrOwner()
	async def reginald_ignore(self,ctx:SlashContext,mode,user:discord.User):
		ignoreList = data['servers'][str(ctx.guild.id)]['ignore']
		match mode:
			case 'add':
				if user.id in ignoreList: await ctx.send('this user is already on the ignore list!'); return
				ignoreList.append(user.id)
				await ctx.send(f"successfully added {user.name} to ignore list.")
			case 'remove':
				if user.id not in ignoreList: await ctx.send('this user is not on the ignore list!'); return
				ignoreList.remove(user.id)
				await ctx.send(f"successfully removed {user.name} from ignore list.")
		data['servers'][str(ctx.guild.id)]['ignore'] = ignoreList
		general.logOutput(f'{user.name} added to ignore list',ctx)
class msgLogger(commands.Cog):
	def __init__(self,client): self.client = client
	@commands.Cog.listener()
	async def on_message(self,message):
		await msgLogger.logMessages(message,'s',' - image or embed') if message.content == "" else await msgLogger.logMessages(message,'s')
		try: msgLogger.messageCount(str(message.author.id), str(message.guild.id))
		except AttributeError or discord.errors.NotFound: pass
	@commands.Cog.listener()
	async def on_message_delete(self,message): await msgLogger.logMessages(message,'d',' - image or embed') if message.content == "" else await msgLogger.logMessages(message,'d')
	@commands.Cog.listener()
	async def on_bulk_message_delete(self,messages):
		for message in messages: await msgLogger.logMessages(message,'b',' - image or embed') if message.content == "" else await msgLogger.logMessages(message,'b')
	@commands.Cog.listener()
	async def on_message_edit(self,message_before,message_after):
		await msgLogger.logMessages(message_before,'e',message_after,' - image or embed') if message_after.content == "" else await msgLogger.logMessages(message_before,'e',message_after)
	def messageCount(author,guild=None):
		if author in data['variables']['messages']: data['variables']['messages'][author] += 1
		else: data['variables']['messages'].update({author:1})
		if guild != None:
			if author not in data['servers'][guild]['activeMembers'] and data['servers'][guild]['config']['enableTalkingStick']: data['servers'][guild]['activeMembers'].append(author)
		save()
	async def logMessages(ctx,type,ctx2=None,ext=''):
		match type:
			case 's':
				log=f'{ctx.author} sent "{ctx.content}" in {"" if ctx.guild == None else f"{ctx.guild} - "}{ctx.channel}{ext}'
				if data['botConfig']['msgToConsole'] and not (ctx.author.bot and not data['botConfig']['botToConsole']): print(f'{ctx.author.name} sent "{ctx.content}"')
				sentLog.warning(log)
			case 'd':
				log=f'"{ctx.content}" by {ctx.author} was deleted in {"" if ctx.guild == None else f"{ctx.guild} - "}{ctx.channel}{ext}'
				for attachment in ctx.attachments: await attachment.save(f'{os.getcwd()}\\fileCache\\{datetime.fromtimestamp(time()).strftime("%d.%m.%Y %H.%M.%S.%f")[:-4]}.{attachment.filename.split(".")[len(attachment.filename.split("."))-1]}',use_cached=True)
				if data['botConfig']['msgToConsole'] and not (ctx.author.bot and not data['botConfig']['botToConsole']): print(f'{ctx.author.name} - "{ctx.content}" was deleted')
				deletedLog.warning(log)
			case 'b':
				log=f'"{ctx.content}" by {ctx.author} was purged in {"" if ctx.guild == None else f"{ctx.guild} - "}{ctx.channel}{ext}'
				for attachment in ctx.attachments: await attachment.save(f'{os.getcwd()}\\fileCache\\{datetime.fromtimestamp(time()).strftime("%d.%m.%Y %H.%M.%S.%f")[:-4]}.{attachment.filename.split(".")[len(attachment.filename.split("."))-1]}',use_cached=True)
				if data['botConfig']['msgToConsole'] and not (ctx.author.bot and not data['botConfig']['botToConsole']): print(f'{ctx.author.name} - "{ctx.content}" was bulk deleted')
				deletedLog.warning(log)
			case 'e':
				if ctx.content == ctx2.content: return
				log=f'{ctx.author} edited "{ctx.content}" into "{ctx2.content}" in {"" if ctx.guild == None else f"{ctx.guild} - "}{ctx.channel}{ext}'
				if data['botConfig']['msgToConsole'] and not (ctx.author.bot and not data['botConfig']['botToConsole']): print(f'{ctx.author.name} edited "{ctx.content}" into {ctx2.content}')
				editedLog.warning(log)
class general(commands.Cog):
	def __init__(self,client): self.client = client
	@commands.Cog.listener()
	async def on_ready(self):
		outputLog.warning(f"{client.user.name} connected to Discord!")
		print(f"{client.user.name} connected to Discord!\n")
		await client.change_presence(activity=discord.Activity(type=discord.ActivityType.custom, name='the collective one.'))
		await slash.sync_all_commands()
	@commands.Cog.listener()
	async def on_guild_join(self,guild):
		try: await (discord.utils.get(guild.channels,name='general')).send(file=discord.File('reginald.png'))
		except: pass
		data['servers'][str(guild.id)] = data['defaultServer']
		async for member in guild.fetch_members():
			if str(member.id) in data['users'] and str(guild.id) not in data['users'][str(member.id)]['guilds']: data['users'][str(member.id)]['guilds'].append(str(guild.id))
			else: data['users'].update({str(member.id):{'guilds':[str(guild.id)],'birthday':None}})
		save()
	@commands.Cog.listener()
	async def on_member_join(self,member):
		if str(member.id) in data['users'] and str(member.guild.id) not in data['users'][str(member.id)]['guilds']: data['users'][str(member.id)]['guilds'].append(str(member.guild.id))
		else: data['users'].update({str(member.id):{'guilds':[str(member.guild.id)],'birthday':None}})
		save()
	@commands.Cog.listener()
	async def on_member_leave(member):
		if str(member.id) in data['users'] and str(member.guild.id) in data['users'][str(member.id)]['guilds']: data['users'][str(member.id)]['guilds'].remove(str(member.guild.id))
	@commands.Cog.listener()
	async def on_message(self,ctx):
		try: guild = data['servers'][str(ctx.guild.id)]
		except AttributeError: guild=data['defaultServer']; return
		if ctx.author.id in guild['ignore'] or ctx.author == client.user: return
		if guild['config']['enableAutoResponses'] and not ctx.author.bot: await general.autoResponse(ctx)
		if guild['config']['enableDadBot']: await general.dadBot(ctx)
	async def autoResponse(ctx):
		if data['servers'][str(ctx.guild.id)]['config']['enableAutoResponses'] and not ctx.author.bot:
			if ctx.author.id == client.owner_id and ctx.content in userqa and not data['servers'][str(ctx.guild.id)]['config']['godExempt']: await ctx.channel.send(userqa[ctx.content]); return
			if ctx.author.id == client.owner_id and ctx.content in fileqa and not data['servers'][str(ctx.guild.id)]['config']['godExempt']: await ctx.channel.send(file=discord.File(f'{os.getcwd()}\\memes\\{fileqa[ctx.content]}'))
			if ctx.author.id != client.owner_id and ctx.content in userqa: await ctx.channel.send(userqa[ctx.content]); return
			if ctx.author.id == client.owner_id and ctx.content in godqa: await ctx.channel.send(godqa[ctx.content])
	async def dadBot(ctx):
		if ctx.author.bot or (ctx.author.id == client.owner_id and data['servers'][str(ctx.guild.id)]['config']['godExempt']): return
		message = re.sub(r'<(@!|@)\d{18}>','[REDACTED]',ctx.content)
		for splitter in splitters:
			split = message.split(splitter)
			if len(split) > 1: break
		else: return
		await ctx.channel.send(f"Hi {splitter.join(split[1:])}, {splitter}dad.")
	def logOutput(log,ctx):
		try: log = f'{log} in {ctx.guild.name} by {ctx.author.name}'
		except: log = f'{log} in DMs with {ctx.author.name}'
		outputLog.warning(log)
		if data['botConfig']['outputToConsole']: print(log)
class development(commands.Cog):
	def __init__(self,client): self.client = client
	@cog_ext.cog_subcommand(base='reginald-dev',name='commit',description='push a commit to the change-log channel',guild_ids=[844127424526680084])
	@is_owner()
	async def reginald_dev_commit(self,ctx:SlashContext,title,features,fixes,newversion:bool=True):
		if newversion: data['information']['version'] += 0.01
		version = data['information']['version']
		features = '- ' + '\n- '.join(features.split(r'\n'))
		fixes = '- ' + '\n- '.join(fixes.split(r'\n'))
		channel = await client.fetch_channel(data['information']['change-log-channel'])
		message = await channel.send(embed=discord.Embed(title=title,description=f'version: {version}\n\nfeatures:\n{features}\n\nfixes:\n{fixes}\n\nthese features are new, remember to report bugs with /reginald issue',color=0x69ff69))
		await message.publish()
		await ctx.send('successfully pushed change.')
		general.logOutput(f'new commit pushed',ctx)
	@cog_ext.cog_subcommand(base='reginald',name='suggest',description='suggest a feature for reginald')
	async def reginald_suggest(self,ctx:SlashContext,suggestion,details):
		channel = await client.fetch_channel(data['information']['suggestions-channel'])
		message = await channel.send(embed=discord.Embed(title=suggestion,description=f'suggested by: {ctx.author.mention}\n\ndetails:\n{details}',color=0x69ff69))
		for i in ['👍','👎']: await message.add_reaction(i)
		await ctx.send('thank you for your suggestion!')
		general.logOutput(f'new suggestion {suggestion}',ctx)
	@cog_ext.cog_subcommand(base='reginald',name='issue',description='report an issue with reginald')
	async def reginald_issue(self,ctx:SlashContext,issue,details):
		channel = await client.fetch_channel(data['information']['issues-channel'])
		message = await channel.send(embed=discord.Embed(title=issue,description=f'suggested by: {ctx.author.mention}\n\nhow to replicate:\n{details}',color=0x69ff69))
		for i in ['👍','👎']: await message.add_reaction(i)
		await ctx.send('thank you for reporting this issue!')
		general.logOutput(f'new issue {issue}',ctx)
	@cog_ext.cog_subcommand(base='reginald-dev',name='initguild',description='Initialize current guild.',guild_ids=[559830737889787924,786716046182187028])
	@is_owner()
	async def reginald_dev_initguild(self,ctx:SlashContext):
		await ctx.send('initalizing guild...')
		async for member in ctx.guild.fetch_members():
			if str(member.id) in data['users'] and str(ctx.guild.id) not in data['users'][str(member.id)]['guilds']: data['users'][str(member.id)]['guilds'].append(str(ctx.guild.id))
			else: data['users'].update({str(member.id):{'guilds':[str(ctx.guild.id)],'birthday':None}})
			await ctx.channel.send(f'initalized {member.name}...')
		save()
		await ctx.channel.send('initialization complete.')
	@cog_ext.cog_subcommand(base='reginald-dev',name='test',description='used for testing',guild_ids=[786716046182187028])
	@is_owner()
	async def reginald_dev_test(self,ctx:SlashContext):
		await ctx.send('[this is a hyperlink test](<https://www.youtube.com/watch?v=dQw4w9WgXcQ>)')
class birthdays(commands.Cog):
	def __init__(self,client): self.client = client
	@cog_ext.cog_subcommand(base='birthday',name='setup',description='setup auto birthdays. (requires admin)')
	@adminOrOwner()
	@guild_only()
	async def birthday_setup(self,ctx:SlashContext,role:discord.Role,channel:discord.TextChannel):
		if not data['servers'][str(ctx.guild.id)]['config']['enableBirthdays']: await ctx.send(embed=discord.Embed(title='Birthdays is not enabled on this server.',color=0x69ff69)); return
		data['servers'][str(ctx.guild.id)]['birthdayRole'] = role.id
		data['servers'][str(ctx.guild.id)]['birthdayChannel'] = channel.id
		await ctx.send(f'successfully set birthday role to {role.mention} and birthday channel to {channel.mention}')
		general.logOutput(f'birthday role set to {role.name}',ctx)
	@cog_ext.cog_subcommand(base='birthday',name='set',description='setup birthday role')
	async def birthday_set(self,ctx:SlashContext,month,day):
		data['users'][str(ctx.author.id)]['birthday'] = f'{month.zfill(2)}/{day.zfill(2)}'
		await ctx.send(f"birthday successfully set to {data['users'][str(ctx.author.id)]['birthday']}")
		general.logOutput(f"birthday set to {data['users'][str(ctx.author.id)]['birthday']}",ctx)
	@cog_ext.cog_subcommand(base='birthday',name='reset',description='reset your birthday')
	async def birthday_remove(self,ctx:SlashContext):
		data['users'][str(ctx.author.id)]['birthday'] = None
		await ctx.send(f'birthday successfully reset')
		general.logOutput(f'birthday reset',ctx)
	async def birthdayLoop():
		await client.wait_until_ready()
		oldDate = None
		while client.is_ready:
				await asyncio.sleep(300)
				date = datetime.now().strftime('%m/%d')
				if date != oldDate:
					for user in data['users']:
						if user == 'default' or user in data['variables']['activeBirthdays']: continue
						if data['users'][user]['birthday'] == date:
							for guild in data['users'][user]['guilds']:
								if not data['servers'][guild]['config']['enableBirthdays']: continue
								server = await client.fetch_guild(int(guild))
								if data['servers'][guild]['birthdayRole'] == 0 or data['servers'][guild]['birthdayChannel'] == 0:
									await (await server.fetch_member(server.owner_id)).send(f'error in birthday loop. please redo setup or move birthday role below reginald role in {server.name}.')
									continue
								member = await server.fetch_member(user)
								await member.add_roles(discord.Object(data['servers'][guild]['birthdayRole']))
								data['variables']['activeBirthdays'].append(user)
								await (await client.fetch_channel(data['servers'][guild]['birthdayChannel'])).send(f'Happy Birthday {member.mention}!')
					for user in data['variables']['activeBirthdays']:
						if date != data['users'][user]['birthday']:
							for guild in data['users'][user]['guilds']:
								if not data['servers'][guild]['config']['enableBirthdays']: continue
								server = await client.fetch_guild(int(guild))
								if data['servers'][guild]['birthdayRole'] == 0 or data['servers'][guild]['birthdayChannel'] == 0:
									await (await server.fetch_member(server.owner_id)).send(f'error in birthday loop. please redo setup or move birthday role below reginald role in {server.name}.')
									continue
								member = await server.fetch_member(user)
								await member.remove_roles(discord.Object(data['servers'][guild]['birthdayRole']))
								data['variables']['activeBirthdays'].remove(user)
					oldDate = date
class crypto(commands.Cog):
	def __init__(self,client): self.client = client
	@cog_ext.cog_subcommand(base='crypto',subcommand_group='calculate',name='zano',description='calculate zano stats')
	async def crypto_calculate_zano(self,ctx:SlashContext,hashrate:float,holdings:float):
		try: exchRate = float(json.loads(requests.get('https://api.coingecko.com/api/v3/coins/zano').text)['market_data']['current_price']['usd']); zanoExplorer = json.loads(requests.get('https://explorer.zano.org/api/get_info/4294967295').text)['result']
		except: await ctx.send('failed to fetch exchange rate',hidden=True); return
		hashrate = float(hashrate); holdings = float(holdings)
		response = []
		response.append(f'Your hashrate: {hashrate} MH/s')
		response.append(f'Your holdings: {holdings} Zano')
		response.append(f'Your USD: ${holdings*exchRate}')
		hashrate = hashrate*1000000
		posDiff = int(zanoExplorer['pos_difficulty'])
		networkHash = int(zanoExplorer['current_network_hashrate_350'])
		timeToBlock = round(100/(hashrate/networkHash*100/2),2)
		zanoDay = round(1440/(100/(hashrate/networkHash*100)),3)/2
		usdDay = round(1440/(100/(hashrate/networkHash*100))*exchRate,3)/2
		response.append(f'Network hashrate: {round(networkHash/1000000000,3)} GH/s')
		response.append(f'Zano price: ${format(exchRate,".3f")}')
		response.append(f'Chance of mining next block: {format(round(hashrate/networkHash*100/2,3),".3f")}%')
		response.append(f'Est. time to mine block: {timeToBlock} minutes | {round(timeToBlock/60,2)} hours')
		response.append(f'Est. PoS Earnings: {round(holdings*720/(posDiff/1000000000000/100),5)} Zano')
		response.append(f'Zano/day: {zanoDay}')
		response.append(f'Zano/month: {round(zanoDay*30,3)}')
		response.append(f'Zano/year: {round(zanoDay*365,3)}')
		response.append(f'USD/day: ${usdDay}')
		response.append(f'USD/month: ${round(usdDay*30,3)}')
		response.append(f'USD/year: ${round(usdDay*365,3)}')
		await ctx.send(embed=discord.Embed(title='Your Zano Stats:',description='\n'.join(response),color=0x69ff69))
		general.logOutput(f'zano stats requested',ctx)
	@cog_ext.cog_subcommand(base='crypto',name='exchange',description='get worth of currency in usd.')
	async def crypto_exchange(self,ctx:SlashContext,coin,amount):
		try: exchRate = float(json.loads(requests.get(f'https://api.coingecko.com/api/v3/coins/{coin.lower()}').text)['market_data']['current_price']['usd'])
		except: await ctx.send('failed to fetch exchange rate. is the coin name correct?',hidden=True); return
		await ctx.send(f'{format(float(amount),",.3f")} {coin} = ${format(exchRate*int(amount),",.3f")} USD')
		general.logOutput(f'exchange rate for {amount} {coin}',ctx)
@client.event
async def on_command_error(ctx,error): await ctx.send('all commands have been ported to slash commands, type "/" to see a list of commands.')
@client.event
async def on_slash_command_error(ctx:SlashContext,error): await ctx.send(str(error),hidden=True); print(error)
@client.command(name='test')
async def nonSlashTest(ctx): await ctx.channel.send('pp')

client.loop.create_task(theDisciplineSticc.sticcLoop())
client.loop.create_task(birthdays.birthdayLoop())
client.add_cog(theDisciplineSticc(client))
client.add_cog(serverMcstarter(client))
client.add_cog(development(client))
client.add_cog(birthdays(client))
client.add_cog(msgLogger(client))
client.add_cog(command(client))
client.add_cog(general(client))
client.add_cog(crypto(client))

try: client.run(os.getenv('token'))
finally: save()