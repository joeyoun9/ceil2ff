"""
	Joe Young, December 2011
	Updated February 2012

"""

import os,calendar,time
from numpy import append,zeros,array,float32,int64
import numpy as np
from ceil2ff.formats import *


__all__ = ['formats','peek','tools']

save_index = 0
t = False
s = False
d = False
f = False
r = False
t0 = False
op = 0 # hold  the operation type

def compressFile(input_file,out='./ceil.dat',saveas='ascii',dtype=False):
	"""
	Compress only a specific file.
	
	Inputs:
		filename    = absolute reference to the file to be read
		out         = Filename where data are saved
		saveas      = 'netcdf' or 'ascii' how to save the data

	"""	
	files = [input_file]
	save(files,out,saveas,dtype)

def compressDir(directory='.',out='./ceil.dat',saveas='ascii',dtype=False):
	"""
		Read in Ceilometer data from raw data files
	Inputs:
		directory   = directory to read all files from 
		out         = Filename where data are saved
		saveas      = 'netcdf' or 'ascii' how to save the data

		
	"""
	print "Attempting to read Vaisala Ceilometer Data"
	if not directory[-1] == "/":
		directory += "/"
	stime = time.time() # for efficiency monitoring purposes.

	files = [directory + F for F in os.listdir(directory)] # not currently recursive...
	save(files,out,saveas,dtype)

def save(files,out_fname,saveas,dtype):

	global time_index,save_index,t,s,d,verbose,f,t0,op,r

	# determine the way we should save!
	# reset the global variables, as many of them may have been deleted.
	save_index = 0
	t = False
	s = False
	d = False
	f = False
	r = False
	t0 = False
	op = 0 # hold  the operation type

	if saveas == 'ascii':

		# then save a text file... 
		op = 0
		f = open(out_fname,'w') # open the file, and since it is global, it shall
		# be written to!
		print "Writing ASCII file"
	elif saveas == 'npz':
		op=3
	elif saveas == 'mat':
		op=4
	elif saveas == 'pickle':
		# pickling is a stupid option, I must assure you.
		import cPickle
		op = 2
		f = open(out_fname,'w')
		# pickle the numpy data structures...
		# will use the t,s,d,r variables to save...
		print "Generating a Pickle of this dataset"

		t=s=d=r=False

	else:
		op = 1
		from  scipy.io.netcdf import netcdf_file as nc
		# create the NetCDF
		f = nc(out_fname,'w')
		t0 = False
		# create the dimensions and variables
		f.createDimension('time',None) # can have unlimited time values
		#f.create_dimension('status',100)
		f.createDimension('dist',1000) # units of distance
		 
	
		# create the netCDF variables
		vD = f.createVariable('b/s','f',('time','dist')) #FIXME ->barely works :[
		vD.units = "Lidar Backscatter"
		vT = f.createVariable('time','i',('time',)) #FIXME ->doesn't work.
		vT.units = "Seconds since 1970-01-01 00:00"
		
		#this will hold the times (as a list of times!)

		f.createVariable('status','S1',('time',)) #FIXME -> doesn't work at all.

		vR = f.createVariable('range','i',('dist',))
		vR.units = "meters"
		# this is set once per save event... at the end
		
		t = s = d = r = False

		print "Saving NetCDF"

	save_index=0
	ht_key = False


	for fd in files:
		# check that the file is a file:
		if os.path.isdir(fd):
			continue # fail quietly
		fn = fd.split("/")[-1]
		if fn[0] == ".":
			continue # binary file, fail quietly

		print "reading",fn
		
		ret = getObs(fd) 
		# this saves the entire file's obs into the format needed...
		if not ret:
			continue

	print "Found",save_index,"profiles!"
	if op == 1:
		#f.variables['time'][:] = t # doing it internally, because, it doesnt work anyway.
		f.sync()

	if op == 2:
		# pickle
		pv = [d,t,s,r]
		print "Pickling"
		cPickle.dump(pv,f) 
		del pv
	if op == 3:
		print "Writing NPZ"
		np.savez(out_fname,backscatter=d,time=t,ranges=r) # FIXME status info is not written!!

	del d,t,s

	# then regardless of format, we must close f
	if f:
		f.close()
	return True




