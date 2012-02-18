"""
	Joe Young, December 2011

	__init__.py for ceil2ff package. This code is the front end, and will do all the logic,
	as derived from UUAdip.

	Saves each profile in a single line [flat file]

	TTTTTTTTTT,RG,DDDDD.DDD,DDDDD.DDD,DDDDD.DDD,DDDDD.DDD,...

	T = unix timestamp
	RG = Range gate in meters, how far apart is each ob, starting at 0
	SH = starting height, elevation of the observation NOTE!!! == 0 ALWAYS!!
	D = backscatter coefficient value in m^-1 s^-1
"""

import os,calendar,time
from numpy import append,zeros
import numpy as np
import ob as obc 
import save as sv
#from obs import IDprofile
from ceil2ff.obs.formats import *
#import Nio
from  scipy.io.netcdf import netcdf_file as nc


__all__ = ['obs','peek']

import obs

def compressFile(input_file,out='./ceil.nc'):
	"""
	Compress only a specific file.
	
	Inputs:
		filename    = absolute reference to the file to be read
		out         = Filename where data are saved

	"""	
	files = [input_file]
	save(files,out)

def compressDir(directory='.',out='./ceil.nc'):
	"""
		Read in Ceilometer data from raw data files
		
	"""
	print "Attempting to read Vaisala Ceilometer Data"
	if not directory[-1] == "/":
		directory += "/"
	stime = time.time() # for efficiency monitoring purposes.
	# BEGIN - *recursively* open every file in the provided directories!
	# do not open the same file twice.
	files = [directory + F for F in os.listdir(directory)] # not currently recursive...
	save(files,out)

def save(files,out_fname):
	#f = open(out,'w')
	# save netcdf
	###f = nc(out,'w')
	t=False
	s=False
	d=False #initialize...
	for fd in files:
		# check that the file is a file:
		if os.path.isdir(fd):
			continue # fail quietly
		fn = fd.split("/")[-1]
		if fn[0] == ".":
			continue # binary file, fail quietly
		if ".dat" not in fn and ".DAT" not in fn:
			#FIXME - failsafe - only open .dat
			continue

		print "reading",fn
		
		out = getObs(fd,t,s,d) # this retuns the entire coded ob set, a list of ob objects
		if not out:
			continue
		else:
			t,s,d = out

		"""
		if not obs or len(obs) == 0:
			print "No profiles found."
			continue #move on to the next file
		profs = []
		times = []
		hts = []
		statl = [] # for cloud/status infomrmation
		for ob in obs:
			# heights, time, values, and the extra fun stuff (clouds, stats, whatnot)
			profs.append(ob['v'])  # this is the entire profile.
			times.append(ob['t'])  # this is the time of the ob
			hts.append(ob['h']) # this is just the distance between range gates
			statl.append(ob['c']) # get status/cloud information
			
		#profs = profs # do not flip!! # not saving log10'd!!!!!!!!!! 
		# then loop through the data - AND ASSEMBLE THE DATA LINE!
		text = "" # the first character, blank thanks to the new format
		for i in range(len(profs)):
			# now each i is a key to an entire profile
			text = str(times[i])+','+str(hts[i])+','+statl[i] # add the time, RG, status info
			# now loop through the data and add to the line
			for d in profs[i]:
				text += ','+str(d)
			text += "\n" # add the requisite newline!
			f.write(text)
		"""
	if type(t) == bool:
		print "Didn't find anything"
		exit()
	print "Found",time_index,"profiles!"
	print "Saving"
	f = nc(out_fname,'w')

	# create the dimensions and variables
	f.createDimension('time',time_index) # can have unlimited time values
	#f.create_dimension('status',100)
	f.createDimension('range',1000) # these netCDfs will not be able to handle varying vertical dimensions!

	# create the netCDF variables
	f.createVariable('time','d',('time',)) #this will hold the times (as a list of times!)
	f.createVariable('status','S1',('time',))
	#f.create_variable('range','f',('range',))
	f.createVariable('data','d',('time','range'))

	f.variables['time'][:] = t
	f.variables['status'][:] = s
	f.variables['data'][:] = d

	f.close()
	return True

