import os,re,json,logging,discord,asyncio
from discord_slash.utils.manage_commands import create_option
from mcrcon import MCRcon
from random import randint
from shutil import copytree
from time import time,sleep
from datetime import datetime
from dotenv import load_dotenv
# from serverConnection import client
from mcstatus import MinecraftServer
from discord.ext import commands
from discord_slash import cog_ext,SlashCommand,SlashContext
from discord.ext.commands import has_permissions,is_owner

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
except: data = {"defaultServer":{"config":{"godExempt":True,"enableAutoResponses":True,"enableTalkingStick":True,"maxServerStartTime":90,"maxRoll":16384},"activeMembers":[],"tsLeaderboard":{},"tsRole":0,"tsChannel":0,"currentStik":0},"variables":{"idNameCache":{},"messages":{}},"servers":{}}
try: ricePurityFile = json.loads(open('ricePurity.json','r',1,'utf-8').read())
except: print('error loading rice purity'); pass
serverStarted=False
sizes={2:'MBs',3:'GBs'}
mainDirectory = os.getcwd()
splitters = ["I'm ","i'm "," im ",' Im ',"i am ","I am ","I'M "," IM ","I AM "]
hypixelKey=os.getenv('hypixelKey')
serverQuery=os.getenv('serverQuery')
servers = json.loads(open('servers.json','r').read())
outputLog=setupLogger('output log','logs/output.log')
sentLog=setupLogger('sent log','logs/messages/sent.log')
editedLog=setupLogger('edited log','logs/messages/edited.log')
deletedLog=setupLogger('deleted log','logs/messages/deleted.log')
valueConverter={'True':True,'False':False,'true':True,'false':False}
bannedVariables=['__file__','qa','userqa','godqa','hypixelKey','servers']
qa=json.loads(open('qa.json','r').read()); userqa = qa['userqa']; godqa = qa['godqa']; fileqa = qa['fileqa']
mc=MCRcon(os.getenv('mcRconHost'),os.getenv('mcRconPassword'),int(os.getenv('mcRconPort')))
client=commands.Bot(command_prefix=('reginald!','reg!','r!'),case_insensitive=True,help_command=None,owner_id=250797109022818305)
slash=SlashCommand(client)


def adminOrOwner(): return (is_owner() or has_permissions(administrator=True))
def modOrOwner(): return (is_owner() or has_permissions(manage_server=True))
def save(): json.dump(data,open('save.json','w+'),indent=2)

