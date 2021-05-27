import discord
from discord.ext import commands
from discord.ext.commands import is_owner
from discord_slash import cog_ext,SlashContext
from bot import data,logOutput,save,adminOrOwner,modOrOwner
from discord_slash.utils.manage_commands import create_option

valueConverter={'True':True,'False':False,'true':True,'false':False}

class config(commands.Cog):
	def __init__(self,client): self.client = client
	@cog_ext.cog_subcommand(base='config',subcommand_group='bot',name='set',description='set variables for the bot',options=[create_option('variable','see current value with /config bot list',3,True,list(data['botConfig'].keys())),create_option('value','bool or int',5,True)])
	@is_owner()
	async def config_bot_set(self,ctx:SlashContext,variable:str,value:bool):
		data['botConfig'][variable] = value
		await ctx.send(f"successfully set {variable} to {data['botConfig'][variable]}")
		save(data)
		logOutput(f'bot config {variable} set to {str(value)}',ctx)
	@cog_ext.cog_subcommand(base='config',subcommand_group='server',name='set',description='set variables for the bot. (requires admin)',options=[create_option('variable','see current value with /config server list',3,True,list(data['defaultServer']['config'].keys())),create_option('value','bool or int',3,True)])
	@adminOrOwner()
	async def config_server_set(self,ctx:SlashContext,variable:str,value:str):
		if variable == 'maxRolls' and int(value) > 32768: await ctx.send('maxRolls cannot be higher than 32768!'); return
		if value in valueConverter: value = valueConverter[value]
		else:
			try: value = int(value)
			except: await ctx.send('value error'); return
		if type(data['servers'][str(ctx.guild.id)]['config'][variable]) == type(value): data['servers'][str(ctx.guild.id)]['config'][variable] = value
		else: await ctx.send('type error'); return
		await ctx.send(f"successfully set {variable} to {data['servers'][str(ctx.guild.id)]['config'][variable]}")
		if variable == 'enableTalkingStick' and value in valueConverter: await ctx.send('remember to do /sticc setup to enable the talking sticc.')
		save(data)
		logOutput(f'server config {variable} set to {str(value)}',ctx)
	@cog_ext.cog_subcommand(base='config',subcommand_group='bot',name='list',description='list config variables.')
	@is_owner()
	async def config_bot_list(self,ctx:SlashContext):
		await ctx.send(embed=discord.Embed(title='Config:',description='\n'.join([f"{i}:{data['botConfig'][i]}" for i in data['botConfig']]),color=0x69ff69))
		logOutput(f'bot config list requested',ctx)
	@cog_ext.cog_subcommand(base='config',subcommand_group='server',name='list',description='list config variables. (requires moderator)')
	@modOrOwner()
	async def config_server_list(self,ctx:SlashContext):
		await ctx.send(embed=discord.Embed(title='Config:',description='\n'.join([f"{i}:{data['servers'][str(ctx.guild.id)]['config'][i]}" for i in data['servers'][str(ctx.guild.id)]['config']]),color=0x69ff69))
		logOutput(f'server config list requested',ctx)
	
def setup(client): client.add_cog(config(client))