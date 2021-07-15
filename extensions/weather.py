from requests import get
from discord.ext.commands import Cog
from discord_slash import cog_ext,SlashContext
from discord_slash.utils.manage_commands import create_option


class weather(Cog):
  def __init__(self,client): self.client = client

  @cog_ext.cog_slash(name='weather',description='get the weather',
    options=[
      create_option('area','for options, go to https://reginald.nutt.dev',str,True),
      create_option('format','measurement system',str,False,['c','f'])])
  async def weather(self,ctx:SlashContext,area=True):
    pass


def setup(client): pass