class serverMcstarter(commands.Cog):
	def __init__(self,client): self.client = client
	@cog_ext.cog_subcommand(base='minecraft',name='start',description='starts a minecraft server.')
	async def start(self,ctx:SlashContext,server):
		await ctx.send('most of reginald is disabled right now, it should be back in a few weeks, send any emergency issues to https://github.com/TyrantLink/reginald/issues'); return
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
		general.logOutput(f'starting server {server} in {ctx.guild.name} by {ctx.author.name}')
	@cog_ext.cog_subcommand(base='minecraft',name='stop',description='stops active minecraft server.')
	async def stop(self,ctx:SlashContext,args=None):
		await ctx.send('most of reginald is disabled right now, it should be back in a few weeks, send any emergency issues to https://github.com/TyrantLink/reginald/issues'); return
		if args == '-f' and not adminOrOwner():
			if MinecraftServer.lookup(serverQuery).query().players.online > 0: await ctx.send('no, fuck you, there are people online.'); return False
		try: mc.connect(); mc.command('stop'); mc.disconnect(); serverStarted = False; await client.change_presence(activity=discord.Game('Server Stopped')); await ctx.send('stopping server.')
		except: await ctx.send('failed to shutdown server.'); return False
		general.logOutput(f'starting server {server} in {ctx.guild.name} by {ctx.author.name}')
	@cog_ext.cog_subcommand(base='minecraft',name='cmd',description='runs command on the active minecraft server.')
	@is_owner()
	async def cmd(self,ctx:SlashContext,command):
		await ctx.send('most of reginald is disabled right now, it should be back in a few weeks, send any emergency issues to https://github.com/TyrantLink/reginald/issues'); return
		try: mc.connect(); response = mc.command(command); mc.disconnect()
		except: await ctx.send('failed to send command'); return
		try: await ctx.send(re.sub('§.','',response))
		except: pass
		general.logOutput(f'command {command} run in {ctx.guild.name} by {ctx.author.name}')
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
		general.logOutput(f'info about server {server} requested in {ctx.guild.name} by {ctx.author.name}')
	@cog_ext.cog_subcommand(base='minecraft',name='online',description='returns list of players online.')
	async def online(self,ctx:SlashContext):
		try: players = MinecraftServer.lookup(serverQuery).query().players.names
		except: await ctx.send('cannot connect to server. is it online?'); return
		if players == []: await ctx.send('no one is online.'); return
		await ctx.send(embed=discord.Embed(title='Players Online:',description='\n'.join(players),color=0x69ff69))
		general.logOutput(f'online players requested in {ctx.guild.name} by {ctx.author.name}')
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
	@cog_ext.cog_subcommand(base='sticc',name='setup',description='setup the discipline sticc.')
	@adminOrOwner()
	async def setup(self,ctx:SlashContext,role:discord.Role,channel:discord.TextChannel):
		await ctx.send('most of reginald is disabled right now, it should be back in a few weeks, send any emergency issues to https://github.com/TyrantLink/reginald/issues'); return
		if not data['servers'][str(ctx.guild.id)]['config']['enableTalkingStick']: await ctx.send(embed=discord.Embed(title='The Talking Stick is not enabled on this server.',color=0x69ff69)); return
		data['servers'][str(ctx.guild.id)]['tsRole'] = role.id
		data['servers'][str(ctx.guild.id)]['tsChannel'] = channel.id
		await ctx.send(embed=discord.Embed(title='Setup Complete.',description=f'role: <@&{role.id}>\n\nchannel: <#{channel.id}>',color=0x69ff69))
		general.logOutput(f'talking stick setup in {ctx.guild.name} by {ctx.author.name}')
	@cog_ext.cog_subcommand(base='sticc',name='reroll',description='reroll the talking sticc')
	@adminOrOwner()
	async def reroll(self,ctx:SlashContext):
		if not data['servers'][str(ctx.guild.id)]['config']['enableTalkingStick']: await ctx.send(embed=discord.Embed(title='The Talking Stick is not enabled on this server.',color=0x69ff69)); return
		await theDisciplineSticc.rollTalkingStick(str(ctx.guild.id))
		await ctx.send('reroll successful.')
		general.logOutput(f'talking stick reroll in {ctx.guild.name} by {ctx.author.name}')
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
		general.logOutput(f'stick leaderboard requested in {ctx.guild.name} by {ctx.author.name}')
	@cog_ext.cog_subcommand(base='sticc',name='active',description='lists members who have been active in the past day.')
	async def list_active(self,ctx:SlashContext):
		if not data['servers'][str(ctx.guild.id)]['config']['enableTalkingStick']: await ctx.send(embed=discord.Embed(title='The Talking Stick is not enabled on this server.',color=0x69ff69)); return
		active = []
		await ctx.defer()
		for member in data['servers'][str(ctx.guild.id)]['activeMembers']:
			if member not in data['variables']['idNameCache']: data['variables']['idNameCache'][member] = (await client.fetch_user(member)).name
			active.append(data['variables']['idNameCache'][member])
		await ctx.send(embed=discord.Embed(title='Active Members:',description='\n'.join(active),color=0x69ff69))
		general.logOutput(f'active users requested in {ctx.guild.name} by {ctx.author.name}')
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
		general.logOutput(f'{ctx.author.name} said hi to reginald in {ctx.guild.name}')
	@cog_ext.cog_slash(name='clearidcache',description='clears ID cache variable')
	@is_owner()
	async def clearIDcache(self,ctx:SlashContext):
		data['variables']['idNameCache'] = {}
		await ctx.send('successfully cleared ID cache')
		save()
		general.logOutput(f'idNameCache cleared in {ctx.guild.name} by {ctx.author.name}')
	@cog_ext.cog_subcommand(base='config',subcommand_group='bot',name='set',description='set variables for the bot',options=[create_option('variable','see current value with /config bot list',3,True,list(data['botConfig'].keys())),create_option('value','bool or int',5,True)])
	@is_owner()
	async def config_bot_set(self,ctx:SlashContext,variable,value):
		data['botConfig'][variable] = value
		await ctx.send(f"successfully set {variable} to {data['botConfig'][variable]}")
		save()
		general.logOutput(f'bot config {variable} set to {str(value)} in {ctx.guild.name} by {ctx.author.name}')
	@cog_ext.cog_subcommand(base='config',subcommand_group='server',name='set',description='set variables for the bot',options=[create_option('variable','see current value with /config server list',3,True,list(data['defaultServer']['config'].keys())),create_option('value','bool or int',3,True)])
	@adminOrOwner()
	async def config_server_set(self,ctx:SlashContext,variable,value):
		await ctx.send('most of reginald is disabled right now, it should be back in a few weeks, send any emergency issues to https://github.com/TyrantLink/reginald/issues'); return
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
		general.logOutput(f'server config {variable} set to {str(value)} in {ctx.guild.name} by {ctx.author.name}')
	@cog_ext.cog_slash(name='reload',description='reloads save files')
	@is_owner()
	async def reloadSaves(self,ctx:SlashContext):
		global qa,userqa,godqa,fileqa,servers
		qa = json.loads(open('qa.json','r').read()); userqa = qa['userqa']; godqa = qa['godqa']; fileqa = qa['fileqa']
		servers = json.loads(open('servers.json','r').read())
		await ctx.send('reload successful.')
		general.logOutput(f'reloaded saves in {ctx.guild.name} by {ctx.author.name}')
	@cog_ext.cog_subcommand(base='config',subcommand_group='bot',name='list',description='list config variables.')
	@is_owner()
	async def config_bot_list(self,ctx:SlashContext):
		await ctx.send(embed=discord.Embed(title='Config:',description='\n'.join([f"{i}:{data['botConfig'][i]}" for i in data['botConfig']]),color=0x69ff69))
		general.logOutput(f'bot config list requested in {ctx.guild.name} by {ctx.author.name}')
	@cog_ext.cog_subcommand(base='config',subcommand_group='server',name='list',description='list config variables.')
	@modOrOwner()
	async def config_server_list(self,ctx:SlashContext):
		await ctx.send(embed=discord.Embed(title='Config:',description='\n'.join([f"{i}:{data['servers'][str(ctx.guild.id)]['config'][i]}" for i in data['servers'][str(ctx.guild.id)]['config']]),color=0x69ff69))
		general.logOutput(f'server config list requested in {ctx.guild.name} by {ctx.author.name}')
	@cog_ext.cog_slash(name='exec',description='execute any python command on host computer.')
	@is_owner()
	async def execute(self,ctx,function):
		try: await ctx.send(eval((' '.join(function))))
		except Exception as e: await ctx.send(e)
		general.logOutput(f'{" ".join(function)} executed in {ctx.guild.name} by {ctx.author.name}')
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
		general.logOutput(f'roll {dice}d{sides}+{modifiers} requested in  {ctx.guild.name} by {ctx.author.name}')
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
		general.logOutput(f'message leaderboard requested in {ctx.guild.name} by {ctx.author.name}')
	@cog_ext.cog_subcommand(base='get',name='avatar',description='returns the avatar of given user')
	async def get_avatar(self,ctx:SlashContext,user:discord.User,resolution=512):
		if isinstance(user,int): user = await client.fetch_user(user)
		await ctx.send(embed=discord.Embed(title=f'{user.name}\'s avatar',color=0x69ff69).set_image(url=str(user.avatar_url_as(format="png",size=int(resolution)))))
		general.logOutput(f'avater of {user.name} requested in {ctx.guild.name} by {ctx.author.name}')
	@cog_ext.cog_subcommand(base='get',name='guild',description='returns guild name from id')
	async def get_guild(self,ctx:SlashContext,guild):
		await ctx.send((await client.fetch_guild(int(guild))).name)
		general.logOutput(f'guild {guild} requested in {ctx.guild.name} by {ctx.author.name}')
	@cog_ext.cog_subcommand(base='get',name='name',description='returns user name from id')
	async def get_name(self,ctx:SlashContext,user):
		await ctx.send((await client.fetch_user(int(user))).name)
		general.logOutput(f'name of {user} requested in {ctx.guild.name} by {ctx.author.name}')
	@cog_ext.cog_subcommand(base='get',name='variable',description='returns variable')
	@is_owner()
	async def get_variable(self,ctx:SlashContext,variable:str):
		if variable in bannedVariables: await ctx.send('no, fuck you.'); return
		try: variable = globals()[variable]
		except: await ctx.send('unknown variable name.'); return
		await ctx.send(f'```{type(variable)}\n{variable}```')
		general.logOutput(f'variable {variable} requested in {ctx.guild.name} by {ctx.author.name}')
	@cog_ext.cog_subcommand(base='reginald',name='info',description='lists info on reginald.')
	async def reginald_info(self,ctx:SlashContext):
		embed = discord.Embed(title='Reginald Info:',description="""a fucked up mash up of the server mcstarter, the discipline sticc, and the mcfuck.\n
		please submit any issues to https://github.com/TyrantLink/reginald/issues/\n
		thank you, all hail reginald.""",color=0x69ff69)
		await ctx.send(embed=embed)
		general.logOutput(f'reginald info requested in {ctx.guild.name} by {ctx.author.name}')
	@cog_ext.cog_subcommand(base='reginald',name='ignore',description='adds or removes user to reginald ignore list (auto responses, dadBot, talking stick rolls, etc.)',
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
		general.logOutput(f'{user.name} added to ignore list in {ctx.guild.name} by {ctx.author.name}')
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
		await (discord.utils.get(guild.channels,name='general')).send(file=discord.File('reginald.png'))
		data['servers'][str(guild.id)] = data['defaultServer']
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
		if ctx.author.id == client.owner_id and data['servers'][str(ctx.guild.id)]['config']['godExempt']: return
		for splitter in splitters:
			split = ctx.content.split(splitter)
			if len(split) > 1: break
		else: return
		await ctx.channel.send(f"Hi {splitter.join(split[1:])}, {splitter}dad.")
	def logOutput(log):
		outputLog.warning(log)
		if data['botConfig']['outputToConsole']: print(log)
@client.event
async def on_command_error(ctx,error): await ctx.send('all commands have been ported to slash commands, type "/" to see a list of commands.')
@client.event
async def on_slash_command_error(ctx:SlashContext,error): await ctx.send(str(error),hidden=True); print(error)
@client.command(name='test')
async def nonSlashTest(ctx): await ctx.channel.send('pp')

client.loop.create_task(theDisciplineSticc.sticcLoop())
client.add_cog(theDisciplineSticc(client))
client.add_cog(serverMcstarter(client))
client.add_cog(msgLogger(client))
client.add_cog(command(client))
client.add_cog(general(client))

try: client.run(os.getenv('token'))
finally: save()