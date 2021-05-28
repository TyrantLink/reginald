import discord,json,data
from discord.ext import commands
from discord.ext.commands.core import guild_only
from bot import client,logOutput
from discord_slash import cog_ext,SlashContext
from discord_buttons import DiscordButton, Button, ButtonStyle, InteractionType

riceData = json.loads(open('ricePurity.json','r',encoding='utf-8').read())
ddb = DiscordButton(client)
ynButtons = [Button(style=ButtonStyle.green, label="Yes"),Button(style=ButtonStyle.red, label="No")]

class ricePurity(commands.Cog):
	def __init__(self,client): self.client = client
	@cog_ext.cog_subcommand(base='ricepurity',name='test',description='take the rice purity test.')
	@guild_only()
	async def ricepurity_test(self,ctx:SlashContext):
		await ctx.send('starting rice purity test...')
		channel = await client.fetch_channel(ctx.channel_id)
		message = await channel.send(f'{ctx.author.name}\nDo you want to take the rice purity test?',buttons=ynButtons)
		try: answer = await ddb.wait_for_button_click(message,None,60)
		except: await channel.send('test timed out'); return
		if answer.button.label == 'No': await message.edit('THEN WHY\'D YOU RUN THE COMMAND?'); await answer.respond(); return
		index = 1
		score = 100
		answers = []
		for question in riceData['test']:
			await message.edit(f'{ctx.author.name}\n{index}. {question}')
			await answer.respond()
			try: answer = await ddb.wait_for_button_click(message,None,60)
			except: await channel.send('test timed out'); return
			if index == 101 and answer.button.label == 'Yes': score = f'h{score}'; continue
			match answer.button.label:
				case 'Yes': answers.append(1); score -= 1
				case 'No': answers.append(0)
			index += 1
		await answer.respond()
		data.write(str(score),['users',str(ctx.author.id),'ricePurityScore'])
		riceData['results'][str(ctx.author.id)] = answers
		json.dump(riceData,open('ricePurity.json','w+',encoding='utf-8'),indent=2)
		await message.edit(f'Thank you for taking the rice purity test. Your score is {score}',supress=True)
		logOutput('rice purity test taken',ctx)


def setup(client): client.add_cog(ricePurity(client))