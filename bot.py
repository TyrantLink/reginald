from codetiming import Timer
startup = Timer(name='startup')
startup.start()
import os
os.system('cls')
from dotenv import load_dotenv
import data,discord
from discord.ext.commands import Cog,Bot
from logger import logOutput,outputLog
from discord_slash import SlashContext,SlashCommand,cog_ext
from discord_slash.utils.manage_commands import create_option

load_dotenv()
extensions = [f.split('.py')[0] for f in [i[2] for i in os.walk(f'{os.getcwd()}\\extensions')][0]]
client = Bot('stoplookingatmysourcecode',help_command=None,intents=discord.Intents.all(),owner_id=250797109022818305)
slash = SlashCommand(client,True)
bot = data.load('bot')

class base(Cog):
	@Cog.listener()
	async def on_ready(self): # connected to discord and set presence
		elapsedTime = round(startup.stop()*1000,3)
		outputLog.warning(f"{client.user.name} connected to Discord!")
		print(f"{client.user.name} connected to Discord!\n")
		await client.change_presence(activity=discord.Activity(type=discord.ActivityType.custom, name='the collective one.'))
	
	@cog_ext.cog_subcommand(base='extension',name='reload',description='reloads given extension',
		options=[
			create_option('extension','extension to reload',str,True,extensions),
			create_option('resync','do you want to resync commands',bool,False)])
	async def extension_reload(self,ctx:SlashContext,extension:str,resync:bool=False): # reload an extension
		await ctx.defer()
		client.reload_extension(f'extensions.{extension}')
		if resync: await slash.sync_all_commands() # sync commands if resync is needed
		await ctx.send(f'successfully reloaded {extension} extension')
		logOutput(f'reloaded {extension} extension',ctx)
	
	@cog_ext.cog_subcommand(base='extension',name='add',description='adds given extension')
	async def extension_add(self,ctx:SlashContext,extension:str): # add an extension if the file did not exist on bot startup
		await ctx.defer() # defers to allow loading times longer than 3 seconds
		client.load_extension(f'extensions.{extension}')
		await slash.sync_all_commands() # sync commands on extension add
		await ctx.send(f'successfully reloaded {extension} extension')
		logOutput(f'reloaded {extension} extension',ctx)

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
for extension in extensions:
	try: client.load_extension(f'extensions.{extension}'); continue
	except Exception as error:
		print(f'failed to load extension [{extension}]')
		if bot.read(['config','raiseErrors']): raise(error) # this didn't work as a one-line if, it would always raise.
		else: print(error)

try: client.run(os.getenv('token'))
finally: data.saveAll(); os.system('cls')