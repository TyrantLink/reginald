import os

sizes = {0:'bytes',1:'KBs',2:'MBs',3:'GBs',4:'TBs',5:'PBs',6:'EBs',7:'ZBs',8:'YBs'}



def getDirSize(dir):
	size = 0; sizeType = 0
	for path, dirs, files in os.walk(dir):
		for f in files: fp = os.path.join(path, f); size += os.path.getsize(fp)
	while size/1024 > 1: size = size/1024; sizeType += 1
	return f'{round(size,3)} {sizes[sizeType]}'

def convert_time(seconds,format='list'):
  minutes,hours,days = 0,0,0
  minutes = seconds // 60
  seconds = seconds % 60
  hours = minutes // 60
  minutes = minutes % 60
  days = hours // 24
  hours = hours % 24
  #return f'{days} days, {hours} hours, {minutes} minutes, {seconds} seconds'
  match format:
    case 'list': return [seconds,minutes,hours,days]
    case 'full_str': return f'{days} {"day" if days == 1 else "days"}, {hours} hours, {minutes} minutes, {seconds} seconds'
    case 'str': return f'{days} {"day" if days == 1 else "days"}, {str(hours).zfill(2)}:{str(minutes).zfill(2)}:{str(seconds).zfill(2)}'
    case _: return 'unknown format'
