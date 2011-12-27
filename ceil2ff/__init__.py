"""
	__init__.py for ceil2ff package. This code is the front end, and will do all the logic,
	as derived from UUAdip.

	Saves each profile in a single line [flat file]

	TTTTTTTTTT,RG,SH,DDDDD.DDD,DDDDD.DDD,DDDDD.DDD,DDDDD.DDD,...

	T = unix timestamp
	RG = Range gate in meters, how far apart is each ob, starting at 0
	SH = starting height, elevation of the observation
	D = backscatter coefficient value in m^-1 s^-1
"""

import os,calendar,time,re
from numpy import log10,mean,nan,divide,array,fromstring,int16,int
import numpy as np

def go(directory,out):
	"""
		Read in Ceilometer data from raw data files
		
	"""
	print "Attempting to read Vaisala Ceilometer Data"
	stime = time.time() # for efficiency monitoring purposes.
	# BEGIN - *recursively* open every file in the provided directories!
	# do not open the same file twice.
	files = os.listdir(directory) # not currently recursive...
	text = "" # the first character, blank thanks to the new format
	for f in files:
		# check that the file is a file:
		if os.path.isdir(f):
			continue # fail quietly
		fn = fd.split("/")[-1]
		if fn[0] == ".":
			continue # binary file, fail quietly

		print "reading",fn
		
		obs = getObs(f) # this retuns the entire coded ob set, a list of ob objects
		if len(obs) ==0:
			print "Uhoh, no profiles found..."
			continue #exit() # fail nicely
		profs = []
		times = []
		for ob in obs:
			# heights, time, values, and the extra fun stuff (clouds, stats, whatnot)
			profs.append(ob['v'])
			times.append(ob['t'])
		# well, just use the last value
		hts = ob['h'] #WARNING!!! - this could be a poor assumption!!

		"""
			And write the flatfile!!
		"""
		# first insert a line representing heights:
		for x in hts:
			text += ','+str(x)
		text += "\n"
		nprofs = log10(nprofs) # do not flip!!
		# then loop through the data
		for i in range(len(nprofs)):
			# now each i is a key to an entire profile
			text += str(ntimes[i])
			# now loop through the data and add to the line
			for d in nprofs[i]:
				text += ','+str(d)
			text += "\n" # add the requisite newline!
	# then it is all ready!
	f = open(kwargs['writeout'],'w')
	f.write(text)
	f.close()
	return True

""" ///////////////// INTERNAL METHODS /////////////////"""


def getObs(f):
	"""
	"""
	print "Getting Observations"
	in_time = True # holder for restrictions
	d = {} # the sortable dict that is created
	if restrict:
		check = cls
	else:
		check = False
	for fd in cls.find_files('','.DAT',allow_repeats=False):
		# well, here is the file!
			continue # this is a binary file, like a swp or whatnot
		f = open(fd,'r')
		# now the file is open, read through it and save each identifyable profile

		# if restrict, then pluck out the first ob - and check if it is in range!
		if restrict:
			fl = f.read(500) # the first time stamp should be in the first 500 bytes
			tm = raw_ob(fl,full=False) # this should work with the first ob...
			if not tm:
				continue
			# now get the time of the last ob - neglibly inefficient
			f.seek(-5000,2) # set the pointer to 1000 bytes from the end
			fl = f.read().split(unichr(3))[-2] # this should read the last ob bytes
			tm2 = raw_ob(fl)['time']
			tm1 = tm['time']
			if tm1 > cls.data.end or tm2 < cls.data.begin:
				continue
		f.seek(0,0)#reset the pointer!	
		# Well, we are reding this one!
		cls.log('Reading',fn)
		# split by control character unichr(3), then shave off the top of these elements
		eom = unichr(3)
		fl = f.read() # put the whole thing into a string
		f.close()
		fobs = fl.split(eom) # break the string up by obs
		if len(fobs) < 2:
			# looks like there are no obs...
			continue

		# well, now read through the obs, and append them to the sortable dict
		for ob in fobs:
			info = raw_ob(ob,check=check,full=True,scaled=scaled,max_ht=max_ht,extra=extra,write=write) 
			# get an entire observation, so that this doesnt get redone
			if not info:
				# dont append that guy!
				continue
			d[info['t']] = info 
		del fl # does this garbage collect?
		del fobs
	# now we have the obs... we need to go through them and order by time!
	print "Sorting Observations"
	# then we will sort the dict, and return
	dk = sorted(d.keys())

	# now return
	print "found",len(d),'profiles'
	return [d[k] for k in dk] # the keys were times, when sorted, will print properly!
	