time_index = 0 # hopefully this will be global?
def getObs(fd,t,s,d):
	"""
		Grabs the obs from the given file by exploding it, and then passing the 
		sliced up obs to the parsers (raw_ob) which will then read out the information!
	"""
	global time_index
	in_time = True # holder for restrictions
	# well, here is the file!
	f = open(fd,'r')
	# now the file is open, read through it and save each identifyable profile
	# split by control character unichr(3), then shave off the top of these elements
	bom25 = unichr(1) # ct25/cl31 specific BOM key
	borm = unichr(2) # beginning of message (^B in VI)
	eorm = unichr(3) # ct25/ct12 EOM character / UNIVERSAL end of data string
	eom31 = unichr(4) # cl31 specific EOM key

	# FIXME - if the file is too big, maybe read it in chunks?
	fl = f.read() # put the whole thing into a string
	f.close()
	
	if len(fl) == 0:
		# well, that file is a dud.
		return False
	# determine what is the true eom character
	if eom31 in fl:
		# this is a CL31 message!!!
		split  = eom31
		code_split = bom25
	elif bom25 in fl:
		# this is a CT25 message!!!
		split = eorm
		code_split = bom25
	else:
		split = eorm
		code_split = False
	# ok, then we can split this by the split, which is the message end.

	fobs = fl.split(split)

	tsb = True # boolean - true indicates time stamp before message

	if borm not in fobs[-1]:
		# then the time follows the message! 
		# the last element is a time, not a message
		# now I have to factor this information in
		tsb = False

	# this works robustly for Vaisala ceilometers
	
	# add the number of obs in this file #FIXME the number of obs may not equal number of times... bleh
	if not type(t) == bool:
		t = append(t,zeros(len(fobs)))
		s = append(s,zeros(len(fobs)))
		d = append(d,zeros((len(fobs),1000),dtype=float),axis=0)
	else:
		t = zeros(len(fobs))
		s = zeros(len(fobs))
		d = zeros((len(fobs),1000),dtype=float)
	#FIXME boo. - memory HOGGGGG
	
	for ob_key in range(len(fobs)):
		ttext = "" # time text
		ob = fobs[ob_key]
		if borm not in ob:
			continue
		# ok, so the ob now has a borm, eorm, so get the text
		data = ob.split(eorm)[0].split(borm)[-1]
		# ok, now if there is a code, it will be split from the time by a bom25
		if bom25 in ob:
			code = ob.split(borm)[0].split(bom25)[-1].strip()
		else: 
			code = False
		if tsb:
			ttext = ob.split(borm)[0].split(bom25)[0].strip()
			# IF THIS IS A CT25 OR CL31 - THIS WILL ALSO HAVE THE CODE!
		else:
			ttext = fobs[ob_key+1].split(borm)[0].split(bom25)[0].strip()

		# now attempt to understand the time!
		try:
			# perhaps it is an epoch time
			tm = float(ttext.strip()) 
		except ValueError:
			try:
				#ok, maybe it is horel formatted
				# there may be quotes!
				if '"' in ttext:
					ttext = ttext[2:-2]

				tm = calendar.timegm(time.strptime(ttext.strip()+"UTC",'%m/%d/%Y %H:%M:%S%Z'))
				#FIXME - so, these times are in MST, but python is not playing nice with MST
				# FIXME - this may not be true anymore... 2 Feb 2012
				tm = tm + 7*3600
			except ValueError:
				try:
					# ok, vaisala formatted?
					tm = calendar.timegm(time.strptime(ttext.strip()+"UTC","-%Y-%m-%d %H:%M:%S%Z"))
				except ValueError:
					# And I give up.
					continue
	
		# with that settled, now we know obp[1] == the ob text
		# id the profile...
		data = {'time':tm,'code':code,'rest':data}

		if code and code[0:2] == "CT":
			# CT25
			info = vCT25.read(data)
		elif code and code[0:2] == "CL":
			#CL31
			info = vCL31.read(data)
		else:
			#FIXME - risky
			info = vCT12.read(data)

		# get an entire observation, so that this doesnt get redone
		if not info:
			# move along...
			continue
		# add this data to the netcdf
		# create the needed variables
		"""
		varT = out.create_variable('time',np.dtype(float),('time'))
		varH = out.create_variable('height',np.dtype(float),('height_key'))
		varC = out.create_variable('time',np.dtype(float),('code')) # code -- into a float... hmm 
		varD = out.create_variable('data',np.dtype(float),('vals'))
		"""
		#print time_index,d.shape
		t[time_index]=info['t']
		d[time_index]=info['v']
		s[time_index]=1.
		time_index += 1

		"""
		# FIXME - no sorting... though sorting was stupid anyway.
		text = str(tm)+','+str(info['h'])+','+info['c'] # add the time, RG, status info
		# now loop through the data and add to the line
		for d in info['v']:
			text += ','+str(d)
		text += "\n" # add the requisite newline!
		fileh.write(text)
		"""
	# now snip off all indeces greater than time_index!
	# nevermind - inefficient
	t = t[:time_index]
	d = d[:time_index]
	s = s[:time_index]
	

		#d[info['t']] = info
	del fl # does this garbage collect?

	# and save this absurd amount of data now stuffed into memory :(
	del fobs
	"""
	# now we have the obs... we need to go through them and order by time!
	print "sorting"
	## then we will sort the dict, and return
	dk = sorted(d.keys())

	## now return
	print "found",len(d),'profiles'
	return [d[k] for k in dk] # the keys were times, when sorted, will print properly!
	"""
	return (t,s,d)

