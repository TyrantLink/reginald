import discord,requests
from logger import logOutput
from discord.ext.commands import Cog
from discord_slash import cog_ext,SlashContext
from discord_slash.utils.manage_commands import create_option

explorers = {'zano':'https://explorer.zano.org/api/get_info/4294967295'}


class crypto(Cog):
	@cog_ext.cog_subcommand(base='crypto',name='calculate',description='calculate crypto',
		options=[
			create_option('currency','full name of crypto',str,True,['zano']),
			create_option('hashrate','hashrate in MH',str,True),
			create_option('holdings','current coin holdings',str,True)
		])
	async def crypto_calculate(self,ctx:SlashContext,currency,hashrate,holdings):
		await ctx.defer()
		try: exchRate = float(requests.get(f'https://api.coingecko.com/api/v3/coins/{currency}').json()['market_data']['current_price']['usd']) # fetch 
		except: await ctx.send('failed to fetch exchange rate',hidden=True); return
		try: explorer = requests.get(explorers[currency]).json()['result']
		except: await ctx.send('failed to fetch network hashrate',hidden=True); return
		response = [f'Your hashrate: {hashrate} MH/s',f'Your holdings: {holdings} Zano',f'Your USD: ${round(holdings*exchRate,3)}']
		hashrate = hashrate*1000000
		posDiff = int(explorer['pos_difficulty'])
		networkHash = int(explorer['current_network_hashrate_350'])
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
		logOutput(f'{currency} stats requested',ctx)
	
	@cog_ext.cog_subcommand(base='crypto',name='exchange',description='convert crypto to USD')
	async def crypto_exchange(self,ctx:SlashContext,coin:str,amount:int):
		if '..' in coin: await ctx.send('invalid coin name.'); return
		try: exchRate = float(requests.get(f'https://api.coingecko.com/api/v3/coins/{coin.lower()}').json()['market_data']['current_price']['usd'])
		except: await ctx.send('failed to fetch exchange rate. is the coin name correct?',hidden=True); return
		await ctx.send(f'{format(float(amount),",.3f")} {coin} = ${format(exchRate*int(amount),",.3f")} USD')
		logOutput(f'exchange rate for {amount} {coin}',ctx)

def setup(client): client.add_cog(crypto(client))