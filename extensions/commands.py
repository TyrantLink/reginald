import discord,data
from logger import logOutput
from discord.ext.commands import Cog
from discord_slash import cog_ext,SlashContext
from discord_slash.utils.manage_commands import create_option

bot = data.load('bot')
users = data.load('users')
servers = data.load('servers')

class cmds(Cog):
	def __init__(self,client): self.client = client

	@cog_ext.cog_slash(name='info',description='information about reginald')
	async def info(self,ctx:SlashContext):
		embed = discord.Embed(title='Reginald Info:',description="""a mash up of the server mcstarter, the discipline sticc, and the mcfuck.\n
		please submit any issues using /reginald issue\n
		and if you have any suggestions, you can use /reginald suggest\n
		you can follow development here: https://discord.gg/4mteVXBDW7\n
		thank you, all hail reginald.""",color=bot.read(['config','embedColor']))
		await ctx.send(embed=embed)
		logOutput(f'reginald info requested',ctx)

	@cog_ext.cog_subcommand(base='get',name='userprofile',description='get the profile of a user')
	async def get_userprofile(self,ctx:SlashContext,user:discord.User=None):
		if not user: user = ctx.author
		description = [f'creation date: {user.created_at.strftime("%m/%d/%Y %H:%M:%S")}',f'display name: {user.display_name}']
		guilds = "\n- ".join([i.name for i in user.mutual_guilds])
		description.append(f'mutual guilds:\n  - {guilds}')
		if str(user.id) in users.read(): # adds birthday and rp score if user has saved data
			if users.read([str(user.id),'messages']): description.append(f"messages sent in mutual servers: {users.read([str(user.id),'messages'])}")
			if users.read([str(user.id),'birthday']): description.append(f"birthday: {users.read([str(user.id),'birthday'])}")
			if users.read([str(user.id),'ricePurityScore']): description.append(f"rice purity score: hidden" if users.read([str(user.id),'ricePurityScore']).startswith('h') else f"rice purity score: {users.read(user.id,['ricePurityScore'])}")
		embed = discord.Embed(title=f'{user.name}\'s profile',description=f'id: {user.id}\nname: {user.name}\ndiscriminator: {user.discriminator}',color=bot.read(['config','embedColor']))
		embed.set_thumbnail(url=user.avatar.with_format('png').with_size(512).url) # sets thumbnail to user avatar
		embed.add_field(name='information:',value='\n'.join(description))
		await ctx.send(embed=embed)
		logOutput(f'profile of {user.name} requested',ctx)

	@cog_ext.cog_subcommand(base='get',name='guildprofile',description='get the profile of a guild',
		options=[create_option('guild','id of guild (current guild if left blank)',str,False)])
	async def get_guildprofile(self,ctx:SlashContext,guild_id:str=None):
		await ctx.defer()
		if guild_id: guild = self.client.get_guild(int(guild_id))
		else: guild = ctx.guild
		if not guild:
			try: guild = await self.client.fetch_guild(int(guild_id))
			except discord.errors.Forbidden: await ctx.send('I can\'t get the information on that guild, am I a member?')
		description = [
			f'creation date: {guild.created_at.strftime("%m/%d/%Y %H:%M:%S")}',
			f'online members: {len(list(filter(lambda member: str(member.status) != "offline" and not member.bot,guild.members)))} ({len(list(filter(lambda member: str(member.status) != "offline",guild.members)))})',
			f'total members: {len(list(filter(lambda member: not member.bot,guild.members)))} ({guild.member_count})',
			]
		embed = discord.Embed(title=f'{guild.name}\'s profile',description=f'id: {guild.id}\nname: {guild.name}\nowner: {guild.owner.mention}',color=bot.read(['config','embedColor']))
		embed.set_thumbnail(url=guild.icon.with_format('png').with_size(512).url) # sets thumbnail to guild avatar
		embed.add_field(name='information:',value='\n'.join(description))
		await ctx.send(embed=embed)
		logOutput(f'profile of {guild.name} requested',ctx)

	@cog_ext.cog_subcommand(base='get',name='data',description='request your user data')
	async def get_data(self,ctx:SlashContext):
		userData = users.read([str(ctx.author.id)])
		await ctx.send(embed=discord.Embed(title=f'{ctx.author.name}\'s data',description='\n'.join([f'{i}: {userData[i]}' for i in userData]),color=bot.read(['config','embedColor'])),hidden=True)
		logOutput('user data requested',ctx)

	@cog_ext.cog_subcommand(base='leaderboard',name='messages',description='leaderboard of message count in this server')
	async def leaderboard_messages(self,ctx:SlashContext):
		servers.write({key: value for key, value in sorted(servers.read([str(ctx.guild.id),'messageLeaderboard']).items(),key=lambda item: item[1],reverse=True)},[str(ctx.guild.id),'messageLeaderboard'])
		names = []
		index = 1
		for member in servers.read([str(ctx.guild.id),'messageLeaderboard']):
			if member not in bot.read(['idCache']):
				try: bot.write((await self.client.fetch_user(member)).name,['idCache',member])
				except: continue
			rank = str(index)+("th" if 4<=index%100<=20 else {1:"st",2:"nd",3:"rd"}.get(index%10, "th")); index += 1
			names.append(f"{rank} - {bot.read(['idCache',member])}: {servers.read([str(ctx.guild.id),'messageLeaderboard',member])}")
		await ctx.send(embed=discord.Embed(title='Message Leaderboard:',description='\n'.join(names),color=bot.read(['config','embedColor'])))
		logOutput(f'message leaderboard requested',ctx)

	# readthedocs is pain, I'll figure it out when I'm not asleep.
	# @cog_ext.cog_slash(name='help',description='detailed help on reginald commands')
	# async def help(self,ctx:SlashContext):
	# 	await ctx.send('[Reginald Docs](<https://reginald.readthedocs.io/en/latest/>)')

def setup(client): client.add_cog(cmds(client))