def raw_ob(ob,full=False,check=False,scaled=True,max_ht=3500,extra=False,write=False):
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
	obtime = calendar.timegm(time.strptime(head[-2].strip()+"UTC","-%Y-%m-%d %H:%M:%S%Z"))
	if check:
		# then check should be the request object
		if obtime < check.data.begin or obtime > check.data.end:
			# a harsh and absolute evaluation
			return False
	out = {'time':obtime,'code':code,'rest':p[1]}
	if not full:
		return out
	# well, now we are going to get the full profile, so go!
	return makeProf(out,scaled,max_ht,extra,write) # compacting the operation into one!
	
		


def makeProf(ob,scaled,max_ht,extra,write):
	"""
		This will take the observation, and make a profile, by determining the type
		And then reading into the
	"""
	#lines = ob.split("\n") # split up by newlines, hopeully this gets it
	#print ob
	if len(ob['code']) < 5:
		# this is a CT12 message!
		return read_ct12(ob,extra=extra,scaled=scaled,max_ht=max_ht,write=write)
	elif len(ob['rest'].split("\n")[-2]) > 1500: # data line is [-2] for msg 1 & 2
		# then this is a CL31 message
		return read_cl31(ob,extra=extra,scaled=scaled,max_ht=max_ht,write=write)
	else:
		return read_ct25(ob,extra=extra,scaled=scaled,max_ht=max_ht,write=write)


def bin_profs(cls,profs,times,hts,span):
	"""
		Create and fill bins, and then average them
		ASSUMING MONotonically increasing time values!
	"""
	# calculate the bins, with time in the center of the bin
	bins = [] # for now this will be the END Times of the bins
	t = cls.data.begin
	while t < cls.data.end: # if t == the end, we should not make another!
		t += span*60 # SPAN IN MINUTES
		bins.append(t)
	# if time is not at the end, then make a final bin
	if not t == cls.data.end:
		bins.append(cls.data.end) # final bin
	binct = len(bins)
	# fill the bins!
	print "Creating ",binct,"bins"
	binned = [[] for _ in bins] # so that it is the same size!
	key = 0
	for k in range(len(profs)):
		ob = profs[k]
		tm = times[k]
		# ob is the observation (profile)
		# quickly determine which bin key we are at!
		while tm > bins[key]: # if the time is == to the bin, then it remains in this bin
			# time should never be greater than the last bin...
			# then it is time for a new bin!
			key += 1
		binned[key].append(ob)
	# now create new profiles by averaging each bin by height #FIXME assuming the heights for the bins are the same!
	outp = []# ['' for _ in binned] # initialize the out file
	for bn in binned:
		#bn = binned[b]
		# this should be a list of profile values
		# compute an average for each height in this
		lth = len(bn) # how many profiles are in this bin
		if lth == 0:
			outp.append([nan for _ in hts]) # assign a nan list if it was an empty bin
			continue
		bno = []#[0. for _ in bn[0]] # set the out variable
		if lth > 1: # if there is only one ob, then no averaging can be done
			bn = cls.flip2d(bn) # make it so we can loop through by height instead of by ob
			for l in bn:
				bno.append(mean(l))
		else:
			bno = bn[0]
		outp.append(bno)
	outt = [_ - span*30 for _ in bins] # times are in the middle of the span
	cls.log("Binning Stats:",len(outt),len(outp),len(outp[1]))
	return outp,outt


