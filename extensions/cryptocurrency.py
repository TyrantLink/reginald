import discord,requests,re,data
from logger import logOutput
from tyrantLib import convert_time
from discord.ext.commands import Cog
from discord_slash import cog_ext,SlashContext
from permission_utils import botOwner
from discord_slash.utils.manage_commands import create_option

explorers = {'zano':'https://explorer.zano.org/api/get_info/4294967295'}
bot = data.load('bot')

class cryptocurrency(Cog):
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
		hashrate = float(hashrate); holdings = float(holdings)
		response = [f'Your hashrate: {hashrate} MH/s',f'Your holdings: {holdings} Zano',f'Your USD: ${round(holdings*exchRate,3)}']
		hashrate = hashrate*1000000
		posDiff = int(explorer['pos_difficulty'])
		networkHash = int(explorer['current_network_hashrate_350'])
		timeToBlock = round(100/(hashrate/networkHash*100/2),2)
		zanoDay = round(1440/(100/(hashrate/networkHash*100)),3)/2
		usdDay = round(1440/(100/(hashrate/networkHash*100))*exchRate,3)/2
		posEarnings = holdings*720/(posDiff/1000000000000/100)
		response += [
			f'Network hashrate: {round(networkHash/1000000000,3)} GH/s',
			f'Zano price: ${format(exchRate,".3f")}',
			f'Chance of mining next block: {format(round(hashrate/networkHash*100/2,3),".3f")}%',
			f'Est. time to PoW mine block: {timeToBlock} minutes | {round(timeToBlock/60,2)} hours',
			f'Est. time to PoS mine block: {round(100/posEarnings,2)} minutes | {round(100/posEarnings/60,2)} hours',
			f'Est. PoS Earnings: {round(posEarnings,5)} Zano',
			f'Zano/day: {zanoDay}',
			f'Zano/month: {round(zanoDay*30,3)}',
			f'Zano/year: {round(zanoDay*365,3)}',
			f'USD/day: ${usdDay}',
			f'USD/month: ${round(usdDay*30,3)}',
			f'USD/year: ${round(usdDay*365,3)}']
		await ctx.send(embed=discord.Embed(title='Your Zano Stats:',description='\n'.join(response),color=bot.read(['config','embedColor'])))
		logOutput(f'{currency} stats requested',ctx)
	
	@cog_ext.cog_subcommand(base='crypto',name='exchange',description='convert crypto to USD')
	async def crypto_exchange(self,ctx:SlashContext,coin:str,amount:int=1):
		if '..' in coin: await ctx.send('invalid coin name.'); return
		try: exchRate = float(requests.get(f'https://api.coingecko.com/api/v3/coins/{coin.lower()}').json()['market_data']['current_price']['usd'])
		except: await ctx.send('failed to fetch exchange rate. is the coin name correct?',hidden=True); return
		await ctx.send(f'{format(float(amount),",.3f")} {coin} = ${format(exchRate*int(amount),",.3f")} USD')
		logOutput(f'exchange rate for {amount} {coin}',ctx)

	@cog_ext.cog_subcommand(base='crypto',subcommand_group='miner',name='stats',description='view my mining stats, i guess')
	async def crypto_miner_stats(self,ctx:SlashContext):
		summary = requests.get('http://127.0.0.1:4067/summary').json()
		results = {
			'pool':re.sub(r'stratum1\+tcp:\/\/|:\d{0,6}','',summary['active_pool']['url']),
			'uptime':convert_time(summary['uptime'],'full_str'),
			'hashrate':f'{round(summary["hashrate"]/1000000,3)} MH/s',
			'average hashrate (day)':f'{round(summary["hashrate_day"]/1000000,3)} MH/s',
			'average hashrate (hour)':f'{round(summary["hashrate_hour"]/1000000,3)} MH/s',
			'average hashrate (minute)':f'{round(summary["hashrate_minute"]/1000000,3)} MH/s',
			'accepted shares':summary['accepted_count'],
			'paused':summary['paused']}
		await ctx.send(embed=discord.Embed(title='Zano Miner',description='\n'.join([f'{i}: {results[i]}' for i in results]),color=bot.read(['config','embedColor'])))
		logOutput('mining stats requested',ctx)
	
	@cog_ext.cog_subcommand(base='crypto',subcommand_group='miner',name='pause',description='pause the miner')
	@botOwner()
	async def crypto_miner_pause(self,ctx:SlashContext):
		if requests.get('http://127.0.0.1:4067/control?pause=true').status_code == 200: await ctx.send('successfully paused miner'); return
		await ctx.send('failed to pause miner')
	
	@cog_ext.cog_subcommand(base='crypto',subcommand_group='miner',name='unpause',description='pause the miner')
	@botOwner()
	async def crypto_miner_unpause(self,ctx:SlashContext):
		if requests.get('http://127.0.0.1:4067/control?pause=false').status_code == 200: await ctx.send('successfully unpaused miner'); return
		await ctx.send('failed to unpause miner')

def setup(client): client.add_cog(cryptocurrency(client))