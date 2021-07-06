import discord,data
from logger import logOutput
from discord.ext.commands import Cog
from permission_utils import moderator
from discord_slash import cog_ext,SlashContext

bot = data.load('bot')
servers = data.load('servers')

class admin(Cog):
	@cog_ext.cog_subcommand(base='admin',subcommand_group='ignore',name='add',description='add a user to the ignore list')
	@moderator()
	async def admin_ignore_add(self,ctx:SlashContext,user:discord.User):
		servers.action('append',user.id,[str(ctx.guild.id),'ignore'])
		await ctx.send(f'successfully added {user.name} to ignore list.')
		logOutput(f'{user.name} was added to ignore list',ctx)

	@cog_ext.cog_subcommand(base='admin',subcommand_group='ignore',name='remove',description='add a user to the ignore list')
	@moderator()
	async def admin_ignore_remove(self,ctx:SlashContext,user:discord.User):
		servers.action('remove',user.id,[str(ctx.guild.id),'ignore'])
		await ctx.send(f'successfully added {user.name} to ignore list.')
		logOutput(f'{user.name} was removed from ignore list',ctx)

def setup(client): client.add_cog(admin(client))