""" /////////////// Ob datatype readers //////////////// """
"""
	These functions will take an individual ob, and return 3 datum:
	# a list of values along the vertical profile
	# a list of the applicable heights of these profiles
	# the text of the other information, preferably formatted, but #FIXME not yet

"""
def read_ct12(ob,extra=False,scaled=True,max_ht=3500,write=False,**kwargs):
	"""
		process ct12 data
		-- this instrument formats it's data in feet, so, you must use feet
		-- however, cloud heights may not be in feet
	
		extra: should clouds be read and reported
		max_ht: maximum height to report from
	"""
	SCALING_FACTOR = 1.0e7
	if not scaled:
		SCALING_FACTOR = 1
	obtime = int(ob['time'])
	cld = []
	dl = ob['rest'].split("\n")
	if extra == 'compress':
		# then just grab the extra lines - since this compress tries to save everything
		cld = 'CT12'+dl[1].strip()+dl[2].strip()
	elif extra:
		# well, now we have to read the first status line (line 2)
		data = dl[0].strip()
		# first check if this is feet or meters:
		# if data[-3] == 1 then this is in meters
		FM = data[-3]
		N = data[0] # n is how many decks observed,
		H1 = data[5:9]
		T1 = data[11:15]
		H2 = data[17:21]
		T2 = data[19:23]
		if N < 3:
			cld = [det_hts(H1),det_hts(H2)] # T values are something odd, backscatter range
		elif N == 3:
			cld = [-999] # this is a precip trigger! 
		
	#print "CT12K Data ...",ob[4].strip(),obtime,'sdfds'
	hts = []
	values = []
	# data are lines (keys) 4 - 16 # 2 digit hex, (rounded) FF = overflow
	# the first values are heights of the beginning of the row...
	for l in dl[3:15]:
		l = l.rstrip()
		h0 = int(l[0:2])*1000 # FEET!
		_ = -1 # this is the multiplier for each ob per line
		# each ob is 50 feet higher than h0 
		#print l[2:2+2]," L:",l
		badline = False # new line, hopefully, things have improved
		for i in xrange(2,len(l[2:]), 2):
			_+= 1
			hght = f2m(h0+_*50)
			if 'max_ht' in kwargs.keys():
				if hght > kwargs['max_ht']:
					break
			# sadly, there is a small glitch in the way these messages are saved
			if l[i:i+2] == '  ' or badline:
				badline = True # then the rest of this line is bad
				values.append(nan)
				hts.append(hght)
				continue
			# append values and heights! Woohoo!
			values.append(pow(int(l[i:i+2],16),2)/SCALING_FACTOR) #lets try the value squared...
			hts.append(hght)
	#print values
	out = {'t':obtime,'h':hts,'v':values,'c':cld}
	if write:
		# then write the data, and do not return
		# the line should be formatted tm|hts,|vals,|cld\n
		strh = ""
		strv = ""
		for i in range(len(hts)):
			strh += str(hts[i])+","
			strv += str(values[i])+","
		write.write(str(obtime)+'|'+strh+"|"+strv+"|"+cld+'\n')
		return False # This will trigger no response, even though the job was done
	return out


