from os import device_encoding
import discord,json
from bot import data,client
from logger import logOutput
from discord.ext import commands
from discord_slash import cog_ext,SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option

versusData = json.loads(open('versus.json','r').read())
def save(): json.dump(versusData,open('versus.json','w+'),indent=2)

class versus(commands.Cog):
  def __init__(self,client): self.client = client
  @cog_ext.cog_subcommand(base='versus',name='lifelines',description='list lifelines for given versus',options=[create_option('versus','pick a versus',str,True,list(versusData.keys()))],guild_ids=[847421655320100894])
  async def versus_lifelines(self,ctx:SlashContext,versus:str):
    await ctx.send(embed=discord.Embed(title=f'{versus} lifelines:',description='- ' + '\n- '.join([f'{lifeline}: {versusData[versus]["lifelines"][lifeline]}' for lifeline in versusData[versus]['lifelines']]),color=0x69ff69))
    
    # 

def setup(client): client.add_cog(versus(client))