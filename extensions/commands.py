import discord,data
from logger import logOutput
from discord.ext.commands import Cog
from discord_slash import cog_ext,SlashContext

bot = data.load('bot')
users = data.load('users')

class cmds(Cog):
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
	async def get_userprofile(self,ctx:SlashContext,user:discord.User):
		description = [f'creation date: {user.created_at.strftime("%m/%d/%Y %H:%M:%S")}',f'display name: {user.display_name}']
		guilds = ",\n- ".join([i.name for i in user.mutual_guilds])
		description.append(f'mutual guilds:\n  - {guilds}')
		if str(user.id) in users.read(): # adds birthday and rp score if user has saved data
			if users.read([str(user.id),'birthday']): description.append(f"birthday: {users.read([str(user.id),'birthday'])}")
			if users.read([str(user.id),'ricePurityScore']): description.append(f"rice purity score: hidden" if users.read([str(user.id),'ricePurityScore']).startswith('h') else f"rice purity score: {users.read(user.id,['ricePurityScore'])}")
		embed = discord.Embed(title=f'{user.name}\'s profile',description=f'id: {user.id}\nname: {user.name}\ndiscriminator: {user.discriminator}',color=bot.read(['config','embedColor']))
		embed.set_thumbnail(url=user.avatar.with_format('png').with_size(512).url) # sets thumbnail to user avatar
		embed.add_field(name='information:',value='\n'.join(description))
		await ctx.send(embed=embed)
		logOutput(f'profile of {user.name} requested',ctx)

	@cog_ext.cog_subcommand(base='get',name='data',description='request your user data')
	async def get_data(self,ctx:SlashContext):
		userData = users.read([str(ctx.author.id)])
		await ctx.send(embed=discord.Embed(title=f'{ctx.author.name}\'s data',description='\n'.join([f'{i}: {userData[i]}' for i in userData]),color=bot.read(['config','embedColor'])),hidden=True)
		logOutput('user data requested',ctx)

def setup(client): client.add_cog(cmds(client))