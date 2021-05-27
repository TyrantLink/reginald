import discord,logging,os
from time import time
from datetime import datetime
from discord.ext import commands
from bot import save,client,data


def setupLogger(name,log_file,level=logging.WARNING):
	logger = logging.getLogger(name)
	formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] %(message)s','%d/%m/%Y %H:%M:%S')
	fileHandler = logging.FileHandler(log_file, mode='a',encoding='utf-8')
	fileHandler.setFormatter(formatter)
	logger.setLevel(level)
	logger.addHandler(fileHandler)
	return logger


class msgLogger(commands.Cog):
	def __init__(self,client): self.client = client
	@commands.Cog.listener()
	async def on_ready(self):
		for guild in client.guilds: msgLogger.messageLoggers(guild.id)
		msgLogger.messageLoggers('DMs')
	@commands.Cog.listener()
	async def on_message(self,message):
		await msgLogger.logMessages(message,'s',' - image or embed') if message.content == "" else await msgLogger.logMessages(message,'s')
		try: msgLogger.messageCount(str(message.author.id), str(message.guild.id))
		except AttributeError or discord.errors.NotFound: pass
	@commands.Cog.listener()
	async def on_message_delete(self,message): await msgLogger.logMessages(message,'d',' - image or embed') if message.content == "" else await msgLogger.logMessages(message,'d')
	@commands.Cog.listener()
	async def on_bulk_message_delete(self,messages):
		for message in messages: await msgLogger.logMessages(message,'b',' - image or embed') if message.content == "" else await msgLogger.logMessages(message,'b')
	@commands.Cog.listener()
	async def on_message_edit(self,message_before,message_after):
		await msgLogger.logMessages(message_before,'e',message_after,' - image or embed') if message_after.content == "" else await msgLogger.logMessages(message_before,'e',message_after)
	def messageCount(author,guild=None):
		if author in data['variables']['messages']: data['variables']['messages'][author] += 1
		else: data['variables']['messages'].update({author:1})
		if guild != None:
			if author not in data['servers'][guild]['activeMembers'] and data['servers'][guild]['config']['enableTalkingStick']: data['servers'][guild]['activeMembers'].append(author)
		save(data)
	async def logMessages(ctx,type,ctx2=None,ext=''):
		try: guildID = ctx.guild.id
		except: guildID = 'DMs'
		match type:
			case 's':
				log=f'{ctx.author} sent "{ctx.content}" in {"" if ctx.guild == None else f"{ctx.guild} - "}{ctx.channel}{ext}'
				if data['botConfig']['msgToConsole'] and not (ctx.author.bot and not data['botConfig']['botToConsole']): print(f'{ctx.author.name} sent "{ctx.content}"')
				globals()[f'{guildID}_sent'].warning(log)
			case 'd':
				log=f'"{ctx.content}" by {ctx.author} was deleted in {"" if ctx.guild == None else f"{ctx.guild} - "}{ctx.channel}{ext}'
				for attachment in ctx.attachments: await attachment.save(f'{os.getcwd()}\\fileCache\\{datetime.fromtimestamp(time()).strftime("%d.%m.%Y %H.%M.%S.%f")[:-4]}.{attachment.filename.split(".")[len(attachment.filename.split("."))-1]}',use_cached=True)
				if data['botConfig']['msgToConsole'] and not (ctx.author.bot and not data['botConfig']['botToConsole']): print(f'{ctx.author.name} - "{ctx.content}" was deleted')
				globals()[f'{guildID}_delete'].warning(log)
			case 'b':
				log=f'"{ctx.content}" by {ctx.author} was purged in {"" if ctx.guild == None else f"{ctx.guild} - "}{ctx.channel}{ext}'
				for attachment in ctx.attachments: await attachment.save(f'{os.getcwd()}\\fileCache\\{datetime.fromtimestamp(time()).strftime("%d.%m.%Y %H.%M.%S.%f")[:-4]}.{attachment.filename.split(".")[len(attachment.filename.split("."))-1]}',use_cached=True)
				if data['botConfig']['msgToConsole'] and not (ctx.author.bot and not data['botConfig']['botToConsole']): print(f'{ctx.author.name} - "{ctx.content}" was bulk deleted')
				globals()[f'{guildID}_delete'].warning(log)
			case 'e':
				if ctx.content == ctx2.content: return
				log=f'{ctx.author} edited "{ctx.content}" into "{ctx2.content}" in {"" if ctx.guild == None else f"{ctx.guild} - "}{ctx.channel}{ext}'
				if data['botConfig']['msgToConsole'] and not (ctx.author.bot and not data['botConfig']['botToConsole']): print(f'{ctx.author.name} edited "{ctx.content}" into {ctx2.content}')
				globals()[f'{guildID}_edit'].warning(log)
	def messageLoggers(guild):
		while True:
			try:
				globals()[f'{guild}_sent']=setupLogger(f'{guild}_sent',f'logs/messages/{guild}/sent.log')
				globals()[f'{guild}_edit']=setupLogger(f'{guild}_edit',f'logs/messages/{guild}/edited.log')
				globals()[f'{guild}_delete']=setupLogger(f'{guild}_delete',f'logs/messages/{guild}/deleted.log')
			except: os.mkdir(f'logs/messages/{guild}'); continue
			break

def setup(client): client.add_cog(msgLogger(client))