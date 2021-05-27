import logging,json

def setupLogger(name,log_file,level=logging.WARNING):
	logger = logging.getLogger(name)
	formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] %(message)s','%d/%m/%Y %H:%M:%S')
	fileHandler = logging.FileHandler(log_file, mode='a',encoding='utf-8')
	fileHandler.setFormatter(formatter)
	logger.setLevel(level)
	logger.addHandler(fileHandler)
	return logger

outputLog=setupLogger('output log','logs/output.log')
outputToConsole=json.loads(open('save.json','r').read())['botConfig']['outputToConsole']

def logOutput(log,ctx):
		try: log = f'{log} in {ctx.guild.name} by {ctx.author.name}'
		except: log = f'{log} in DMs with {ctx.author.name}'
		outputLog.warning(log)
		if outputToConsole: print(log)