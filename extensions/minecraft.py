import discord,data,os
from re import sub
from mcrcon import MCRcon
from asyncio import sleep
from logger import logOutput
from tyrantLib import getDirSize
from mcstatus import MinecraftServer
from discord.ext.commands import Cog
from permission_utils import administrator, botOwner, guild_only, moderator
from discord_slash import cog_ext,SlashContext
from discord_slash.utils.manage_commands import create_option

serverStarted=False
bot=data.load('bot')
mainDirectory=os.getcwd()
servers=data.load('servers')
# mcServers=data.load('mcServers')
serverQuery=f"{os.getenv('minecraftHost')}:{os.getenv('mcQueryPort')}"
mc=MCRcon(os.getenv('minecraftHost'),os.getenv('mcRconPassword'),int(os.getenv('mcRconPort')))

mcGuilds = bot.read(['mcGuilds'])

class minecraft(Cog):
	@cog_ext.cog_subcommand(base='minecraft',name='start',description='start a minecraft start.',guild_ids=mcGuilds,
		options=[create_option('server','minecraft server name',str,True)])
	@guild_only()
	async def minecraft_start(self,ctx:SlashContext,server:str):
		global serverStarted
		await ctx.defer()
		if server not in servers.read([str(ctx.guild.id),'mcservers']): await ctx.send('unknown server name, try /minecraft list'); return
		if servers.read([str(ctx.guild.id),'mcservers',server,'custom']): await ctx.send('I can\'t start custom servers!'); return
		if serverStarted: await ctx.send('a server is already started!'); return
		if not minecraft.startServer(self,server): await ctx.send('failed to start server'); return
		await ctx.send('okay, it\'s starting.')
		for i in range(120):
			try: MinecraftServer.lookup(serverQuery).query().players.online; break
			except: await sleep(1)
		else: await ctx.channel.send('server either took more than 120 seconds to start or failed to start.'); return
		await ctx.channel.send(f'{ctx.author.mention} it should be up at `mc.nutt.dev`')
		logOutput(f'minecraft server {server} started',ctx)

	def startServer(self,server):
		global serverStarted
		dir = os.getcwd()
		try: os.chdir(f'/home/tyrantlink/mcservers/{server}')
		except: return False
		os.system(f'gnome-terminal --tab -t {server} -- java -XX:+UseG1GC -XX:+UnlockExperimentalVMOptions -Xmx4096M -Xms4096M -jar server.jar nogui')
		os.chdir(dir)
		serverStarted = True
		return True
	
	def stopServer():
		global serverStarted
		mc.connect()
		mc.command('stop')
		mc.disconnect()
		serverStarted = False
	
	@cog_ext.cog_subcommand(base='minecraft',name='stop',description='stop a minecraft server',guild_ids=mcGuilds,
		options=[create_option('force','force stop the server (requires admin)',bool,False)])
	async def minecraft_stop(self,ctx:SlashContext,force:bool=False):
		global serverStarted
		await ctx.defer()
		try: online = MinecraftServer.lookup(serverQuery).query().players.online
		except ConnectionResetError: online = 0
		if online > 0:
			match force:
				case True:
					if await administrator(ctx): await ctx.send('unable to shutdown server.'); return
				case False:
					if not await administrator(ctx): await ctx.send('you don\'t have permission to do this.'); return
		try: minecraft.stopServer(); await ctx.send('stopping server.')
		except: await ctx.send('failed to shutdown server.'); return
		logOutput('minecraft server stopped',ctx)

	@cog_ext.cog_subcommand(base='minecraft',name='restart',description='stops then starts a minecraft server.',guild_ids=mcGuilds,
		options=[
			create_option('server','minecraft server name',str,True),
			create_option('force','force stop the server (requires admin)',bool,False)])
	async def minecraft_restart(self,ctx:SlashContext,server:str,force:bool=False):
		await ctx.send('I\'ll maintain this command when I get around to it, for now just use stop and start'); return
		await ctx.defer()
		try: online = MinecraftServer.lookup(serverQuery).query().players.online
		except ConnectionResetError: online = 0
		if online > 0:
			match force:
				case True:
					if await administrator(ctx): await ctx.send('unable to shutdown server.'); return
				case False:
					if not await administrator(ctx): await ctx.send('you don\'t have permission to do this.'); return
		try: minecraft.stopServer()
		except: await ctx.send('failed to shutdown server.'); return
		await ctx.send('restarting server...')
		minecraft.startServer(self,server)
		await sleep(3)
		for i in range(100):
			try: MinecraftServer.lookup(serverQuery).query().players.online; break
			except: await sleep(1)
		else: await ctx.channel.send('server either took more than 100 seconds to start or failed to start.'); return
		await ctx.channel.send('it should be up at `mc.nutt.dev`')
		logOutput(f'minecraft server {server} restarted',ctx)

	@cog_ext.cog_subcommand(base='minecraft',name='command',description='run a command on the minecraft server',guild_ids=mcGuilds)
	@administrator()
	async def minecraft_command(self,ctx:SlashContext,command:str):
		try: mc.connect(); response = mc.command(command); mc.disconnect()
		except: await ctx.send('failed to send command.'); return
		try: await ctx.send(sub('§.','',response))
		except: await ctx.send('no command response.') if not response else await ctx.send('error sending command response.')

	@cog_ext.cog_subcommand(base='minecraft',name='info',description='info about a minecraft server',guild_ids=mcGuilds,
		options=[create_option('server','minecraft server name',str,True,)])
	async def minecraft_info(self,ctx:SlashContext,server:str):
		if server not in servers.read([str(ctx.guild.id),'mcservers']): await ctx.send('unknown server name, try /minecraft list'); return
		server_data=servers.read([str(ctx.guild.id),'mcservers',server])
		info = []
		try:
			for i in server_data:
				if i=='directory' or i=='custom': continue
				info.append(f"{i}: {server_data[i]}")
		except: await ctx.send('server name error'); return
		if not server_data['custom']:
			info.append(f"size: {getDirSize(f'/home/tyrantlink/mcservers/{server}')}")
			server += ' [official]'
		else: server += ' [custom]'
		await ctx.send(embed=discord.Embed(title=f'{server}:',description='\n'.join(info),color=0x69ff69))
		logOutput(f'info about server {server} requested',ctx)

	@cog_ext.cog_subcommand(base='minecraft',name='online',description='list all online players.',guild_ids=mcGuilds)
	async def online(self,ctx:SlashContext):
		try: players = MinecraftServer.lookup(serverQuery).query().players.online.names
		except: await ctx.send('cannot connect to server. is it online?'); return
		await ctx.send(embed=discord.Embed(title='Players Online:',description='\n'.join(players) if players else 'there are no players online',color=0x69ff69))
		logOutput(f'online players requested',ctx)
	
	@cog_ext.cog_subcommand(base='dev',name='set_serverstarted',description='set the minecraft server started value',
		options=[create_option('value','value',bool,True)])
	@botOwner()
	async def dev_set_serverstarted(self,ctx:SlashContext,value):
		global serverStarted
		serverStarted = value
		await ctx.send(f'successfully set serverStarted to {serverStarted}')
		logOutput(f'set serverStarted to {value}',ctx)
	
	@cog_ext.cog_subcommand(base='minecraft',name='add_server',description='add a minecraft server to reginald. (reginald cannot start custom servers)',guild_ids=mcGuilds,
		options=[
			create_option('name','server name',str,True),
			create_option('ip','server ip or hostname',str,True),
			create_option('version','minecraft version',str,True),
			create_option('modpack','name of modpack (vanilla if left empty)',str,False),
			create_option('modpack_url','url to download modpack (required if using modpack)',str,False)
		])
	@moderator()
	async def minecraft_add_server(self,ctx:SlashContext,name,ip,version,modpack=None,modpack_url=None):
		if name in servers.read([str(ctx.guild.id),'mcservers']): await ctx.send('a server already has that name!'); return
		server = {
			'custom':True,
			'ip':ip,
			'version':version
		}
		if not modpack and not modpack_url: server.update({'modpack':'Vanilla'})
		elif modpack and not modpack_url: await ctx.send('unspecified modpack url!'); return
		else: server.update({'modpack':f'[{modpack}](<{modpack_url}>)'})
		servers.write(server,[str(ctx.guild.id),'mcservers',name])
		await ctx.send(f'{name} has successfully been added to reginald.')
		logOutput(f'minecraft server {name} added',ctx)

def setup(client): client.add_cog(minecraft(client))