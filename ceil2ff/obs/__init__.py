"""
	Joe Young, December 2011

	__init__.py for obreader sub package. this will contain many of the necessary functions for reading obs!

"""

import os,calendar,time
from numpy import nan,array,log10,exp
import numpy as np

__all__ = ['formats']

from ceil2ff.obs.formats import *

	
def ReadRaw1(ob,full=False,check=False,scaled=True,max_ht=3500,extra=False,write=False):
	"""
	/// THIS IS FORMAT #1 SO IT IS DEISGNED FOR FILES CREATED BY VAISALA SOFTWARE!
		A mthod to transcribe raw obs, split by EOM character
		quickly into something desireable - getting out header and time info

		ob:    is the string for the observation, split by the term character!
		full:  should only the time/code be returned, or should an entire analysis be done?

		# -- when split by the term character, the endline/checksum may be included
			-- disregard it

		-> So, this function will attempt to isolate individual profiles in a more dynamic fashion
		
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
			
	
	# we need to return 'rest' as a stripped input...
	out = {'time':obtime,'code':code,'rest':p[1].strip()}
 
	# well, now we are going to get the full profile, so go!
	return IDprofile(out) # compacting the operation into one!
	
def ReadRaw2(ob):
	"""
	ReadRaw2 is a function which will read raw files in format #2, this is going to be hard coded
	to a more specific format... however, it is included anyway.
	
	Inputs:
		ob	=	chunk of text representing a received ob, which will be analyzed

	IDprofile will be hopefully still used
	"""
	out = {}
	ob = ob.strip() # clear unknown whitespace (including control characters)
	p = ob.split("\n") # split by lines instead of control characters, since they are now unreliable
	# now we need to check the length of the ob,
	if len(p) < 16: 
		return False
	date_str = p[15].strip() # line 15 should be the date... let us see!

	### DATE STRING ISSUE, sometimes there are quotes!! damnation!
	if '"' in date_str:
		date_str = date_str[2:-2]
		#print 'corrected:'+date_str # hopefully this correction is accurate for the new files!
	try:
		# well, John saves these bad boys in MST, so there you go.
		obtime = calendar.timegm(time.strptime(date_str.strip()+"UTC",'%m/%d/%Y %H:%M:%S%Z'))
	except (ValueError):
		return False
	#FIXME - so, these times are in MST, but python is not playing nice with MST
	obtime = obtime + 7*3600
	# now, #FIXME - assuming no code currently (CT12)
	# FIXME reassembling the data message should be done simply by just giving the whole darn ob
	rest = ""
	for l in p[:-1]:
		rest += l+"\n"
	out = {'time':obtime,'code':[0],'rest':rest.strip()} # that should figure it out
	return IDprofile(out)
	
	
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

	# corrected 5 Jan 2012 for .strip() on ob string, changed data line from [-2] to [-1]
	elif len(ob['rest'].split("\n")[-1]) > 1500: # data line is [-2] for msg 1 & 2
		# then this is a CL31 message
		return vCL31.read(ob)

	else:
		return vCT25.read(ob)
