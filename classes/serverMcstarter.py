import discord,os,json,re,asyncio,data
from mcrcon import MCRcon
from discord.ext import commands
from mcstatus import MinecraftServer
from discord.ext.commands import is_owner
from bot import adminOrOwner,logOutput
from discord_slash import cog_ext,SlashContext

serverStarted = False
sizes={2:'MBs',3:'GBs'}
mainDirectory = os.getcwd()
serverQuery=os.getenv('serverQuery')
servers=json.loads(open('servers.json','r').read())
mc=MCRcon(os.getenv('mcRconHost'),os.getenv('mcRconPassword'),int(os.getenv('mcRconPort')))

class serverMcstarter(commands.Cog):
	def __init__(self,client): self.client = client
	@cog_ext.cog_subcommand(base='minecraft',name='start',description='starts a minecraft server.')
	async def start(self,ctx:SlashContext,server:str):
		if serverStarted: return
		try: os.chdir(servers[server]['directory'])
		except: await ctx.send('server name error')
		os.startfile('botStart.bat')
		os.chdir(mainDirectory)
		await ctx.send('okay, it\'s starting.')
		for i in range(data.read(['servers',str(ctx.guild.id),'config','maxServerStartTime'])):
			try: MinecraftServer.lookup(serverQuery).query().players.online; break
			except: asyncio.sleep(1)
		else: await ctx.send('error starting server.'); return
		await ctx.send('it should be up.')
		logOutput(f'starting server {server}',ctx)
	@cog_ext.cog_subcommand(base='minecraft',name='stop',description='stops active minecraft server. (\'-f\' requires admin)')
	async def stop(self,ctx:SlashContext,args:str=None):
		if MinecraftServer.lookup(serverQuery).query().players.online > 0:
			if not (args == '-f' and adminOrOwner()): await ctx.send('no, fuck you, there are people online.'); return
		try: mc.connect(); mc.command('stop'); mc.disconnect(); serverStarted = False; await ctx.send('stopping server.')
		except: await ctx.send('failed to shutdown server.'); return
		logOutput(f'stopping server',ctx)
	@cog_ext.cog_subcommand(base='minecraft',name='cmd',description='runs command on the active minecraft server.')
	@is_owner()
	async def cmd(self,ctx:SlashContext,command:str):
		try: mc.connect(); response = mc.command(command); mc.disconnect()
		except: await ctx.send('failed to send command'); return
		try: await ctx.send(re.sub('§.','',response))
		except: pass
		logOutput(f'command {command} run',ctx)
	@cog_ext.cog_subcommand(base='minecraft',name='info',description='lists info on given minecraft server.')
	async def minecraft_info(self,ctx:SlashContext,server:str):
		info = []
		try:
			for i in servers[server]:
				if i=='directory' or i=='isModded' or i=='mods': continue
				info.append(f'{i}: {servers[server][i]}')
		except: await ctx.send('server name error')
		info.append('modpack: vanilla') if servers[server]['isModded']==False else info.append(f'modpack: https://mods.nutt.dev/{server}')
		info.append(f'size: {serverMcstarter.getServerSize(server)}')
		await ctx.send(embed=discord.Embed(title=f'{server} info:',description='\n'.join(info),color=0x69ff69))
		logOutput(f'info about server {server} requested',ctx)
	@cog_ext.cog_subcommand(base='minecraft',name='online',description='returns list of players online.')
	async def online(self,ctx:SlashContext):
		try: players = MinecraftServer.lookup(serverQuery).query().players.names
		except: await ctx.send('cannot connect to server. is it online?'); return
		if players == []: await ctx.send('no one is online.'); return
		await ctx.send(embed=discord.Embed(title='Players Online:',description='\n'.join(players),color=0x69ff69))
		logOutput(f'online players requested',ctx)
	@cog_ext.cog_subcommand(base='minecraft',name='servers',description='lists all minecraft servers')
	async def list_servers(self,ctx:SlashContext): await ctx.send(embed=discord.Embed(title='Minecraft Servers:',description='\n'.join(servers),color=0x69ff69))
	def getServerSize(server):
		size = 0; sizeType = 0
		for path, dirs, files in os.walk(servers[server]['directory']):
			for f in files: fp = os.path.join(path, f); size += os.path.getsize(fp)
		while size/1024 > 1: size = size/1024; sizeType += 1
		return f'{round(size,3)} {sizes[sizeType]}'

def setup(client): client.add_cog(serverMcstarter(client))