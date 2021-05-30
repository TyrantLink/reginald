import discord,asyncio,data
from random import randint
from datetime import datetime
from discord.ext import commands
from discord.ext.commands.core import guild_only
from discord_slash import cog_ext,SlashContext
from bot import adminOrOwner, logOutput,client,questions
from discord_slash.utils.manage_commands import create_choice, create_option


activityList = {'Poker Night':755827207812677713,'Betrayal.io':773336526917861400,'YouTube Together':755600276941176913,'Fishington.io':814288819477020702,'Chess':832012586023256104}
eightBallResponses = ['It is certain','Without a doubt','You may rely on it','Yes definitely','It is decidedly so','As I see it, yes','Most likely','Yes','Outlook good','Signs point to yes','Reply hazy try again','Better not tell you now','Ask again later','Cannot predict now','Concentrate and ask again','Don’t count on it','Outlook not so good','My sources say no','Very doubtful','My reply is no']
save = data.load('save')


class fun(commands.Cog):
	def __init__(self,client): self.client = client
	@cog_ext.cog_subcommand(base='reginald',name='activites',description='invite an embedded application to a voice channel.',options=[create_option('activity','activity type',str,True,list(activityList.keys()))])
	async def reginald_activities(self,ctx:SlashContext,activity:str):
		activity_id = activityList[activity]
		if not ctx.author.voice: await ctx.send('you must be in a voice channel to use this command!')
		try: cache = save.read(['variables','activities',str(ctx.author.voice.channel.id)])
		except: save.write({},['variables','activities',str(ctx.author.voice.channel.id)]); cache = save.read(['variables','activities',str(ctx.author.voice.channel.id)])
		if str(activity_id) in cache: await ctx.send(f'[Click to Open {activity} in {ctx.author.voice.channel.name}](<https://discord.gg/{cache[str(activity_id)]}>)')
		else:
			invite = await ctx.author.voice.channel.create_invite(target_type=2,target_application_id=activity_id,reason=f'{activity} created in {ctx.channel.name}')
			save.write(invite.code,['variables','activities',str(ctx.author.voice.channel.id),str(activity_id)])
			await ctx.send(f'[Click to Open {activity} in {ctx.channel.name}](<https://discord.gg/{invite.code}>)')
	@cog_ext.cog_subcommand(base='reginald',name='activity_clear',description='clear activity cache if an invite was deleted.')
	@adminOrOwner()
	async def reginald_activity_clear(self,ctx:SlashContext):
		if not ctx.author.voice: await ctx.send('you must be in a voice channel to use this command!')
		save.write({},['variables','activities',str(ctx.author.voice.channel.id)])
		await ctx.send(f'successfully cleared activity cache for {ctx.author.voice.channel.mention}')
	@cog_ext.cog_subcommand(base='quotes',name='setup',description='setup quotes')
	async def quotes_setup(self,ctx:SlashContext,channel:discord.TextChannel):
		await ctx.send('quotes are temporarily disabled until I actually have some.'); return
		if not save.read(['servers',str(ctx.guild.id),'config','enableQuotes']): await ctx.send(embed=discord.Embed(title='Quotes are not enabled on this server.',color=0x69ff69)); return
		save.write(channel.id,['servers',str(ctx.guild.id),'quoteChannel'])
		await ctx.send(embed=discord.Embed(title='Setup Complete.',description=f'channel: <#{channel.id}>',color=0x69ff69))
		logOutput(f'quotes setup',ctx)
	@cog_ext.cog_subcommand(base='qotd',name='setup',description='setup QOTD')
	async def qotd_setup(self,ctx:SlashContext,channel:discord.TextChannel):
		if not save.read(['servers',str(ctx.guild.id),'config','enableQOTD']): await ctx.send(embed=discord.Embed(title='The QOTD is not enabled on this server.',color=0x69ff69)); return
		save.write(channel.id,['servers',str(ctx.guild.id),'qotdChannel'])
		await ctx.send(embed=discord.Embed(title='Setup Complete.',description=f'channel: <#{channel.id}>',color=0x69ff69))
		logOutput(f'qotd setup',ctx)
	@cog_ext.cog_subcommand(base='qotd',name='add',description='add a custom question to QOTD')
	async def qotd_add(self,ctx:SlashContext,question:str):
		if not question.endswith('?'): await ctx.send('that is not a valid question!'); return
		questions.append(question)
		await ctx.send(f'successfully added `{question}` to the question pool.')
	@cog_ext.cog_subcommand(base='reginald',name='hello',description='have reginald say hi.')
	async def hello_reginald(self,ctx:SlashContext):
		await ctx.send(file=discord.File('reginald.png'))
		logOutput(f'said hi to reginald',ctx)
	@cog_ext.cog_subcommand(base='reginald',name='roll',description='roll with modifiers')
	async def roll(self,ctx:SlashContext,dice:int,sides:int,modifiers:int=0):
		try: maxRoll = save.read(['servers',str(ctx.guild.id),'config','maxRoll'])
		except: maxRoll = 16384
		await ctx.defer()
		if dice > maxRoll or sides > maxRoll or dice < 0 or sides < 0: await ctx.send(f'rolls must be between 0 and {maxRoll}!'); return
		result = modifiers
		rolls = []
		for i in range(dice): roll = randint(1,sides); rolls.append(str(roll)); result+=roll
		try: await ctx.send(embed=discord.Embed(title=f'roll: {dice}d{sides}+{modifiers}' if modifiers>0 else f'roll: {dice}d{sides}',color=0x69ff69).add_field(name='rolls:',value=f'[{",".join(rolls)}]',inline=False).add_field(name='Result:',value=result,inline=False))
		except: await ctx.send(embed=discord.Embed(title=f'roll: {dice}d{sides}+{modifiers}' if modifiers>0 else f'roll: {dice}d{sides}',color=0x69ff69).add_field(name='rolls:',value='total rolls above character limit.',inline=False).add_field(name='Result:',value=result,inline=False))
		logOutput(f'roll {dice}d{sides}+{modifiers} requested',ctx)
	@cog_ext.cog_subcommand(base='leaderboard',name='messages',description='leaderboard of total messages sent.')
	async def leaderboard_messages(self,ctx:SlashContext):
		save.write({key:value for key,value in sorted(save.read(['variables','messages']).items(),key=lambda item: item[1],reverse=True)},['variables','messages'])
		names = []
		index = 1
		await ctx.defer()
		for member in save.read(['variables','messages']):
			if index > 50: break
			if member not in save.read(['variables','idNameCache']):
				try: save.write((await client.fetch_user(member)).name,['variables','idNameCache',member])
				except: continue
			rank = str(index)+("th" if 4<=index%100<=20 else {1:"st",2:"nd",3:"rd"}.get(index%10, "th")); index += 1
			names.append(f"{rank} - {save.read(['variables','idNameCache',member])}: {save.read(['variables','messages',member])}")
		await ctx.send(embed=discord.Embed(title='Messages:',description='\n'.join(names),color=0x69ff69))
		logOutput(f'message leaderboard requested',ctx)
	@cog_ext.cog_subcommand(base='reginald',name='time',description='reginald can tell time.')
	async def reginald_time(self,ctx:SlashContext):
		await ctx.send(datetime.now().strftime("%H:%M:%S"))
		logOutput(f'time requested',ctx)
	@cog_ext.cog_subcommand(base='reginald',name='poll',description='run a poll.')
	async def reginald_poll(self,ctx:SlashContext,title:str,description:str,optiona:str,optionb:str,optionc=None,optiond=None,other:discord.TextChannel=None):
		options = ['🇦','🇧']
		description = f'{description}\n\n🇦: {optiona}\n🇧: {optionb}'
		if optionc != None: description = f'{description}\n🇨: {optionc}'; options.append('🇨')
		if optiond != None: description = f'{description}\n🇩: {optiond}'; options.append('🇩')
		if other != None: description = f'{description}\nOther: please specify in {other}'; options.append('🇴')
		message = await ctx.send(embed=discord.Embed(title=title,description=description))
		for i in options: await message.add_reaction(i)
		logOutput('poll created',ctx)
	@cog_ext.cog_subcommand(base='reginald',name='8ball',description='ask the 8-ball a question.')
	async def reginald_8ball(self,ctx:SlashContext,question:str):
		await ctx.send(eightBallResponses[randint(0,len(eightBallResponses)-1)])
		logOutput('8ball rolled',ctx)
	@cog_ext.cog_subcommand(base='reginald',name='timer',description='start a timer',options=[create_option('label','timer label',str,True),create_option('time','amount of time',int,True),create_option('unit','unit of time',str,True,['second(s)','minute(s)','hour(s)'])])
	async def reginald_timer(self,ctx:SlashContext,label:str,time:int,unit:str):
		# time = int(time)
		match unit:
			case 'second(s)': time = time
			case 'minute(s)': time = time/60
			case 'hour(s)': time = time/60/60
		await ctx.send(f'timer "{label}" for {time} {unit} started')
		await asyncio.sleep(time)
		await ctx.channel.send(f'{ctx.author.name}\'s timer "{label}" for {time} {unit} is over.')
	@cog_ext.cog_subcommand(base='reginald',name='color',description='generate a random color')
	async def reginald_color(self,ctx:SlashContext):
		color = hex(randint(0,16777215)).upper()
		res = [f'#{color[2:]}']
		res.append(f'R: {int(color[2:4],16)}')
		res.append(f'G: {int(color[4:6],16)}')
		res.append(f'B: {int(color[6:8],16)}')
		await ctx.send(embed=discord.Embed(title='random color:',description='\n'.join(res),color=int(color,16)))

def setup(client): client.add_cog(fun(client))