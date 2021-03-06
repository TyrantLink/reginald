import discord,data
from random import choice
from asyncio import sleep
from logger import logOutput
from datetime import datetime
from discord.ext.commands import Cog
from discord_slash import cog_ext,SlashContext
from permission_utils import guild_only,moderator

questions = data.load('questions').read(['qotd'])
servers = data.load('servers')
bot = data.load('bot')

class qotd(Cog):
	def __init__(self,client): self.client = client; client.loop.create_task(qotd.loop(self))

	@cog_ext.cog_subcommand(base='qotd',name='setup',description='setup question of the day')
	@guild_only()
	@moderator()
	async def qotd_setup(self,ctx:SlashContext,channel:discord.TextChannel):
		if not servers.read([str(ctx.guild.id),'config','enableQOTD']): await ctx.send(f'QOTD is not enabled on this server, enable it with /config')
		servers.write(channel.id,[str(ctx.guild.id),'channels','qotd'])
		await ctx.send(embed=discord.Embed(title='Setup Complete.',description=f'channel: <#{channel.id}>',color=bot.read(['config','embedColor'])))
		logOutput(f'qotd setup',ctx)

	async def loop(self):
		await self.client.wait_until_ready()
		while self.client.is_ready():
			await sleep(60)
			if datetime.now().strftime("%H:%M") == '09:00':
				for guild in self.client.guilds:
					try: server = servers.read([str(guild.id)])
					except: continue
					if not server['config']['enableQOTD']: continue
					if not server['channels']['qotd']: await guild.owner.send(f'error in qotd. please redo setup in {guild.name}.')
					await guild.get_channel(server['channels']['qotd']).send(embed=discord.Embed(title='❓❔ Question of the Day ❔❓',description=choice(questions),color=bot.read(['config','embedColor'])))

def setup(client): client.add_cog(qotd(client))