def getObs(fd):
	"""
		Grabs the obs from the given file by exploding it, and then passing the 
		sliced up obs to the parsers (raw_ob) which will then read out the information!
	"""
	global save_index,t,s,d,r,verbose,f,t0,op

	in_time = True # holder for restrictions
	# well, here is the file!
	fr = open(fd,'r')
	# now the file is open, read through it and save each identifyable profile

	# FIXME - if the file is too big, maybe read it in chunks?
	fl = fr.read() # put the whole thing into a string
	fr.close()
	
	if len(fl) == 0:
		# well, that file is a dud.
		return False


	# determine the control characters
	bom25 = unichr(1) # ct25/cl31 specific BOM key
	borm = unichr(2) # beginning of message (^B in VI)
	eorm = unichr(3) # ct25/ct12 EOM character / UNIVERSAL end of data string
	eom31 = unichr(4) # cl31 specific EOM key

	# determine what is the true eom character
	if eom31 in fl:
		# this is a CL31 message
		dtype='cl31'
		split  = eom31
		code_split = bom25
	elif bom25 in fl:
		# this is a CT25 message
		dtype='ct25'
		split = eorm
		code_split = bom25
	else:
		# presumably this is a CT12 message...
		dtype='ct12'
		split = eorm
		code_split = False

	# ok, then we can split this by the split, which is the message end.

	fobs = fl.split(split)
	del fl # get rid of that as quickly as you can!

	# determine which end the time stamp is on... could be difficult...
	tsb = True # boolean - true indicates time stamp before message

	if borm not in fobs[-1]:
		# then the time follows the message! 
		# the last element is a time, not a message
		# now I have to factor this information in
		tsb = False

	# this works semi-robustly for Vaisala ceilometers /// always room for improvement
	if dtype=='cl31':
		obL = 1000
	elif dtype=='ct25':
		obL = 1000 # FIXME - this is known
	elif dtype=='ct12':
		obL = 250
	if not type(t) == bool: #ie, before any time has been assigned, pre-assign and whatnot
		if op == 1:
			# if netCDF
			f.variables['time'][:] = append(f.variables['time'][:],zeros(len(fobs),dtype=int64))
			f.variables['status'][:] = append(f.variables['status'][:],zeros((len(fobs),100),\
				dtype='S1'),axis=0)
			f.variables['b/s'][:] = append(f.variables['data'][:],zeros((len(fobs),1000),\
				dtype=float32),axis=0)
		elif op > 1:
			# pickle,npz,mat
			d = append(d,zeros((len(fobs),obL),dtype=float32))
			t = append(t,zeros(len(fobs),dtype=int64))
	
		# if either
		s.append(range(len(fobs)))

	else:
		if op == 1:
			# if netCDF
			f.variables['time'][:] = zeros(len(fobs),dtype=int64)
			f.variables['b/s'][:] = zeros((len(fobs),1000),dtype=float32)
			f.variables['status'][:] = zeros(len(fobs),dtype='S1') # could be bad...
		elif op > 1:
			#if pickle, npz, or mat
			t = zeros(len(fobs),dtype=int64)
			d = zeros((len(fobs),obL),dtype=float32)
		# if either
		s = range(len(fobs)) # use a regular list for status strings...

	rn = False # control to know if I need to record height information
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
		else:
			ttext = fobs[ob_key+1].split(borm)[0].split(bom25)[0].strip()

		# now attempt to understand the time!
		try:
			# perhaps it is an epoch time
			tm = float(ttext.strip()) 
		except ValueError:
			try:
				#horel formatting -- check for quotes
				#if '"' in ttext: ttext = ttext[2:-2]
				tm = calendar.timegm(time.strptime(ttext.replace('"','').strip()+"UTC",'%m/%d/%Y %H:%M:%S%Z')) \
					+ 7*3600 # a correction for MST
			except ValueError:
				try:
					# ok, vaisala formatted?
					tm = calendar.timegm(time.strptime(ttext.strip()+"UTC","-%Y-%m-%d %H:%M:%S%Z"))
				except ValueError:
					# And I give up.
					continue
		if not t0:
			t0 = tm
	
		# with that settled, now we know obp[1] == the ob text
		# id the profile...
		data = {'time':tm,'code':code,'rest':data}

		if code and code[0:2] == "CT":
			# CT25
			out = vCT25.read(data)
		elif code and code[0:2] == "CL":
			#CL31
			out = vCL31.read(data)
		else:
			#FIXME - risky
			out = vCT12.read(data)

		# get an entire observation, so that this doesnt get redone
		if not out:
			# move along...
			continue

		# save data in the desired manner. do it silently

		# lots of logical overhead... but it doesn't seem to slow it down too much.

		if op == 1:
			f.variables['b/s'][save_index]=out['v']
			f.variables['time'][save_index]=tm
			f.variables['status'][save_index]=out['c']

		elif op > 1:
			t[save_index] = tm
			s[save_index] = out['c']
			d[save_index] = out['v'][:obL] # it will spit out 1000 values regardless...

		if not rn and not op == 0:
			rn = True
			if op == 1:
				f.variables['range'][:] = array([x*out['h'] for x in range(1000)],dtype=int)
			else:
				r = array([x*out['h'] for x in range(obL)],dtype=int)


		if op == 0:
			# finally, just append to the darn text file!
			dat_text = ""
			for v in out['v'][:out['l']]:
				dat_text += str(v)+"," # ugh, so long, 1000 values each... real drain
			f.write(str(tm)+","+str(out['h'])+","+out['c']+","+dat_text[:-1]+"\n")

		save_index += 1

	
	# catch up with the last set of indices if pickle/npz/mat...
	if op >= 2:
		t = t[:save_index]
		d = d[:save_index]
		s = s[:save_index]

	del fobs

	return True

