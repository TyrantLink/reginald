import logging,data

bot = data.load('bot')
logging.debug

def setupLogger(name,log_file,level=logging.WARNING): # initialize logger
	logger = logging.getLogger(name)
	formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] %(message)s','%m/%d/%Y %H:%M:%S')
	fileHandler = logging.FileHandler(log_file, mode='a',encoding='utf-8')
	fileHandler.setFormatter(formatter)
	logger.setLevel(level)
	logger.addHandler(fileHandler)
	return logger

outputLog=setupLogger('output log','logs/output.log')

def logOutput(log,ctx): # log to output.log file
	try: log = f'{log} in {ctx.guild.name} by {ctx.author.name}'
	except: log = f'{log} in DMs with {ctx.author.name}'
	outputLog.warning(log)
	if bot.read(['config','outputToConsole']): print(log)