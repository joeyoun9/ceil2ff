"""
	Joe Young, December 2011

	__init__.py for ceil2ff package. This code is the front end, and will do all the logic,
	as derived from UUAdip.

	Saves each profile in a single line [flat file]

	TTTTTTTTTT,RG,SH,DDDDD.DDD,DDDDD.DDD,DDDDD.DDD,DDDDD.DDD,...

	T = unix timestamp
	RG = Range gate in meters, how far apart is each ob, starting at 0
	SH = starting height, elevation of the observation NOTE!!! == 0 ALWAYS!!
	D = backscatter coefficient value in m^-1 s^-1
"""

import os,calendar,time
from numpy import nan,array,log10,exp
import numpy as np

__all__ = ['obreader','peek','go','getObs']

import obreader

def go(directory='.',out='./ceil.dat'):
	"""
		Read in Ceilometer data from raw data files
		
	"""
	print "Attempting to read Vaisala Ceilometer Data"
	stime = time.time() # for efficiency monitoring purposes.
	# BEGIN - *recursively* open every file in the provided directories!
	# do not open the same file twice.
	f = open(out,'w')
	files = os.listdir(directory) # not currently recursive...
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
		for ob in obs:
			# heights, time, values, and the extra fun stuff (clouds, stats, whatnot)
			profs.append(ob['v'])  # this is the entire profile.
			times.append(ob['t'])  # this is the time of the ob
			hts.append(ob['h']) # this is just the distance between range gates
		"""
			And write the flatfile!!
		"""
		profs = log10(profs) # do not flip!! # not saving log10'd 
		# then loop through the data - AND ASSEMBLE THE DATA LINE!
		text = "" # the first character, blank thanks to the new format
		for i in range(len(profs)):
			# now each i is a key to an entire profile
			text += str(times[i])+','+str(hts[i])+',0' # add the time, RG, and SH
			# now loop through the data and add to the line
			for d in profs[i]:
				text += ','+str(d)
			text += "\n" # add the requisite newline!
		# then it is all ready!
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
	eom = unichr(3)
	fl = f.read() # put the whole thing into a string
	f.close()
	fobs = fl.split(eom) # break the string up by obs
	if len(fobs) < 2:
		# looks like there are no obs...
		return False

	# well, now read through the obs, and append them to the sortable dict
	for ob in fobs:
		info = obreader.ReadRaw(ob) 
		# get an entire observation, so that this doesnt get redone
		if not info:
			# dont append that guy!
			continue
		d[info['t']] = info 
	del fl # does this garbage collect?
	del fobs
	# now we have the obs... we need to go through them and order by time!
	
	## then we will sort the dict, and return
	dk = sorted(d.keys())

	## now return
	print "found",len(d),'profiles'
	return [d[k] for k in dk] # the keys were times, when sorted, will print properly!


