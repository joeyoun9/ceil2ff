"""
	Joe Young, December 2011

	__init__.py for obreader sub package. this will contain many of the necessary functions for reading obs!

"""

import os,calendar,time
from numpy import nan,array,log10,exp
import numpy as np

__all__ = ['vaisala']

from ceil2ff.obreader.vaisala import *
	
def ReadRaw(ob,full=False,check=False,scaled=True,max_ht=3500,extra=False,write=False):
	"""
		A mthod to transcribe raw obs, split by EOM character
		quickly into something desireable - getting out header and time info

		ob:    is the string for the observation, split by the term character!
		full:  should only the time/code be returned, or should an entire analysis be done?

		# -- when split by the term character, the endline/checksum may be included
			-- disregard it
	"""

	out = {} # a dict will be returned
	p = ob.split(unichr(2)) # this will always split the time stamp from the data stream
	if len(p) < 2: 
		return False # fail, but in way that can be caught nicely... this is no ob! (EOF Most likely)
	"""
		Now there are two pieces, the first of which contains the date and a line
	"""
	head = p[0].split("\n") # split by newline, there should be "\n\r"
	code = head[-1].strip() # the last two lines of this ob are the time/CTcode

	#FIXME - make the timestamp reading more dynamic!
	obtime = calendar.timegm(time.strptime(head[-2].strip()+"UTC","-%Y-%m-%d %H:%M:%S%Z"))

	out = {'time':obtime,'code':code,'rest':p[1]}
	###if not full: # no longer an option
	###	return out
	# well, now we are going to get the full profile, so go!
	return IDprofile(out) # compacting the operation into one!
	

def IDprofile(ob):
	"""
		IDprofile
		Given a formatted ob in a dict, this will use the characteristics
		of the individual observation type to determine what kind of ob
		it is, and subsequently, it will pass this to the correct reader.

		Inputs:
		ob:		the formatted observation dictionary from ReadRaw()
	"""
	if len(ob['code']) < 5:
		# this is a CT12 message!
		return vCT12.read(ob)

	elif len(ob['rest'].split("\n")[-2]) > 1500: # data line is [-2] for msg 1 & 2
		# then this is a CL31 message
		return vCL31.read(ob)

	else:
		return vCT25.read(ob)

	




#/////////// other utilities ///////////////////#
"""
	These will remain here for simplicity, and can be called via
	ceil2ff.obreader.det_hts() or otherwise.
"""

def f2m(ft):
	"""
		f2m
		Convert feet to meters

		Inputs:
		ft:		a distance in feet
	"""
	return .3048*ft

def det_hts(ht):
	"""
		A quck function to streamline the logic of 
		/////// == 0 in cloud height detection
	"""
	if "/" in ht:
		return 0
	return int(ht)

def chunk(l,i0,n):
	return [l[i:i+n] for i in range(i0,len(l), n)]


def flip2d(wrong):
	"""
		Return a row-column flipped 2-d array, mostly useful for plotting data, converts rows into columns.
	"""
	if type(wrong[0][0]) is list:
		raise "Oops, flip2d can only handle 2 dimensional arrays!"
		exit()
	from numpy import zeros
	#UPDATED 1 - 6- 2011: wrong[0] instead of wrong[1]. Thus, all (both) columns must be the same length as col 0!
	right = zeros((len(wrong[0]),len(wrong))) 
	# since Z is always full, but X can vary with the span parameter, it is best to use obCount
	i = 0
	for r in wrong:
		c = 0
		for v in r:
			right[c][i] = v
			c+=1
		i+=1
	return right	

