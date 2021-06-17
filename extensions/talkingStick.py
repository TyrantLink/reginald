import discord,data
from discord.object import Object
from asyncio import sleep
from random import choice
from datetime import datetime
from discord.ext.commands import Cog
from logger import logOutput,outputLog
from permission_utils import administrator
from discord_slash import cog_ext,SlashContext

bot = data.load('bot')
servers = data.load('servers')

class talkingStick(Cog):
	def __init__(self,client): self.client = client; client.loop.create_task(talkingStick.loop(self))

	@cog_ext.cog_subcommand(base='stick',name='setup',description='setup the talking stick')
	@administrator()
	async def stick_setup(self,ctx:SlashContext,role:discord.Role,channel:discord.TextChannel):
		if not servers.read([str(ctx.guild.id),'config','enableTalkingStick']): await ctx.send(f'the talking stick is not enabled on this server, enable it with /config'); return
		servers.write(role.id,[str(ctx.guild.id),'roles','talkingStick'])
		servers.write(channel.id,[str(ctx.guild.id),'channels','talkingStick'])
		await ctx.send(embed=discord.Embed(title='Setup Complete.',description=f'role: {role.mention}\n\nchannel: {channel.mention}',color=bot.read(['config','embedColor'])))
		logOutput(f'talking stick setup',ctx)

	@cog_ext.cog_subcommand(base='stick',name='reroll',description='force reroll the talking stick.')
	@administrator()
	async def stick_reroll(self,ctx:SlashContext):
		if not servers.read([str(ctx.guild.id),'config','enableTalkingStick']): await ctx.send(f'the talking stick is not enabled on this server, enable it with /config'); return
		await talkingStick.rollTalkingStick(self,str(ctx.guild.id))
		await ctx.send('reroll successful.')
		logOutput(f'talking stick reroll',ctx)

	@cog_ext.cog_subcommand(base='leaderboard',name='sticks',description='talking stick leaderboard.')
	async def leaderboard_sticks(self,ctx:SlashContext):
		await ctx.defer()
		if not servers.read([str(ctx.guild.id),'config','enableTalkingStick']): await ctx.send(f'the talking stick is not enabled on this server, enable it with /config'); return
		servers.write({key: value for key, value in sorted(servers.read([str(ctx.guild.id),'tsLeaderboard']).items(),key=lambda item: item[1],reverse=True)},[str(ctx.guild.id),'tsLeaderboard'])
		names = []
		index = 1
		for member in servers.read([str(ctx.guild.id),'tsLeaderboard']):
			if member not in bot.read(['idCache']): bot.write((await self.client.fetch_user(member)).name,['idCache',member])
			rank = str(index)+("th" if 4<=index%100<=20 else {1:"st",2:"nd",3:"rd"}.get(index%10, "th")); index += 1
			names.append(f"{rank} - {bot.read(['idCache',member])}: {servers.read([str(ctx.guild.id),'tsLeaderboard',member])}")
		await ctx.send(embed=discord.Embed(title='Sticc Leaderboard:',description='\n'.join(names),color=bot.read(['config','embedColor'])))
		logOutput(f'stick leaderboard requested',ctx)

	@cog_ext.cog_subcommand(base='stick',name='active',description='list all daily active users.')
	async def stick_active(self,ctx:SlashContext):
		await ctx.defer()
		if not servers.read([str(ctx.guild.id),'config','enableTalkingStick']): await ctx.send(f'the talking stick is not enabled on this server, enable it with /config'); return
		active = []
		for member in servers.read([str(ctx.guild.id),'activeMembers']):
			if str(member) not in bot.read(['idCache']):
				try: bot.write((await self.client.fetch_user(member)).name,['idCache',str(member)])
				except: continue
			active.append(bot.read(['idCache',str(member)]))
		await ctx.send(embed=discord.Embed(title='Active Members:',description='\n'.join(active),color=bot.read(['config','embedColor'])))
		logOutput(f'active users requested',ctx)

	async def rollTalkingStick(self,guild_id):
		role = discord.Object(servers.read([guild_id,'roles','talkingStick'])) # get tsRole
		server = await self.client.fetch_guild(guild_id) # get guild object
		activeMembers = servers.read([guild_id,'activeMembers']) # get list of active members
		while True: # loop until valid 
			rand = choice(activeMembers) # get random active user.
			if rand in servers.read([guild_id,'ignore']): continue # resets loop if random user is in ignore list.
			try: oldStik = await server.fetch_member(servers.read([guild_id,'currentStick'])) # gets old stick holder as member object
			except discord.errors.NotFound or KeyError: oldStik = None # sets oldStik to none if first roll of talking stick
			try: newStik = await server.fetch_member(rand) # tries to fetch random member
			except: continue # resets loops if failed
			if not rand == servers.read([guild_id,'currentStick']): # checks if old user and new user are the same
				try:
					if newStik.bot and oldStik.bot: break # checks if two bots were rolled in a row
					else: continue
				except AttributeError: break # breaks if oldStik == None
			break
		if oldStik != None: await oldStik.remove_roles(role) # removes role from oldStik
		await newStik.add_roles(role) # adds role to oldStik
		await (await server.fetch_channel(servers.read([guild_id,'channels','talkingStick']))).send(f'congrats <@!{rand}>, you have the talking stick.', # get channel and send message
			embed=discord.Embed(
				title=f'chances: 1/{len(activeMembers)}', # sets title to chances of rolling talking stick
				description='\n'.join([f'<@!{member_id}>' if member_id != rand else f'>>><@!{member_id}><<<' for member_id in activeMembers]),
				color=bot.read(['config','embedColor']))) # lists active members and highlights newStik
		servers.write(rand,[guild_id,'currentStick']) # saves current stick
		try: servers.read([guild_id,'tsLeaderboard',str(rand)])
		except KeyError: servers.write(0,[guild_id,'tsLeaderboard',str(rand)]) # adds user to stick leaderboard if they aren't on it
		servers.math('+',1,[guild_id,'tsLeaderboard',str(rand)]) # add one to leaderboard
		servers.write([],[guild_id,'activeMembers']) # resets active members
		log = f'stick rerolled to {newStik.name} in {server.name}'
		outputLog.warning(log)
		if bot.read(['config','stickToConsole']): print(log) # logs to console if config is enabled

	async def loop(self):
		await self.client.wait_until_ready()
		while self.client.is_ready():
			await sleep(59)
			if datetime.now().strftime("%H:%M") == '09:00':
				for guild in servers.read():
					server = await self.client.fetch_guild(int(guild))
					if not servers.read([guild,'config','enableTalkingStick']): continue
					if not servers.read([guild,'channels','talkingStick']) or not servers.read([guild,'roles','talkingStick']): await server.owner.send(f'error in talking stick. please redo setup in {server.name}.')
					await talkingStick.rollTalkingStick(self,guild)

def setup(client): client.add_cog(talkingStick(client))