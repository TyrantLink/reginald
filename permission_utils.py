import data
from discord.ext.commands import check

bot = data.load('bot')
owner_id = bot.read(['development','owner'])

def administrator(): # checks if the user has the administrator permission
	async def perms(ctx):
		if ctx.author.id == owner_id or ctx.author.guild_permissions.administrator: return True
		await ctx.send('You are not an admin.'); return False
	return check(perms)

def moderator(): # checks if the user has the manage server permission
	async def perms(ctx):
		if ctx.author.id == owner_id or ctx.author.guild_permissions.manage_guild: return True
		await ctx.send('You are not a moderator. (requires Manage Server)'); return False
	return check(perms)

def owner(): # checks if author is owner of guild
	async def perms(ctx):
		if ctx.author.id == owner_id or ctx.author.id == ctx.guild_id: return True
		await ctx.send('You are not the server owner.'); return False
	return check(perms)

def botOwner(): # checks if author is owner of bot
	async def perms(ctx):
		if ctx.author.id == owner_id: return True
		await ctx.send('You are not the bot owner.'); return False
	return check(perms)

def guild_only(): # checks message was sent in a guild
	def perms(ctx):
		if ctx.guild is None: raise Exception('This command can only be used in a guild.')
		return True
	return check(perms)

def dm_only(): # checks if message was sent in a direct message
	def perms(ctx):
		if ctx.guild is None: raise Exception('This command can only be used in a DM.')
		return True
	return check(perms)
