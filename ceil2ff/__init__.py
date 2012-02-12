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
from numpy import nan,array,log10,exp
import numpy as np
import ob as obc 
import save as sv
from obs import IDprofile

__all__ = ['obs','peek']

import obs

def compressFile(input_file,out='./ceil.dat'):
	"""
	Compress only a specific file.
	
	Inputs:
		filename    = absolute reference to the file to be read
		out         = Filename where data are saved

	"""	
	files = [input_file]
	save(files,out)

def compressDir(directory='.',out='./ceil.dat'):
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

def save(files,out):
	f = open(out,'w')
	for fd in files:
		# check that the file is a file:
		if os.path.isdir(fd):
			continue # fail quietly
		fn = fd.split("/")[-1]
		if fn[0] == ".":
			continue # binary file, fail quietly

		print "reading",fn
		
		obs = getObs(fd) # this retuns the entire coded ob set, a list of ob objects
		if not obs or len(obs) == 0:
			print "No profiles found."
			continue #exit() # fail nicely
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
			
		"""
			And write the flatfile!!
		"""
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

	f.close()
	return True


def getObs(fd):
	"""
		Grabs the obs from the given file by exploding it, and then passing the 
		sliced up obs to the parsers (raw_ob) which will then read out the information!
	"""
	in_time = True # holder for restrictions
	d = {} # the sortable dict that is created
	# well, here is the file!
	f = open(fd,'r')
	# now the file is open, read through it and save each identifyable profile
	# split by control character unichr(3), then shave off the top of these elements
	eom = unichr(3) # end of Message (^C when viewed in VI)
	bom = unichr(2) # beginning of message (^B in VI)
	fl = f.read() # put the whole thing into a string
	f.close()
	"""
		This is an update - there are times where the eom character is not ideal for splitting
		How to detect this, I do not know! But, sometimes simply splitting is not good enough
	"""

	if len(fl) == 0:
		# well, that file is a dud.
		return False
	# ok, new plan - always split by the EOM character
	# then split by the BOM character 
	# -- check the first and last ones to see if there is a time on either end
	
	fobs = fl.split(eom) # now check the first and last
	# FIXME there is risk in this method, but it works better
	tsb = True # boolean - true indicates time stamp before message
	if bom not in fobs[-1]:
		# then the time follows the message! 
		# the last element is a time, not a message
		# now I have to factor this information in
		tsb = False
	"""

	elif fl[0] == '-':
		# generally a sign that this is a vaisala production
		fobs = fl.split(eom) # break the string up by obs
		reader_func = obs.ReadRaw1
	elif "\"" in fl:
		fobs = fl.split(bom) # split by beginning of message
		reader_func = obs.ReadRaw2 # and use reader #2!
	else:
		fobs = fl.split(eom)
		reader_func = obs.ReadRaw3

	if len(fobs) < 2:
		# looks like there are no obs...
		return False
	
	# well, now read through the obs, and append them to the sortable dict
	"""
	for ob_key in range(len(fobs)):
		ttext = "" # time text
		ob = fobs[ob_key]
		if bom not in ob:
			continue
		obp = ob.split(bom)
		if tsb:
			ttext = obp[0].strip()
		else:
			ttext = fobs[ob_key+1].split(bom)[0].strip()
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
				# FIXME - this may not be true anymore... 2 Feb 2012
				#FIXME - so, these times are in MST, but python is not playing nice with MST
				tm = tm + 7*3600
			except ValueError:
				try:
					# ok, vaisala formatted?
					tm = calendar.timegm(time.strptime(ttext.strip()+"UTC","-%Y-%m-%d %H:%M:%S%Z"))
				except ValueError:
					# And I give up.
					continue
	
		# with that settled, now we know obp[1] == the ob text
		# FIXME - this does not handle codes properly...ugh (ct25/cl31 problem)	
		info = IDprofile({'time':tm,'code':[0],'rest':obp[1]}) # gotta get away from codes!!!
		#######info = reader_func(ob.strip()) 
		# get an entire observation, so that this doesnt get redone
		if not info:
			# dont append that guy!
			continue
		d[info['t']] = info 
	del fl # does this garbage collect?
	del fobs
	# now we have the obs... we need to go through them and order by time!
	print "sorting"
	## then we will sort the dict, and return
	dk = sorted(d.keys())

	## now return
	print "found",len(d),'profiles'
	return [d[k] for k in dk] # the keys were times, when sorted, will print properly!


