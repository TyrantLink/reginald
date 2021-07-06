import os

sizes = {0:'bytes',1:'KBs',2:'MBs',3:'GBs',4:'TBs',5:'PBs',6:'EBs',7:'ZBs',8:'YBs'}



def getDirSize(dir):
	size = 0; sizeType = 0
	for path, dirs, files in os.walk(dir):
		for f in files: fp = os.path.join(path, f); size += os.path.getsize(fp)
	while size/1024 > 1: size = size/1024; sizeType += 1
	return f'{round(size,3)} {sizes[sizeType]}'

def convert_time(seconds):
  minutes = seconds // 60
  seconds = seconds % 60
  hours = minutes // 60
  minutes = minutes % 60
  days = hours // 24
  hours = hours % 24
  if days: return f'{days} days, {hours} hours, {minutes} minutes, {seconds} seconds'
  if hours: return f'{hours} hours, {minutes} minutes, {seconds} seconds'
  if minutes: return f'{minutes} minutes, {seconds} seconds'
  if seconds: return f'{seconds} seconds'
  return False