import discord
from random import randint
from logger import logOutput
from discord.ext import commands
from discord_slash import cog_ext,SlashContext
from bot import adminOrOwner,data,client,save,outputLog


class theDisciplineSticc(commands.Cog):
	def __init__(self,client): self.client = client
	@cog_ext.cog_subcommand(base='sticc',name='setup',description='setup the discipline sticc. (requires admin)')
	@adminOrOwner()
	async def setup(self,ctx:SlashContext,role:discord.Role,channel:discord.TextChannel):
		if not data['servers'][str(ctx.guild.id)]['config']['enableTalkingStick']: await ctx.send(embed=discord.Embed(title='The Talking Stick is not enabled on this server.',color=0x69ff69)); return
		data['servers'][str(ctx.guild.id)]['tsRole'] = role.id
		data['servers'][str(ctx.guild.id)]['tsChannel'] = channel.id
		await ctx.send(embed=discord.Embed(title='Setup Complete.',description=f'role: <@&{role.id}>\n\nchannel: <#{channel.id}>',color=0x69ff69))
		logOutput(f'talking stick setup',ctx)
	@cog_ext.cog_subcommand(base='sticc',name='reroll',description='reroll the talking sticc. (requires admin)')
	@adminOrOwner()
	async def reroll(self,ctx:SlashContext):
		if not data['servers'][str(ctx.guild.id)]['config']['enableTalkingStick']: await ctx.send(embed=discord.Embed(title='The Talking Stick is not enabled on this server.',color=0x69ff69)); return
		await theDisciplineSticc.rollTalkingStick(str(ctx.guild.id))
		await ctx.send('reroll successful.')
		logOutput(f'talking stick reroll',ctx)
	@cog_ext.cog_subcommand(base='leaderboard',name='sticcs',description='leaderboard of how many times someone has had the talking sticc')
	async def leaderboard_sticcs(self,ctx:SlashContext):
		if not data['servers'][str(ctx.guild.id)]['config']['enableTalkingStick']: await ctx.send(embed=discord.Embed(title='The Talking Stick is not enabled on this server.',color=0x69ff69)); return
		data['servers'][str(ctx.guild.id)]['tsLeaderboard'] = {key: value for key, value in sorted(data['servers'][str(ctx.guild.id)]['tsLeaderboard'].items(), key=lambda item: item[1],reverse=True)}
		names = []
		index = 1
		await ctx.defer()
		for member in data['servers'][str(ctx.guild.id)]['tsLeaderboard']:
			if member not in data['variables']['idNameCache']: data['variables']['idNameCache'][member] = (await client.fetch_user(member)).name
			rank = str(index)+("th" if 4<=index%100<=20 else {1:"st",2:"nd",3:"rd"}.get(index%10, "th")); index += 1
			names.append(f"{rank} - {data['variables']['idNameCache'][member]}: {data['servers'][str(ctx.guild.id)]['tsLeaderboard'][member]}")
		await ctx.send(embed=discord.Embed(title='Sticc Leaderboard:',description='\n'.join(names),color=0x69ff69))
		logOutput(f'stick leaderboard requested',ctx)
	@cog_ext.cog_subcommand(base='sticc',name='active',description='lists members who have been active in the past day.')
	async def list_active(self,ctx:SlashContext):
		if not data['servers'][str(ctx.guild.id)]['config']['enableTalkingStick']: await ctx.send(embed=discord.Embed(title='The Talking Stick is not enabled on this server.',color=0x69ff69)); return
		active = []
		await ctx.defer()
		for member in data['servers'][str(ctx.guild.id)]['activeMembers']:
			if member not in data['variables']['idNameCache']: data['variables']['idNameCache'][member] = (await client.fetch_user(member)).name
			active.append(data['variables']['idNameCache'][member])
		await ctx.send(embed=discord.Embed(title='Active Members:',description='\n'.join(active),color=0x69ff69))
		logOutput(f'active users requested',ctx)

def setup(client): client.add_cog(theDisciplineSticc(client))