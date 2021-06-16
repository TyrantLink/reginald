import discord,data,os
from re import sub
from mcrcon import MCRcon
from asyncio import sleep
from logger import logOutput
from tyrantLib import getDirSize
from mcstatus import MinecraftServer
from discord.ext.commands import Cog
from permission_utils import administrator
from discord_slash import cog_ext,SlashContext
from discord_slash.utils.manage_commands import create_option

serverStarted=False
bot = data.load('bot')
mainDirectory=os.getcwd()
servers=data.load('servers')
mcServers=data.load('mcServers')
serverQuery=f"{os.getenv('minecraftHost')}:{os.getenv('mcQueryPort')}"
mc=MCRcon(os.getenv('minecraftHost'),os.getenv('mcRconPassword'),int(os.getenv('mcRconPort')))

mcGuilds = bot.read(['mcGuilds'])

class minecraft(Cog):
	@cog_ext.cog_subcommand(base='minecraft',name='start',description='start a minecraft start.',guild_ids=mcGuilds,
		options=[create_option('server','minecraft server name',str,True,list(mcServers.read().keys()))])
	async def minecraft_start(self,ctx:SlashContext,server:str):
		global serverStarted
		if serverStarted: await ctx.send('a server is already started!'); return
		os.chdir(mcServers([server,'directory']))
		os.startfile('botStart.bat')
		serverStarted = True
		os.chdir(mainDirectory)
		await ctx.send('okay, it\'s starting.')
		for i in range(100):
			try: MinecraftServer.lookup(serverQuery).query().players.online; break
			except: sleep(1)
		else: await ctx.send('server either took more than 100 seconds to start or failed to start.'); return
		await ctx.send('it should be up on `mc.nutt.dev`')
		logOutput(f'minecraft server {server} started',ctx)
	
	@cog_ext.cog_subcommand(base='minecraft',name='stop',description='stop a minecraft server',guild_ids=mcGuilds,
		options=[create_option('force','force stop the server (requires admin)',bool,True)])
	async def minecraft_stop(self,ctx:SlashContext,force:bool=False):
		global serverStarted
		if MinecraftServer.lookup(serverQuery).query().players.online > 0 and (force and administrator()): await ctx.send('you don\'have permission to do this.'); return
		try: mc.connect(); mc.command('stop'); mc.disconnect(); serverStarted = False; await ctx.send('stopping server.')
		except: await ctx.send('failed to shutdown server.'); return
		logOutput('minecraft server stopped',ctx)

	@cog_ext.cog_subcommand(base='minecraft',name='command',description='run a command on the minecraft server',guild_ids=mcGuilds)
	@administrator()
	async def minecraft_command(self,ctx:SlashContext,command:str):
		try: mc.connect(); response = mc.command(command); mc.disconnect()
		except: await ctx.send('failed to send command.'); return
		try: await ctx.send(sub('§.','',response))
		except: await ctx.send('no command response.') if not response else await ctx.send('error sending command response.')

	@cog_ext.cog_subcommand(base='minecraft',name='info',description='info about a minecraft server',guild_ids=mcGuilds,
		options=[create_option('server','minecraft server name',str,True,list(mcServers.read().keys()))])
	async def minecraft_info(self,ctx:SlashContext,server:str):
		info = []
		try:
			for i in servers.read([server]):
				if i=='directory' or i=='isModded' or i=='mods': continue
				info.append(f'{i}: {servers.read([server,i])}')
		except: await ctx.send('server name error')
		info.append('modpack: vanilla') if not servers.read([server,'isModded']) else info.append(f'modpack: https://mods.nutt.dev/{server}')
		info.append(f'size: {getDirSize(mcServers.read([server,"directory"]))}')
		await ctx.send(embed=discord.Embed(title=f'{server} info:',description='\n'.join(info),color=0x69ff69))
		logOutput(f'info about server {server} requested',ctx)

	@cog_ext.cog_subcommand(base='minecraft',name='online',description='list all online players.',guild_ids=mcGuilds)
	async def online(self,ctx:SlashContext):
		try: players = MinecraftServer.lookup(serverQuery).query().players.online.name
		except: await ctx.send('cannot connect to server. is it online?'); return
		await ctx.send(embed=discord.Embed(title='Players Online:',description='\n'.join(players) if players else 'there are no players online',color=0x69ff69))
		logOutput(f'online players requested',ctx)

def setup(client): client.add_cog(minecraft(client))