def read_cl31(ob,scaled=True,max_ht=3500,extra=False,write=False,top=3500,**kwargs):
	"""
		Read a cl31 message 1 or two observation
	"""
	SCALING_FACTOR = 1.0e9
	if not scaled:
		SCALING_FACTOR = 1
	# this is a data set, ob is a array of lines
	# FIXME cloud data does not currently get processed!!!
	tm = int(ob['time'])
	data = ob['rest'].split("\n") # split into lines
	prof = data[-2].strip() # important to obliterate that little guy...
	code = ob['code']
	cld = [] # and thustly it will remain for now
	if extra == 'compress':
		# then just grab the extra lines - since this compress tries to save everything
		cld = 'CL31'+ob['code'].strip()+data[1].strip()+data[2].strip()
	# ... data lines ... #
	# determine height difference by reading the last digit of the code
	height_codes= [0,10,20,5,5] #'0' is not a valid key, and will not happen
	htMult = height_codes[int(code[-1])] # assumes that newlines and spaces have been strip()ed off
	hts = []
	values = []
	# the data line is simply the last line [-1]
	#values = np.int(chunk(prof,0,5),16)/ array([SCALING_FACTOR for x in range(len(prof))])
	#print values
	# split with regexp? #BOO BAD!
	#val = re.split('[00,ff]',prof)
	#print val
	for i in xrange(0,len(prof),5):
		values.append(np.int(prof[i:i+5],16) / SCALING_FACTOR) # scaled to 100000sr/km (x1e9 sr/m)FYI
	hts = [x * htMult for x in range(len(values))] #FIXME compensate for tilt!
	# sadly, there is more that must be done... any value above 1e7 must be removed
	values = [chkl31(x,ovr=not scaled) for x in values] # apply the filter for nan's
	out = {'t':tm,'h':hts,'v':values,'c':cld}
	if write:
		# then write the data, and do not return
		# the line should be formatted tm|hts,|vals,|cld\n
		strh = ""
		strv = ""
		for i in range(len(hts)):
			strh += str(hts[i])+","
			strv += str(values[i])+","
		write.write(str(tm)+'|'+strh+"|"+strv+"|"+cld+'\n')
		return False # This will trigger no response, even though the job was done
	return out
	#print data
def chkl31(v,ret=1e-8,ovr=False):
	"""
		Quickly check cl31 backscatter for high-failure, set to 1
		over = override
	"""
	if ovr:
		return v
	if v > 1e-3:
		return ret
	return v

def read_ct25(ob,scaled=True,max_ht=3500,extra=False,write=False,**kwargs):
	"""
		Read CT25 Observations
	"""
	SCALING_FACTOR = 1.0e7
	if not scaled:
		SCALING_FACTOR = 1
	#FIXME - also not grabbing clouds at this time...
	cld = []
	data = ob['rest'].split("\n")
	if extra == 'compress':
		# then just grab the extra lines - since this compress tries to save everything
		cld = 'CT25'+ob['code'].strip()+data[1].strip()+data[2].strip()
		if ob['code'].strip()[-2] == '7':
			cld += data[19]
	# the code line does not indicate anything, except message number [-2]
	# that changes what the very lasst line is, nothing more (7 has a last line [s/c])
	prof = data[3:18]
	hts = []
	values = []
	for l in prof:
		# the line is HHHD0D1D2D3D4...
		l=l.strip()
		h0 = int(l[0:3])*30. # in meters
		_ = -30 # the counter to keep track of heights
		"""
		#vals = fromstring(l[3:],dtype=int,count=len(l[3:])/4) #chunk(l,3,4)
		# try adding hex encoding 'x' to the line, every 4
		_1 = 0
		ln = ""
		for c in l[3:]:
			if _1 == 4:
				_1 = 0
				ln += ','# insert delimiters
			ln += c
			_1 +=1
		vals=fromstring(ln,dtype=int,sep=',')#count = len(ln)/4)
		print ln,vals
		#vals = np.int(vals)#.dtype=int
		#print "vals",vals
		for x in vals/array([SCALING_FACTOR for _ in vals]):
			values.append(x)
		# add the heights!
		hts += [h0+30*i for i in range(len(vals))]
		"""
		for i in xrange(3,len(l),4):
			_ += 30
			hght = h0+_
			if 'max_ht' in kwargs.keys():
				if hght > kwargs['max_ht']:
					break
			values.append(chkl31(int(l[i:i+4],16)/SCALING_FACTOR,ovr=not scaled))
			hts.append(hght)
		""""""
	out = {'t':ob['time'],'h':hts,'v':values,'c':cld}
	if write:
		# then write the data, and do not return
		# the line should be formatted tm|hts,|vals,|cld\n
		strh = ""
		strv = ""
		for i in range(len(hts)):
			strh += str(hts[i])+","
			strv += str(values[i])+","
		write.write(str(ob['time'])+'|'+strh+"|"+strv+"|"+cld+'\n')
		return False # This will trigger no response, even though the job was done
	return out
	




#/////////// other utilities ///////////////////#
def f2m(ft):
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

