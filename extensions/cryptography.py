import discord
from logger import logOutput
from discord.ext.commands import Cog
from discord_slash import cog_ext,SlashContext
from discord_slash.utils.manage_commands import create_option
from base64 import b64encode,b64decode

supportedAlgos = ['base64','caesar cipher']

class cryptography(Cog):
	@cog_ext.cog_slash(name='encode',description='encode a message with various algorithms',
		options=[
			create_option('message','message you want to encode',str,True),
			create_option('algorithm','algorithm to encode with',str,True,supportedAlgos),
			create_option('arg','different use depending on algorithm refer to /help',str,False),
			create_option('passphrase','some algorithms require a passphrase',str,False),
			create_option('hidden','choose whether you send this as a hidden message or not.',bool,False)])
	async def encode_cmd(self,ctx:SlashContext,message,algorithm,arg=None,passphrase=None,hidden=False):
		match algorithm:
			case 'base64': response = b64encode(message.encode()).decode()
			case 'caesar cipher':
				if arg == None: arg = 7
				response = ''.join([c if c == ' ' else chr((ord(c) + int(arg) - 65) % 26 + 65) if c.isupper() else chr((ord(c) + int(arg) - 97) % 26 + 97) for c in message])
			case _: response = 'unknown algorithm'
		await ctx.send(response,hidden=hidden)
		logOutput(f'encoded "{message}" in {algorithm}',ctx)

	@cog_ext.cog_slash(name='decode',description='decode a message with various algorithms',
		options=[
			create_option('message','message you want to encode',str,True),
			create_option('algorithm','algorithm to decode with',str,True,supportedAlgos),
			create_option('arg','different use depending on algorithm refer to /help',str,False),
			create_option('passphrase','some algorithms require a passphrase',str,False),
			create_option('hidden','choose whether you send this as a hidden message or not.',bool,False)])
	async def decode_cmd(self,ctx:SlashContext,message,algorithm,arg=None,passphrase=None,hidden=False):
		match algorithm:
			case 'base64': response = b64decode(message.encode()).decode()
			case 'caesar cipher':
				if arg == None: arg = 7
				response = ''.join([c if c == ' ' else chr((ord(c) - int(arg) - 65) % 26 + 65) if c.isupper() else chr((ord(c) - int(arg) - 97) % 26 + 97) for c in message])
			case _: response = 'unknown algorithm'
		await ctx.send(response,hidden=hidden)
		logOutput(f'decoded "{message}" in {algorithm}',ctx)

def setup(client): client.add_cog(cryptography(client))