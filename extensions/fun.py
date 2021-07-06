import discord,data,asyncio
from re import sub
from os import getenv
from requests import post
from random import randint,choice
from logger import logOutput
from datetime import datetime
from discord.ext.commands import Cog
from permission_utils import administrator,guild_only, moderator
from discord_slash import cog_ext,SlashContext
from discord_slash.utils.manage_commands import create_option


bot = data.load('bot')
servers = data.load('servers')
questions = data.load('questions')

class fun(Cog):
	def __init__(self,client): self.client = client

	@cog_ext.cog_slash(name='activities',description='invite an embedded application to a voice channel.',
		options=[create_option('activity','activity choice',str,True,list(bot.read(['activities']).keys()))])
	async def activities(self,ctx:SlashContext,activity):
		activity_id = bot.read(['activities',activity])
		if not ctx.author.voice: await ctx.send('you must be in a voice channel to use this command!')
		try: cache = servers.read([str(ctx.guild.id),'activities',str(ctx.author.voice.channel.id)])
		except KeyError: cache = []
		if str(activity_id) in cache: await ctx.send(f'[Click to Open {activity} in {ctx.author.voice.channel.name}](<https://discord.gg/{cache[str(activity_id)]}>)')
		else:
			invite = await ctx.author.voice.channel.create_invite(target_type=2,target_application_id=activity_id,reason=f'{activity} created in {ctx.channel.name}')
			try: servers.write(invite.code,[str(ctx.guild.id),'activities',str(ctx.author.voice.channel.id),str(activity_id)])
			except KeyError:
				servers.write({},[str(ctx.guild.id),'activities',str(ctx.author.voice.channel.id)])
				servers.write(invite.code,[str(ctx.guild.id),'activities',str(ctx.author.voice.channel.id),str(activity_id)])
			await ctx.send(f'[Click to Open {activity} in {ctx.author.voice.channel.name}](<https://discord.gg/{invite.code}>)')
		logOutput(f'{activity} invited',ctx)
	
	@cog_ext.cog_subcommand(base='clear',name='activity_cache',description='clear the activity invite cache.')
	@guild_only()
	@administrator()
	async def clear_activity_cache(self,ctx:SlashContext):
		servers.write({},[str(ctx.guild.id),'activities'])
		await ctx.send('successfully cleared activity invite cache.')
		logOutput('activity cache cleared',ctx)

	@cog_ext.cog_slash(name='hello',description='say hello to reginald.')
	async def hello(self,ctx:SlashContext):
		await ctx.send(file=discord.File('reginald.png'))
		logOutput(f'said hi to reginald',ctx)

	@cog_ext.cog_slash(name='roll',description='roll a die')
	async def roll(self,ctx:SlashContext,dice:int,sides:int,modifier:int=0):
		await ctx.defer()
		try: maxRoll = servers.read([str(ctx.guild.id),'config','maxRoll'])
		except: maxRoll = 16384
		if dice > maxRoll or sides > maxRoll or dice < 0 or sides < 0: await ctx.send(f'rolls must be between 0 and {maxRoll}!'); return
		result = modifier
		rolls = []
		for i in range(dice): roll = randint(1,sides); rolls.append(str(roll)); result+=roll
		try: await ctx.send(embed=discord.Embed(title=f'roll: {dice}d{sides}+{modifier}' if modifier>0 else f'roll: {dice}d{sides}',color=0x69ff69).add_field(name='rolls:',value=f'[{",".join(rolls)}]',inline=False).add_field(name='Result:',value=result,inline=False))
		except: await ctx.send(embed=discord.Embed(title=f'roll: {dice}d{sides}+{modifier}' if modifier>0 else f'roll: {dice}d{sides}',color=0x69ff69).add_field(name='rolls:',value='total rolls above character limit.',inline=False).add_field(name='Result:',value=result,inline=False))
		logOutput(f'roll {dice}d{sides}+{modifier} requested',ctx)

	@cog_ext.cog_slash(name='time',description='reginald can tell time')
	async def timecmd(self,ctx:SlashContext):
		await ctx.send(datetime.now().strftime("%H:%M:%S"))
		logOutput(f'time requested',ctx)

	@cog_ext.cog_slash(name='poll',description='run a poll.')
	@moderator()
	async def poll(self,ctx:SlashContext,title:str,description:str,optiona:str,optionb:str,optionc=None,optiond=None,other:discord.TextChannel=None):
		options = ['🇦','🇧']
		description = f'{description}\n\n🇦: {optiona}\n🇧: {optionb}'
		if optionc != None: description = f'{description}\n🇨: {optionc}'; options.append('🇨')
		if optiond != None: description = f'{description}\n🇩: {optiond}'; options.append('🇩')
		if other != None: description = f'{description}\nOther: please specify in {other}'; options.append('🇴')
		message = await ctx.send(embed=discord.Embed(title=title,description=description))
		for i in options: await message.add_reaction(i)
		logOutput('poll created',ctx)

	@cog_ext.cog_slash(name='8ball',description='ask the 8-ball a question.')
	async def eightball(self,ctx:SlashContext,question:str):
		await ctx.send(choice(questions.read(['8ball'])))
		logOutput('8ball rolled',ctx)

	@cog_ext.cog_slash(name='timer',description='start a timer',options=[create_option('label','timer label',str,True),create_option('time','amount of time',int,True),create_option('unit','unit of time',str,True,['second(s)','minute(s)','hour(s)'])])
	async def timer(self,ctx:SlashContext,label:str,time:int,unit:str):
		match unit:
			case 'second(s)': rtime = time
			case 'minute(s)': rtime = time*60
			case 'hour(s)': rtime = time*60*60
		await ctx.send(f'timer "{label}" for {time} {unit} started')
		logOutput(f'timer {label} started',ctx)
		await asyncio.sleep(rtime)
		await ctx.channel.send(f'{ctx.author.name}\'s timer "{label}" for {time} {unit} is over.')

	@cog_ext.cog_slash(name='color',description='generate a random color')
	async def color(self,ctx:SlashContext):
		color = hex(randint(0,16777215)).upper()
		res = [f'#{color[2:]}']
		res.append(f'R: {int(color[2:4],16)}')
		res.append(f'G: {int(color[4:6],16)}')
		res.append(f'B: {int(color[6:8],16)}')
		await ctx.send(embed=discord.Embed(title='random color:',description='\n'.join(res),color=int(color,16)))
		logOutput(f'random color #{color} generated',ctx)

	@cog_ext.cog_slash(name='shorten',description='shorten a url using s.nutt.dev',
		options=[
			create_option('url','e.g. example.com',str,True),
			create_option('name','name of link',str,True),
			create_option('path','s.nutt.dev/{path}, randomized if left empty',str,False)])
	async def shorten(self,ctx:SlashContext,url,name,path):
		await ctx.defer()
		url = sub(' ','',url)
		path = sub(' ','',path)
		linkData = {
			'title':name,
			'path':path,
			'domain':'s.nutt.dev',
			'originalURL':url}
		res = post('https://api.short.io/links',linkData,headers={'authorization':getenv('shortioKey')},json=True)
		match res.status_code:
			case 200: pass
			case 409: await ctx.send('error: that path is already taken!',hidden=True); return
			case _: await ctx.send(f'unknown error: status code {res.status_code}')
		await ctx.send(embed=discord.Embed(title='your link has been shortened:',description=res.json()['shortURL'],color=0x69ff69))
		logOutput(f'link {url} shortened to {res.json()["shortURL"]}',ctx)
		
def setup(client): client.add_cog(fun(client))