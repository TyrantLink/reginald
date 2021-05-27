import os,re,json,discord,asyncio
from time import time
from random import randint
from shutil import copytree
from datetime import datetime
from discord_slash.utils.manage_commands import create_option
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext.commands import *
from logger import outputLog,logOutput
from discord_slash import cog_ext,SlashCommand,SlashContext

load_dotenv()
extentions = ['birthdays','cmds','config','crypto','devTools','fun','msgLogger','ricePurity','serverMcstarter','theDisciplineSticc','versus']

try: data = json.loads(open('save.json','r').read())
except: data = json.loads(open('save.json.default','r').read())
quotes = json.loads(open('quotes.json','r').read())
issues = json.loads(open('issues.json','r').read())
hypixelKey=os.getenv('hypixelKey')
serverQuery=os.getenv('serverQuery')
servers=json.loads(open('servers.json','r').read())
questions = json.loads(open('questions.json','r').read())
qa = json.loads(open('qa.json','r').read()); userqa = qa['userqa']; godqa = qa['godqa']; fileqa = qa['fileqa']
bannedVariables=['__file__','qa','userqa','godqa','fileqa','hypixelKey','servers','bannedVariables']
splitters=["I'm ","i'm "," im ",' Im ',"i am ","I am ","I'M "," IM ","I AM "]

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
def save(file): json.dump(file,open('save.json','w+'),indent=2)
def load_extentions(extentions:list): [client.load_extension(f'classes.{extention}') for extention in extentions]

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
		save(data)
	@commands.Cog.listener()
	async def on_member_join(self,member):
		if str(member.id) in data['users'] and str(member.guild.id) not in data['users'][str(member.id)]['guilds']: data['users'][str(member.id)]['guilds'].append(str(member.guild.id))
		else: data['users'].update({str(member.id):{'guilds':[str(member.guild.id)],'birthday':None}})
		save(data)
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
			if ctx.author.id == client.owner_id and ctx.content in userqa and not data['botConfig']['godExempt']: await ctx.channel.send(userqa[ctx.content]); return
			if ctx.author.id == client.owner_id and ctx.content in fileqa and not data['botConfig']['godExempt']: await ctx.channel.send(file=discord.File(f'{os.getcwd()}\\memes\\{fileqa[ctx.content]}')); return
			if ctx.author.id != client.owner_id and ctx.content in userqa: await ctx.channel.send(userqa[ctx.content]); return
			if ctx.author.id != client.owner_id and ctx.content in fileqa: await ctx.channel.send(file=discord.File(f'{os.getcwd()}\\memes\\{fileqa[ctx.content]}')); return
			if ctx.author.id == client.owner_id and ctx.content in godqa: await ctx.channel.send(godqa[ctx.content])
	async def dadBot(ctx):
		if ctx.author.bot or (ctx.author.id == client.owner_id and data['botConfig']['godExempt']): return
		message = re.sub(r'<(@!|@)\d{18}>','[REDACTED]',ctx.content)
		for splitter in splitters:
			split = message.split(splitter)
			if len(split) > 1: break
		else: return
		await ctx.channel.send(re.sub('  ',' ',f"Hi {splitter.join(split[1:])}, {splitter}dad."))
	@cog_ext.cog_subcommand(base='reginald',subcommand_group='reload',name='qa',description='reloads save files')
	@is_owner()
	async def reginald_reload_qa(self,ctx:SlashContext):
		global qa,userqa,godqa,fileqa
		qa = json.loads(open('qa.json','r').read()); userqa = qa['userqa']; godqa = qa['godqa']; fileqa = qa['fileqa']
		await ctx.send('reload successful.')
		logOutput(f'reloaded qa',ctx)
	@cog_ext.cog_subcommand(base='reginald',subcommand_group='reload',name='extention',description='reloads given extention',options=[create_option('extention','extention to reload',str,True,extentions),create_option('resync','do you want to resync commands',bool,False)])
	@is_owner()
	async def reginald_reload_extention(self,ctx:SlashContext,extention:str,resync:bool=False):
		client.unload_extension(f'classes.{extention}')
		client.load_extension(f'classes.{extention}')
		await ctx.send(f'successfully reloaded {extention} extention')
		if resync: await slash.sync_all_commands()
		logOutput(f'reloaded {extention} extention',ctx)
class loops():
	async def nineLoop():
		await client.wait_until_ready()
		while client.is_ready:
				await asyncio.sleep(60)
				if datetime.now().strftime("%H:%M") == '09:00':
					for guild in data['servers']:
						server = await client.fetch_guild(int(guild))
						if (data['servers'][guild]['tsRole'] == 0 or data['servers'][guild]['tsChannel'] == 0) and data['servers'][guild]['config']['enableTalkingStick']:
							await (await server.fetch_member(server.owner_id)).send(f'error in talking stick. please redo setup in {server.name}.')
						elif data['servers'][guild]['config']['enableTalkingStick']: await loops.rollTalkingStick(guild)
						if data['servers'][guild]['qotdChannel'] == 0 and data['servers'][guild]['config']['enableQOTD']:
							await (await server.fetch_member(server.owner_id)).send(f'error in QOTD. please redo setup in {server.name}.')
						elif data['servers'][guild]['config']['enableQOTD']: await (await client.fetch_channel(data['servers'][guild]['qotdChannel'])).send(embed=discord.Embed(title='❓❔ Question of the Day ❔❓',description=questions[randint(0,len(questions))]))
						if data['servers'][guild]['quotesChannel'] == 0 and data['servers'][guild]['config']['enableQuotes']:
							await (await server.fetch_member(server.owner_id)).send(f'error in Quotes. please redo setup in {server.name}.')
						elif data['servers'][guild]['config']['enableQuotes']: await (await client.fetch_channel(data['servers'][guild]['qotdChannel'])).send(quotes[randint(0,len(quotes))])
					copytree(f'{os.getcwd()}\\logs',f'{os.getcwd()}\\backups\\logs\\{datetime.fromtimestamp(time()).strftime("%d.%m.%Y %H.%M.%S")}')
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
	async def rollTalkingStick(guild):
		tsRole = discord.Object(data['servers'][guild]['tsRole'])
		server = await client.fetch_guild(guild)
		while True:
			try: rand = data['servers'][guild]['activeMembers'][randint(0,len(data['servers'][guild]['activeMembers'])-1)]
			except ValueError: return 
			if int(rand) in data['servers'][guild]['ignore']: continue
			try: oldStik = await server.fetch_member(data['servers'][guild]['currentStik'])
			except discord.errors.NotFound: oldStik = None
			try: newStik = await server.fetch_member(rand)
			except: continue
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
		save(data)

@client.event
async def on_command_error(ctx,error): await ctx.send('all commands have been ported to slash commands, type "/" to see a list of commands.')
@client.event
async def on_slash_command_error(ctx:SlashContext,error): await ctx.send(str(error),hidden=True); raise(error)
@client.command(name='test')
async def nonSlashTest(ctx): await ctx.channel.send('pp')

client.loop.create_task(loops.nineLoop())
client.loop.create_task(loops.birthdayLoop())
client.add_cog(general(client))
load_extentions(extentions)

try: client.run(os.getenv('token'))
finally: print('closing bot.')