import discord,data
from discord.ext import commands
from discord_slash import cog_ext,SlashContext
from bot import logOutput,client,adminOrOwner
from discord_slash.utils.manage_commands import create_option

save = data.load('save')

class cmds(commands.Cog):
	def __init__(self,client): self.client = client
	@cog_ext.cog_subcommand(base='reginald',name='info',description='lists info on reginald.')
	async def reginald_info(self,ctx:SlashContext):
		embed = discord.Embed(title='Reginald Info:',description="""a mash up of the server mcstarter, the discipline sticc, and the mcfuck.\n
		please submit any issues using /reginald issue\n
		and if you have any suggestions, you can use /reginald suggest\n
		you can follow development here: https://discord.gg/4mteVXBDW7\n
		thank you, all hail reginald.""",color=0x69ff69)
		await ctx.send(embed=embed)
		logOutput(f'reginald info requested',ctx)
	@cog_ext.cog_subcommand(base='get',name='avatar',description='returns the avatar of given user')
	async def get_avatar(self,ctx:SlashContext,user:discord.User,resolution:int=512):
		if isinstance(user,int): user = await client.fetch_user(user)
		await ctx.send(embed=discord.Embed(title=f'{user.name}\'s avatar',color=0x69ff69).set_image(url=user.avatar.with_format('png').with_size(resolution).url))
		logOutput(f'avater of {user.name} requested',ctx)
	@cog_ext.cog_subcommand(base='get',name='guild',description='returns guild name from id')
	async def get_guild(self,ctx:SlashContext,guild:int):
		await ctx.send((await client.fetch_guild(int(guild))).name)
		logOutput(f'guild {guild} requested',ctx)
	@cog_ext.cog_subcommand(base='get',name='name',description='returns user name from id')
	async def get_name(self,ctx:SlashContext,user:int):
		await ctx.send((await client.fetch_user(int(user))).name)
		logOutput(f'name of {user} requested',ctx)
	@cog_ext.cog_subcommand(base='reginald',name='ignore',description='adds or removes user to reginald ignore list. (requires admin)',
	options=[create_option('mode','mode',3,True,['add','remove']),create_option('user','user',6,True)])
	@adminOrOwner()
	async def reginald_ignore(self,ctx:SlashContext,mode:str,user:discord.User):
		ignoreList = save.read(['servers',str(ctx.guild.id),'ignore'])
		match mode:
			case 'add':
				if user.id in ignoreList: await ctx.send('this user is already on the ignore list!'); return
				ignoreList.append(user.id)
				await ctx.send(f"successfully added {user.name} to ignore list.")
			case 'remove':
				if user.id not in ignoreList: await ctx.send('this user is not on the ignore list!'); return
				ignoreList.remove(user.id)
				await ctx.send(f"successfully removed {user.name} from ignore list.")
		save.write(ignoreList,['servers',str(ctx.guild.id),'ignore'])
		logOutput(f'{user.name} added to ignore list',ctx)
	@cog_ext.cog_subcommand(base='reginald',subcommand_group='request',name='data',description='request your user save.')
	async def reginald_request_data(self,ctx:SlashContext):
		userdata = save.read(['users',str(ctx.author.id)])
		response = []
		response.append(f'known guilds: {userdata["guilds"]}')
		response.append(f'birthday: {userdata["birthday"]}')
		await ctx.send(embed=discord.Embed(title=f'{ctx.author.name}\'s data',description='\n\n'.join(response),color=0x69ff69),hidden=True)
		logOutput(f'data requested',ctx)
	@cog_ext.cog_subcommand(base='get',name='profile',description='get profile and information of a user.')
	async def get_profile(self,ctx:SlashContext,user:discord.User):
		description = []
		description.append(f'creation date: {user.created_at.strftime("%m/%d/%Y %H:%M:%S")}')
		description.append(f'display name: {user.display_name}')
		guilds = ",\n- ".join([i.name for i in user.mutual_guilds])
		description.append(f'mutual guilds:\n  - {guilds}')
		description.append(f"birthday: {save.read(['users',str(user.id),'birthday'])}")
		description.append(f"rice purity score: hidden" if save.read(['users',str(user.id),'ricePurityScore']).startswith('h') else f"rice purity score: {save.read(['users',str(user.id),'ricePurityScore'])}")
		embed = discord.Embed(title=f'{user.name}\'s profile',description=f'id: {user.id}\nname: {user.name}\ndiscriminator: {user.discriminator}',color=0x69ff69)
		embed.set_thumbnail(url=user.avatar.with_format('png').with_size(512).url)
		embed.add_field(name='information:',value='\n'.join(description))
		user.avatar.with_format('png')
		await ctx.send(embed=embed)
		logOutput(f'profile of {user.name} requested',ctx)

def setup(client): client.add_cog(cmds(client))