
import discord,re,data,os
from logger import logOutput
from discord.ext.commands import Cog
from permission_utils import botOwner
from discord_slash import cog_ext,SlashContext
from discord_slash.utils.manage_commands import create_option

autoResponses = data.load('autoResponses')
bot = data.load('bot')
help = data.load('help')
mcServers = data.load('mcServers')
questions = data.load('questions')
servers = data.load('servers')
users = data.load('users')

class devTools(Cog):
	def __init__(self,client): self.client = client

	def msgFormat(message):
		message = '- ' + '\n- '.join(message.split(r'\n'))
		return message

	def hyperlink(response):
		for i in re.findall(r'issue\d+',response): response = re.sub(r'issue\d+',f"([issue#{i.split('issue')[1]}](<https://discord.com/channels/844127424526680084/844131633787699241/{bot.read(['issues',int(i.split('issue')[1])-1])}>))",response,1)
		for i in re.findall(r'suggestion\d+',response): response = re.sub(r'suggestion\d+',f"([suggestion#{i.split('suggestion')[1]}](<https://discord.com/channels/844127424526680084/844130469197250560/{bot.read(['suggestions',int(i.split('suggestion')[1])-1])}>))",response,1)
		return response

	@cog_ext.cog_subcommand(base='dev',name='commit',description='push a commit to change-log channel')
	@botOwner()
	async def dev_commit(self,ctx:SlashContext,title:str,features:str=None,fixes:str=None,notes:str=None,test:bool=False,newversion:bool=True):
		await ctx.defer()
		if newversion and not test: bot.math('+',0.01,['version'],True,2)
		version = bot.read(['version'])
		channel = await self.client.fetch_channel(bot.read(['development','testing'])) if test else await self.client.fetch_channel(bot.read(['development','change-log']))
		response = f'version: {format(version,".2f")}\n\n'
		if features != None: response += f'features:\n{devTools.msgFormat(features)}\n\n'
		if fixes != None: response += f'fixes / changes:\n{devTools.msgFormat(fixes)}\n\n'
		if notes != None: response += f'notes:\n{devTools.msgFormat(notes)}\n\n'
		response += f'these features are new, remember to report bugs with /reginald issue\ncommands may take up to an hour to update globally.\n[development server](<https://discord.gg/4mteVXBDW7>)'
		response = devTools.hyperlink(response)
		message = await channel.send(embed=discord.Embed(title=title,description=response,color=bot.read(['config','embedColor'])))
		if not test: await message.publish()
		await ctx.send('successfully pushed change.')
		logOutput(f'new commit pushed',ctx)

	@cog_ext.cog_slash(name='suggest',description='suggest a feature for reginald')
	async def suggest(self,ctx:SlashContext,suggestion:str,details:str):
		await ctx.defer()
		bot.math('+',1,['suggestCount'])
		suggestCount = bot.read(['suggestCount'])
		if r'\n' in details: details = devTools.msgFormat(details)
		channel = await self.client.fetch_channel(bot.read(['development','suggestions']))
		message = await channel.send(embed=discord.Embed(title=f"{suggestion} | #{suggestCount}",description=f'suggested by: {ctx.author.mention}\n\ndetails:\n{details}',color=0x69ff69))
		for i in ['<:upvote:854594180339990528>','<:downvote:854594202439909376>']: await message.add_reaction(i)
		bot.action('append',int(message.jump_url.split('/')[-1]),['suggestions'])
		await ctx.send('thank you for your suggestion!')
		logOutput(f'new suggestion "{suggestion}"',ctx)

	@cog_ext.cog_slash(name='issue',description='report an issue with reginald')
	async def issue(self,ctx:SlashContext,issue:str,details:str):
		await ctx.defer()
		bot.math('+',1,['issueCount'])
		issueCount = bot.read(['issueCount'])
		if r'\n' in details: details = devTools.msgFormat(details)
		channel = await self.client.fetch_channel(bot.read(['development','issues']))
		message = await channel.send(embed=discord.Embed(title=f"{issue} | #{issueCount}",description=f'issue by: {ctx.author.mention}\n\ndetails:\n{details}',color=0x69ff69))
		for i in ['<:upvote:854594180339990528>','<:downvote:854594202439909376>']: await message.add_reaction(i)
		bot.action('append',int(message.jump_url.split('/')[-1]),['issues'])
		await ctx.send('thank you for reporting this issue!')
		logOutput(f'new issue "{issue}"',ctx)

	@cog_ext.cog_subcommand(base='clear',name='id_cache',description='clear the idCache variable')
	@botOwner()
	async def clear_id_cache(self,ctx:SlashContext):
		bot.write({},['idCache'])
		await ctx.send('successfully cleared idCache')
		logOutput('idCache cleared',ctx)

	@cog_ext.cog_slash(name='ping',description='ping reginald.')
	async def reginald_ping(self,ctx:SlashContext):
		await ctx.send(f'pong! {round(self.client.latency*100,1)}ms')
		logOutput('pinged',ctx)

	@cog_ext.cog_subcommand(base='dev',name='fsave',description='force save all save files',
		options=[create_option('file','save a specific file (saves all if left blank)',str,False,[f.split('.json')[0] for f in [i[2] for i in os.walk(f'{os.getcwd()}/saves')][0]])])
	@botOwner()
	async def dev_fsave(self,ctx:SlashContext,file:str=None):
		if not file: data.saveAll()
		else: globals()[file].save()
		await ctx.send('successfully saved!')
		logOutput('fsaved',ctx)

	@cog_ext.cog_subcommand(base='dev',name='test',description='test stuffs, I have no clue.')
	@botOwner()
	async def dev_test(self,ctx:SlashContext):
		await ctx.defer()
		for user in users.read():
			try: users.write(self.client.get_user(int(user)).name,[user,'name'])
			except: continue
			print(f'added {user} - {self.client.get_user(int(user)).name}')
		await ctx.send('done')
	
	@cog_ext.cog_subcommand(base='dev',name='clear_console',description='clears the console.')
	async def dev_clear_console(self,ctx:SlashContext):
		os.system('clear')
		await ctx.send('successfully cleared console.')
		logOutput('console cleared',ctx)

	@cog_ext.cog_subcommand(base='dev',name='reload_file',description='reload a save file',
		options=[
			create_option('file','file you want to reload',str,True,[f.split('.json')[0] for f in [i[2] for i in os.walk(f'{os.getcwd()}/saves')][0]]),
			create_option('save','save the file first?',bool,False)])
	async def dev_reload_file(self,ctx:SlashContext,file,save:bool=False):
		if eval(f'{file}.reload({save})'): await ctx.send(f'successfully reloaded {file}')
		else: await ctx.send(f'failed to reload {file}')
		logOutput(f'reloaded {file}.json',ctx)

	@cog_ext.cog_subcommand(base='dev',name='note',description='add a note to a file')
	@botOwner()
	async def dev_note(self,ctx:SlashContext,note):
		with open('notes.txt','w+') as notes: notes.write(f'{note}\n')
		await ctx.send('successfully saved note')
		logOutput(f'note "{note}" saved',ctx)

def setup(client): client.add_cog(devTools(client))