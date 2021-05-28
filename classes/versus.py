import asyncio
from os import device_encoding
from random import randint
import discord,json
from bot import client
from logger import logOutput
from discord.ext import commands
from discord_slash import cog_ext,SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option

versusData = json.loads(open('versus.json','r').read())
def save(): json.dump(versusData,open('versus.json','w+'),indent=2)
troubles = ["Need a Key!",
  "Safe Delivery...",
  "Price Adjustment",
  "Find this guy!",
  "Hit me, please!",
  "I'm hungry!",
  "Try to find me!",
  "Listen to me!",
  "Order me an item!",
  "Emergency Shroom!",
  "Play with me!",
  "Help my Daddy!",
  "Help Wanted!",
  "Heartful Cake Recipe...",
  "The food I want.",
  "Elusive Badge!",
  "Newsletter...",
  "Seeking Legendary Book!",
  "Tell that person...",
  "Looking for a gal!",
  "Important Thing!",
  "Get these ingredients!",
  "I must have that book.",
  "Security Code...",
  "Delivery, please!",
  "I can't speak!",
  "I wanna meet Luigi!",
  "Roust these cads!",
  "Help me make up.",
  "Erase that graffiti!"
]

class versus(commands.Cog):
  def __init__(self,client): self.client = client
  @cog_ext.cog_subcommand(base='versus',name='lifelines',description='list lifelines for given versus',options=[create_option('versus','pick a versus',str,True,list(versusData.keys()))],guild_ids=[847421655320100894])
  async def versus_lifelines(self,ctx:SlashContext,versus:str):
    await ctx.send(embed=discord.Embed(title=f'{versus} lifelines:',description='- ' + '\n- '.join([f'{lifeline}: {versusData[versus]["lifelines"][lifeline]}' for lifeline in versusData[versus]['lifelines']]),color=0x69ff69))
    logOutput(f'{versus} lifelines requested')
  @cog_ext.cog_subcommand(base='versus',name='lifeline',description='use a lifeline',options=[create_option('lifeline','choose a lifeline',str,True,list(versusData['TTYD-1']['lifelines'].keys()))],guild_ids=[847421655320100894])
  async def versus_lifeline(self,ctx:SlashContext,lifeline):
    if versusData['TTYD-1'][str(ctx.author.id)][lifeline] == 0: await ctx.send('you are out of that lifeline!'); return
    versusData['TTYD-1'][str(ctx.author.id)][lifeline] -= 1
    await ctx.send(f'{ctx.author.name} used {lifeline}')
    save()
    logOutput(f'{lifeline} used')
    if lifeline == 'prepare for trouble': await ctx.channel.send(f'trouble: {troubles[randint(0,len(troubles)-1)]}')
    else: await asyncio.sleep(1800); await ctx.channel.send(f'{ctx.author.name}\'s lifeline ({lifeline}) is up!')
def setup(client): client.add_cog(versus(client))