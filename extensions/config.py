import discord,data
from logger import logOutput
from discord.ext.commands import Cog
from discord_slash import cog_ext,SlashContext
from discord_slash.utils.manage_commands import create_option
from permission_utils import administrator,moderator,botOwner,guild_only

servers = data.load('servers')
bot = data.load('bot')
valConv = {'true':True,'false':False}


class config(Cog):
	@cog_ext.cog_subcommand(base='config',name='set',description='set a config value (server specific)',
		options=[
			create_option('key','config option you want to change',str,True,servers.read(['0','config'])),
			create_option('value','value to set',str,True)])
	@administrator()
	@guild_only()
	async def config_set(self,ctx:SlashContext,key,value):
		if value.lower() in valConv: value = valConv[value.lower()] # checks if key should be bool and converts to one
		else:
			try: value = int(value)
			except: await ctx.send('value error.'); return # sends value error if value is not bool or int
			if key == 'maxRoll' and value > 32768: await ctx.send('maxRoll cannot be higher than 32768!'); return # checks if int is too high for maxRolls
		try: 
			if type(value) != type(servers.read([str(ctx.guild.id),'config',key])): await ctx.send('type error.'); return # sends type error if key types are mismatched
		except: await ctx.send('key error.'); return # sends key error if key does not exist in config file
		# checks done
		servers.write(value,[str(ctx.guild.id),'config',key])
		await ctx.send(f'successfully set {key} to {servers.read([str(ctx.guild.id),"config",key])}') # reads from file to confirm write
		logOutput(f'{key} set to {value}',ctx)

	@cog_ext.cog_subcommand(base='config',name='list',description='list config values')
	@moderator()
	@guild_only()
	async def config_list(self,ctx:SlashContext):
		cfg = servers.read([str(ctx.guild.id),'config'])
		await ctx.send(embed=discord.Embed(title='config',description='\n'.join([f'{i}: {cfg[i]}' for i in cfg]),color=bot.read(['config','embedColor'])))
		logOutput('config requested',ctx)

	@cog_ext.cog_subcommand(base='dev',subcommand_group='config',name='set',description='set bot config',
		options=[
			create_option('key','config option you want to change',str,True,bot.read(['config'])),
			create_option('value','value to set',str,True)])
	@botOwner()
	async def dev_config_set(self,ctx:SlashContext,key,value):
		if value.lower() in valConv: value = valConv[value.lower()] # checks if key should be bool and converts to one
		else:
			try: value = int(value,16)
			except: await ctx.send('value error.'); return # sends value error if value is not bool or hex int
		try: 
			if type(value) != type(bot.read(['config',key])): await ctx.send('type error.'); return # sends type error if key types are mismatched
		except: await ctx.send('key error.'); return # sends key error if key does not exist in config file
		# checks done
		bot.write(value,['config',key])
		await ctx.send(f'successfully set {key} to {bot.read(["config",key])}') # reads from file to confirm write
		logOutput(f'bot {key} set to {value}',ctx)

	@cog_ext.cog_subcommand(base='dev',subcommand_group='config',name='list',description='list bot config')
	@botOwner()
	async def dev_config_list(self,ctx:SlashContext):
		cfg = bot.read(['config'])
		await ctx.send(embed=discord.Embed(title='config',description='\n'.join([f'{i}: {cfg[i]}' for i in cfg]),color=bot.read(['config','embedColor'])))
		logOutput('bot config requested',ctx)


def setup(client): client.add_cog(config(client))