import discord,re,json
from discord.ext import commands
from discord.ext.commands import is_owner
from bot import data,client,logOutput,save
from discord_slash import cog_ext,SlashContext
from discord_buttons import DiscordButton, Button, ButtonStyle, InteractionType

ddb = DiscordButton(client)
testingServer=[844127424526680084]

class devTools(commands.Cog):
	def __init__(self,client): self.client = client
	@cog_ext.cog_subcommand(base='dev',name='commit',description='push a commit to the change-log channel',guild_ids=testingServer)
	@is_owner()
	async def reginald_dev_commit(self,ctx:SlashContext,title:str,features:str=None,fixes:str=None,notes:str=None,newversion:bool=True,test:bool=False):
		await ctx.defer()
		versionLoad = json.loads(open('save.json','r').read())['information']['version']
		if newversion: versionLoad = versionLoad+0.01
		version = round(versionLoad,2)
		channel = await client.fetch_channel(844133317041061899) if test else await client.fetch_channel(data['information']['change-log-channel'])
		response = f'version: {format(version,".2f")}\n\n'
		if features != None: features = '- ' + '\n- '.join(features.split(r'\n')); response += f'features:\n{features}\n\n'
		if fixes != None: fixes = '- ' + '\n- '.join(fixes.split(r'\n')); response += f'fixes / changes:\n{fixes}\n\n'
		if notes != None: notes = '- ' + '\n- '.join(notes.split(r'\n')); response += f'notes:\n{notes}\n\n'
		response += f'these features are new, remember to report bugs with /reginald issue\ncommands may take up to an hour to update globally.\n[follow development](<https://discord.gg/4mteVXBDW7>)'
		for i in re.findall(r'issue\d+',response): response = re.sub(r'issue\d+',f"([issue#{i.split('issue')[1]}](<https://discord.com/channels/844127424526680084/844131633787699241/{data['variables']['issues'][int(i.split('issue')[1])-1]}>))",response,1)
		for i in re.findall(r'suggestion\d+',response): response = re.sub(r'suggestion\d+',f"([suggestion#{i.split('suggestion')[1]}](<https://discord.com/channels/844127424526680084/844130469197250560/{data['variables']['suggestions'][int(i.split('suggestion')[1])-1]}>))",response,1)
		message = await channel.send(embed=discord.Embed(title=title,description=response,color=0x69ff69))
		if not test: await message.publish()
		data['information']['version'] = versionLoad
		save(data)
		await ctx.send('successfully pushed change.')
		logOutput(f'new commit pushed',ctx)
	@cog_ext.cog_subcommand(base='reginald',name='suggest',description='suggest a feature for reginald')
	async def reginald_suggest(self,ctx:SlashContext,suggestion:str,details:str):
		await ctx.defer()
		suggestCount = json.loads(open('save.json','r').read())['information']['suggestCount']
		suggestCount += 1
		if r'\n' in details: details = '- ' + '\n- '.join(details.split(r'\n'))
		channel = await client.fetch_channel(data['information']['suggestions-channel'])
		message = await channel.send(embed=discord.Embed(title=f"{suggestion} | #{suggestCount}",description=f'suggested by: {ctx.author.mention}\n\ndetails:\n{details}',color=0x69ff69))
		for i in ['👍','👎']: await message.add_reaction(i)
		await ctx.send('thank you for your suggestion!')
		data['variables']['suggestions'].append(int(message.jump_url.split('/')[-1]))
		data['information']['suggestCount'] = suggestCount
		save(data)
		logOutput(f'new suggestion "{suggestion}"',ctx)
	@cog_ext.cog_subcommand(base='reginald',name='issue',description='report an issue with reginald')
	async def reginald_issue(self,ctx:SlashContext,issue:str,details:str):
		await ctx.defer()
		issueCount = json.loads(open('save.json','r').read())['information']['issueCount']
		issueCount += 1
		channel = await client.fetch_channel(data['information']['issues-channel'])
		message = await channel.send(embed=discord.Embed(title=f"{issue} | #{issueCount}",description=f'suggested by: {ctx.author.mention}\n\ninformation:\n{details}',color=0x69ff69))
		for i in ['<:open:847372839732379688>','👍','👎']: await message.add_reaction(i)
		data['variables']['issues'].append(int(message.jump_url.split('/')[-1]))
		data['information']['issueCount'] = issueCount
		save(data)
		await ctx.send('thank you for reporting this issue!')
		logOutput(f'new issue {issue}',ctx)
	@cog_ext.cog_subcommand(base='dev',name='test',description='used for testing',guild_ids=[844127424526680084,786716046182187028])
	@is_owner()
	async def reginald_dev_test(self,ctx:SlashContext,message:str):
		for user in data['users']:
			data['users'][user]['ricePurityScore'] = 'untaken'
	@cog_ext.cog_subcommand(base='reginald',name='exec',description='execute any python command on host computer.')
	@is_owner()
	async def reginald_dev_execute(self,ctx:SlashContext,function:str):
		await ctx.send(str(eval(function)),hidden=True)
		logOutput(f'{function} executed',ctx)
	@cog_ext.cog_subcommand(base='reginald',name='asyncexec',description='execute any async python command on host computer.')
	@is_owner()
	async def reginald_dev_asyncExecute(self,ctx:SlashContext,function:str):
		await ctx.send(str(await eval(function)),hidden=True)
		logOutput(f'{function} executed',ctx)
	@cog_ext.cog_subcommand(base='reginald',name='clearidcache',description='clears ID cache variable')
	@is_owner()
	async def clearIDcache(self,ctx:SlashContext):
		data['variables']['idNameCache'] = {}
		await ctx.send('successfully cleared ID cache')
		save(data)
		logOutput(f'idNameCache cleared',ctx)

def setup(client): client.add_cog(devTools(client))