import discord,data,re
from os import getcwd
from discord.ext.commands import Cog

bot = data.load('bot')
servers = data.load('servers')
qa = data.load('autoResponses')
userqa = qa.read(['userqa'])
godqa = qa.read(['godqa'])
fileqa = qa.read(['fileqa'])


class autoResponses(Cog):
	def __init__(self,client): self.client = client

	@Cog.listener()
	async def on_message(self,ctx):
		if ctx.guild:
			try: guild = servers.read([str(ctx.guild.id)])
			except: guild = servers.read(['0'])
		else: guild = servers.read(['0'])
		if ctx.author.id in guild['ignore'] or ctx.author == self.client.user: return
		if guild['config']['enableAutoResponses'] and not ctx.author.bot: await autoResponses.autoResponse(self,ctx)
		if guild['config']['enableDadBot'] and not ctx.author.bot: await autoResponses.dadBot(self,ctx)

	async def autoResponse(self,ctx):
		if ctx.author.id == self.client.owner_id:
			if ctx.content in userqa and not bot.read(['config','godExempt']): await ctx.channel.send(userqa[ctx.content]); return
			if ctx.content in fileqa and not bot.read(['config','godExempt']): await ctx.channel.send(file=discord.File(f'{getcwd()}/memes/{fileqa[ctx.content]}')); return
			if ctx.content in godqa: await ctx.channel.send(godqa[ctx.content]); return
		else:
			if ctx.content in userqa: await ctx.channel.send(userqa[ctx.content]); return
			if ctx.content in fileqa: await ctx.channel.send(file=discord.File(f'{getcwd()}/memes/{fileqa[ctx.content]}')); return
		
	async def dadBot(self,ctx):
		if ctx.author.id == self.client.owner_id and bot.read(['config','godExempt']): return
		message = re.sub(r'<(@!|@)\d{18}>','[REDACTED]',ctx.content)
		for splitter in ["I'm ","im ","I am "]:
			res = re.search(splitter,message,re.IGNORECASE)
			if res == None: continue
			try:
				if res.span()[0] == 0: resString = message.split(splitter)[1]; break
			except: continue
			try:
				if message[res.span()[0]-1] == ' ': resString = message.split(splitter)[1]; break
			except: continue
		else: return
		try: await ctx.channel.send(re.sub('  ',' ',f'hi {resString}, {splitter} {ctx.guild.me.name}'))
		except: await ctx.channel.send(re.sub('  ',' ',f'hi {resString[:1941]} (character limit), {splitter} {ctx.guild.me.name}'))

def setup(client): client.add_cog(autoResponses(client))