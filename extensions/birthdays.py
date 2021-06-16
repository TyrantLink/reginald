import discord,data
from logger import logOutput
from discord.ext.commands import Cog
from discord_slash import cog_ext,SlashContext
from permission_utils import administrator,guild_only

servers = data.load('servers')
users = data.load('users')
bot = data.load('bot')

class birthdays(Cog):
	@cog_ext.cog_subcommand(base='birthday',name='setup',description='setup birthday channel and role')
	@administrator()
	@guild_only()
	async def birthday_setup(self,ctx:SlashContext,channel:discord.TextChannel,role:discord.Role):
		if not servers.read([str(ctx.guild.id),'config','enableBirthdays']): await ctx.send(embed=discord.Embed(title='Birthdays is not enabled on this server.',color=bot.read(['config','embedColor']))); return
		servers.write(role.id,[str(ctx.guild.id),'roles','birthdays'])
		servers.write(role.id,[str(ctx.guild.id),'channels','birthdays'])
		await ctx.send(f'successfully set birthday role to {role.mention} and birthday channel to {channel.mention}')
		logOutput(f'birthday role set to {role.name} and birthday channel set to {channel.name}',ctx)

	@cog_ext.cog_subcommand(base='birthday',name='set',description='set your birthday')
	async def birthday_set(self,ctx:SlashContext,month:int,day:int):
		if int(month)>12 or int(day)>31: await ctx.send('invalid date.'); return
		users.write(f'{month.zfill(2)}/{day.zfill(2)}',[str(ctx.author.id),'birthday'])
		await ctx.send(f'birthday successfully set to {users.read([str(ctx.author.id),"birthday"])}')
		logOutput(f'birthday set to {month}/{day}',ctx)

	@cog_ext.cog_subcommand(base='birthday',name='remove',description='remove your birthday')
	async def birthday_remove(self,ctx:SlashContext):
		users.write(None,[str(ctx.author.id),'birthday'])
		await ctx.send(f'birthday successfully removed')
		logOutput(f'birthday removed',ctx)

def setup(client): client.add_cog(birthdays(client))#; client.loop.create_task(birthdays.loop())