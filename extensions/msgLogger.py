import discord,logging,data
from os import makedirs,getcwd,path
from datetime import datetime
from discord.ext.commands import Cog

bot = data.load('bot')
users = data.load('users')
servers = data.load('servers')

def setupLogger(name,log_file,level=logging.WARNING):
	logger = logging.getLogger(name)
	formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] %(message)s','%d/%m/%Y %H:%M:%S')
	fileHandler = logging.FileHandler(log_file, mode='a',encoding='utf-8')
	fileHandler.setFormatter(formatter)
	logger.setLevel(level)
	logger.addHandler(fileHandler)
	return logger

class msgLogger(Cog):
	def __init__(self,client): self.client = client

	@Cog.listener()
	async def on_ready(self):
		for guild in self.client.guilds: msgLogger.messageLoggers(self,guild.id)
		msgLogger.messageLoggers(self,'DMs')

	@Cog.listener()
	async def on_guild_join(self,guild):
		msgLogger.messageLoggers(self,guild.id)

	@Cog.listener()
	async def on_message(self,message):
		if message.guild:
			if str(message.guild.id) not in servers.read(): servers.new(str(message.guild.id))
		await msgLogger.logMessages(self,message,'s',' - image or embed') if message.content == "" else await msgLogger.logMessages(self,message,'s')
		try: msgLogger.messageCount(self,str(message.author.id), str(message.guild.id))
		except AttributeError or discord.errors.NotFound: msgLogger.messageCount(self,str(message.author.id))

	@Cog.listener()
	async def on_message_delete(self,message):
		await msgLogger.logMessages(self,message,'d',' - image or embed') if message.content == "" else await msgLogger.logMessages(self,message,'d')

	@Cog.listener()
	async def on_bulk_message_delete(self,messages):
		for message in messages: await msgLogger.logMessages(self,message,'b',' - image or embed') if message.content == "" else await msgLogger.logMessages(self,message,'b')
	
	@Cog.listener()
	async def on_message_edit(self,message_before,message_after):
		await msgLogger.logMessages(self,message_before,'e',message_after,' - image or embed') if message_after.content == "" else await msgLogger.logMessages(self,message_before,'e',message_after)

	def messageCount(self,author,guild=None):
		if author not in users.read([]): users.new(author)
		users.math('+',1,[author,'messages'])
		if guild != None:
			try: servers.read([guild,'messageLeaderboard',author])
			except: servers.write(0,[guild,'messageLeaderboard',author])
			servers.math('+',1,[guild,'messageLeaderboard',author])
			if int(author) not in servers.read([guild,'activeMembers']) and author not in servers.read([guild,'ignore']): servers.action('append',int(author),[guild,'activeMembers'])

	def messageLoggers(self,guild):
		while True:
			try:
				globals()[f'{guild}_sent']=setupLogger(f'{guild}_sent',f'logs/messages/{guild}/sent.log')
				globals()[f'{guild}_edit']=setupLogger(f'{guild}_edit',f'logs/messages/{guild}/edited.log')
				globals()[f'{guild}_delete']=setupLogger(f'{guild}_delete',f'logs/messages/{guild}/deleted.log')
			except: makedirs(f'logs/messages/{guild}'); continue
			break

	async def logMessages(self,ctx,type,ctx2=None,ext=''):
		if not self.client.is_ready(): return
		try: guildID = ctx.guild.id
		except: guildID = 'DMs'
		match type:
			case 's':
				log=f'[{ctx.id}] {ctx.author} sent "{ctx.content}" in {"" if ctx.guild == None else f"{ctx.guild} - "}{ctx.channel}{ext}'
				if bot.read(['config','msgToConsole']) and not (ctx.author.bot and not bot.read(['config','botmsgToConsole'])): print(f'{ctx.author.name} sent "{ctx.content}"')
				globals()[f'{guildID}_sent'].warning(log)
			case 'd':
				log=f'[{ctx.id}] "{ctx.content}" by {ctx.author} was deleted in {"" if ctx.guild == None else f"{ctx.guild} - "}{ctx.channel}{ext}'
				if len(ctx.attachments):
					if not path.exists(f'logs/messages/{guildID}/files'): makedirs(f'logs/messages/{guildID}/files')
					for attachment in ctx.attachments:
						try: await attachment.save(f'logs/messages/{guildID}/files/{datetime.now().strftime("%d.%m.%Y %H.%M.%S.%f")[:-4]}.{attachment.filename.split(".")[len(attachment.filename.split("."))-1]}',use_cached=True)
						except: print(f'failed to download deleted file in {ctx.guild.name}')
				if bot.read(['config','msgToConsole']) and not (ctx.author.bot and not bot.read(['config','botmsgToConsole'])): print(f'{ctx.author.name} - "{ctx.content}" was deleted')
				globals()[f'{guildID}_delete'].warning(log)
			case 'b':
				log=f'[{ctx.id}] "{ctx.content}" by {ctx.author} was purged in {"" if ctx.guild == None else f"{ctx.guild} - "}{ctx.channel}{ext}'
				if len(ctx.attachments):
					if not path.exists(f'logs/messages/{guildID}/files'): makedirs(f'logs/messages/{guildID}/files')
					for attachment in ctx.attachments:
						try: await attachment.save(f'logs/messages/{guildID}/files/{datetime.now().strftime("%d.%m.%Y %H.%M.%S.%f")[:-4]}.{attachment.filename.split(".")[len(attachment.filename.split("."))-1]}',use_cached=True)
						except: print(f'failed to download deleted file in {ctx.guild.name}')
				if bot.read(['config','msgToConsole']) and not (ctx.author.bot and not bot.read(['config','botmsgToConsole'])): print(f'{ctx.author.name} - "{ctx.content}" was bulk deleted')
				globals()[f'{guildID}_delete'].warning(log)
			case 'e':
				if ctx.content == ctx2.content: return
				log=f'[{ctx.id}] {ctx.author} edited "{ctx.content}" into "{ctx2.content}" in {"" if ctx.guild == None else f"{ctx.guild} - "}{ctx.channel}{ext}'
				if bot.read(['config','msgToConsole']) and not (ctx.author.bot and not bot.read(['config','botmsgToConsole'])): print(f'{ctx.author.name} edited "{ctx.content}" into {ctx2.content}')
				globals()[f'{guildID}_edit'].warning(log)

def setup(client): client.add_cog(msgLogger(client))