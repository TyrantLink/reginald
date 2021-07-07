import data,discord,os
from time import time
from asyncio import sleep
from datetime import datetime
from dotenv import load_dotenv
from tyrantLib import convert_time
from logger import logOutput,outputLog
from discord.ext.commands import Cog,Bot
from discord_slash import SlashContext,SlashCommand,cog_ext
from discord_slash.utils.manage_commands import create_option

st = time()
os.system('clear')

load_dotenv()
extensions = [f.split('.py')[0] for f in [i[2] for i in os.walk(f'{os.getcwd()}/extensions')][0] if not f.endswith('.disabled')]
client = Bot('stoplookingatmysourcecode',help_command=None,intents=discord.Intents.all(),owner_id=250797109022818305)
slash = SlashCommand(client,True)
bot = data.load('bot')

class base(Cog):
	@Cog.listener()
	async def on_ready(self): # connected to discord and set presence
		outputLog.warning(f"{client.user.name} connected to Discord in {round(time()-st,3)} seconds!")
		print(f"{client.user.name} connected to Discord in {round(time()-st,3)} seconds!\n")
		await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,name='starting...'))
	
	@cog_ext.cog_subcommand(base='extension',name='reload',description='reloads given extension',
		options=[
			create_option('extension','extension to reload',str,True,extensions),
			create_option('resync','do you want to resync commands',bool,False)])
	async def extension_reload(self,ctx:SlashContext,extension:str,resync:bool=False): # reload an extension
		await ctx.defer()
		await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,name=f'reloading {extension}.py'))
		client.reload_extension(f'extensions.{extension}')
		if resync: await slash.sync_all_commands() # sync commands if resync is needed
		await ctx.send(f'successfully reloaded {extension} extension')
		logOutput(f'reloaded {extension} extension',ctx)
	
	@cog_ext.cog_subcommand(base='extension',name='load',description='loads given extension')
	async def extension_load(self,ctx:SlashContext,extension:str): # loads an extension if the file did not exist on bot startup
		await ctx.defer() # defers to allow loading times longer than 3 seconds
		await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,name=f'loading {extension}.py'))
		client.load_extension(f'extensions.{extension}')
		await slash.sync_all_commands() # sync commands on extension load
		await ctx.send(f'successfully loaded {extension} extension')
		logOutput(f'loaded {extension} extension',ctx)
	
	@cog_ext.cog_subcommand(base='extension',name='unload',description='loads given extension')
	async def extension_unload(self,ctx:SlashContext,extension:str): # unloads an extension
		await ctx.defer() # defers to allow loading times longer than 3 seconds
		await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,name=f'unloading {extension}.py'))
		client.unload_extension(f'extensions.{extension}')
		await slash.sync_all_commands() # sync commands on extension unload
		await ctx.send(f'successfully unloaded {extension} extension')
		logOutput(f'unloaded {extension} extension',ctx)
	
async def uptime():
	await client.wait_until_ready()
	while client.is_ready():
		await sleep(5)
		await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,name=f'uptime: {convert_time(round(time()-st),"str")}'))

@client.event
async def on_command_error(ctx,error): # run on legacy command error
	await ctx.send('all commands have been ported to slash commands, type "/" to see a list of commands.')
	if bot.read(['config','raiseErrors']): raise(error) # this didn't work as a one-line if, it would always raise.
	else: print(error)

@client.event
async def on_slash_command_error(ctx:SlashContext,error): # run on slash command error
	try: await ctx.send(str(error),hidden=True)
	except: return # returns if error is blank
	if bot.read(['config','raiseErrors']): raise(error) # this didn't work as a one-line if, it would always raise.
	else: print(error)

client.add_cog(base(client))
client.loop.create_task(uptime())
if bot.read(['config','extension_loading']):
	for extension in extensions:
		try: client.load_extension(f'extensions.{extension}'); continue
		except Exception as error:
			print(f'failed to load extension [{extension}]')
			if bot.read(['config','raiseErrors']): raise(error) # this didn't work as a one-line if, it would always raise.
			else: print(error)

try: client.run(os.getenv('token'))
finally: data.saveAll(); os.system('clear')
