import discord,json,requests
from bot import logOutput
from discord.ext import commands
from discord_slash import cog_ext,SlashContext

class crypto(commands.Cog):
	def __init__(self,client): self.client = client
	@cog_ext.cog_subcommand(base='crypto',subcommand_group='calculate',name='zano',description='calculate zano stats')
	async def crypto_calculate_zano(self,ctx:SlashContext,hashrate:float,holdings:float):
		try: exchRate = float(json.loads(requests.get('https://api.coingecko.com/api/v3/coins/zano').text)['market_data']['current_price']['usd']); zanoExplorer = json.loads(requests.get('https://explorer.zano.org/api/get_info/4294967295').text)['result']
		except: await ctx.send('failed to fetch exchange rate',hidden=True); return
		hashrate = float(hashrate); holdings = float(holdings)
		response = []
		response.append(f'Your hashrate: {hashrate} MH/s')
		response.append(f'Your holdings: {holdings} Zano')
		response.append(f'Your USD: ${round(holdings*exchRate,3)}')
		hashrate = hashrate*1000000
		posDiff = int(zanoExplorer['pos_difficulty'])
		networkHash = int(zanoExplorer['current_network_hashrate_350'])
		timeToBlock = round(100/(hashrate/networkHash*100/2),2)
		zanoDay = round(1440/(100/(hashrate/networkHash*100)),3)/2
		usdDay = round(1440/(100/(hashrate/networkHash*100))*exchRate,3)/2
		posEarnings = holdings*720/(posDiff/1000000000000/100)
		response.append(f'Network hashrate: {round(networkHash/1000000000,3)} GH/s')
		response.append(f'Zano price: ${format(exchRate,".3f")}')
		response.append(f'Chance of mining next block: {format(round(hashrate/networkHash*100/2,3),".3f")}%')
		response.append(f'Est. time to PoW mine block: {timeToBlock} minutes | {round(timeToBlock/60,2)} hours')
		response.append(f'Est. time to PoS mine block: {round(100/posEarnings,2)} minutes | {round(100/posEarnings/60,2)} hours')
		response.append(f'Est. PoS Earnings: {round(posEarnings,5)} Zano')
		response.append(f'Zano/day: {zanoDay}')
		response.append(f'Zano/month: {round(zanoDay*30,3)}')
		response.append(f'Zano/year: {round(zanoDay*365,3)}')
		response.append(f'USD/day: ${usdDay}')
		response.append(f'USD/month: ${round(usdDay*30,3)}')
		response.append(f'USD/year: ${round(usdDay*365,3)}')
		await ctx.send(embed=discord.Embed(title='Your Zano Stats:',description='\n'.join(response),color=0x69ff69))
		logOutput(f'zano stats requested',ctx)
	@cog_ext.cog_subcommand(base='crypto',name='exchange',description='get worth of currency in usd.')
	async def crypto_exchange(self,ctx:SlashContext,coin:str,amount:int):
		if '..' in coin: await ctx.send('invalid coin name.'); return
		try: exchRate = float(json.loads(requests.get(f'https://api.coingecko.com/api/v3/coins/{coin.lower()}').text)['market_data']['current_price']['usd'])
		except: await ctx.send('failed to fetch exchange rate. is the coin name correct?',hidden=True); return
		await ctx.send(f'{format(float(amount),",.3f")} {coin} = ${format(exchRate*int(amount),",.3f")} USD')
		logOutput(f'exchange rate for {amount} {coin}',ctx)
	
def setup(client): client.add_cog(crypto(client))