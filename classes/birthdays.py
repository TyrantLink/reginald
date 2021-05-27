import discord,asyncio
from discord.ext import commands
from datetime import datetime
from discord_slash import cog_ext,SlashContext
from bot import adminOrOwner,data,client,logOutput
from discord.ext.commands.core import guild_only

class birthdays(commands.Cog):
	def __init__(self,client): self.client = client
	@cog_ext.cog_subcommand(base='birthday',name='setup',description='setup auto birthdays. (requires admin)')
	@adminOrOwner()
	@guild_only()
	async def birthday_setup(self,ctx:SlashContext,role:discord.Role,channel:discord.TextChannel):
		if not data['servers'][str(ctx.guild.id)]['config']['enableBirthdays']: await ctx.send(embed=discord.Embed(title='Birthdays is not enabled on this server.',color=0x69ff69)); return
		data['servers'][str(ctx.guild.id)]['birthdayRole'] = role.id
		data['servers'][str(ctx.guild.id)]['birthdayChannel'] = channel.id
		await ctx.send(f'successfully set birthday role to {role.mention} and birthday channel to {channel.mention}')
		logOutput(f'birthday role set to {role.name} and birthday channel set to {channel.name}',ctx)
	@cog_ext.cog_subcommand(base='birthday',name='set',description='setup birthday role')
	async def birthday_set(self,ctx:SlashContext,month:int,day:int):
		if int(month)>12 or int(day)>31: await ctx.send('invalid date.'); return
		data['users'][str(ctx.author.id)]['birthday'] = f'{month.zfill(2)}/{day.zfill(2)}'
		await ctx.send(f"birthday successfully set to {data['users'][str(ctx.author.id)]['birthday']}")
		logOutput(f"birthday set to {data['users'][str(ctx.author.id)]['birthday']}",ctx)
	@cog_ext.cog_subcommand(base='birthday',name='reset',description='reset your birthday')
	async def birthday_remove(self,ctx:SlashContext):
		data['users'][str(ctx.author.id)]['birthday'] = None
		await ctx.send(f'birthday successfully reset')
		logOutput(f'birthday reset',ctx)
	

def setup(client): client.add_cog(birthdays(client))