"""
	peek is a quick utility which enables a simple view of 60 minutes of data from 
	a file that has been created. It is intended to be quick, but we shall see

	REQUIRES MATPLOTLIB
"""

import matplotlib.pyplot as plt
import numpy as np
import cPickle
from scipy.io.netcdf import netcdf_file as nc

def peek(fn,vmin=1,vmax=2,length=False):
	"""
		show the data contents of the file created by the compressor
		you might have to edit the vmin/vmax to the dataset.
		
		Warning, this will load (efficiently) and show the whole friggin file, so
			could be a little rough on the memory.
	"""
	print "Peek V2.2"
	try:
		f  = nc(fn,'r')
		vi  = f.variables['b/s'] # thats the only variable I am peeking at...
		f.close()
	except:
		# maybe it wasnt a netCDF
		try:
			print "Reading"
			f = open(fn,'r')
			#count lines => o
			if not length:
				for o,l in enumerate(f): pass
			else:
				o = length
			vi = np.zeros((o+1,770)) #FIXME!! this needs to compensate for the expected sice of the data!
			l=0
			f.seek(0)
			for line in f:
				p = line.split(",",3) # make 4 elements!
				vi[l]=np.fromstring(p[-1],dtype=np.float32,sep=',')
				l+=1
				if l > o:
					#only read o number of obs
					break
			print "read"
			f.close()
		except:
			try:
				# it will take it a while to figure this out .... shouldn't have pickeled
				x = cPickle.load(f)
				vi  = x[0]
			except:
				# ok, this file was not made by me.
				print "I cannot read this file..."
				return False
	# and now plot
	print "Loaded it.. now trying to plot it."
	fig = plt.figure(figsize=(12,8))
	
	plt.imshow(vi[:].T,origin='lower',vmax=vmax,vmin=vmin,aspect='auto')
	plt.colorbar().set_label('Stored Backscatter Value')
	plt.title('Peek at '+fn)
	plt.show()

def ShowLow(fd='./ceil.dat'):

	from cleanfig import ttUTC,ttMST,fig_size
	f = open(fd)
	vals = []
	times = []
	heights = []
	#if not time:
	#	time = int(f.readline().split(',')[0])
	f.seek(0)
	t = 0
	for ob in f.readlines():
		# loop through each line in the file... inefficient, but necessary I think
		od = ob.split(',')
		t = int(od[0])
		#if t < time or t > time + 1800:
		#	continue
		#	# can't break, since the data may not be in order!
		#else:
		# save the profile to the list of values!
		vals.append(od[3:])
		times.append(t)
		heights = [x * int(od[1]) for x in range(len(od[3:]))] # not append!
	print "Plotting"
	# and now plot

	#fig = figure()
	fig = plt.figure()
	#ax = fig.gca()
	ax,ax2 = init_axis(1,1,1,twin=True)
	ttUTC(ax,'x',times[0],times[-1])
	ttMST(ax2,'x',times[0],times[-1])

	ax.set_xlabel("Time (UTC)")
	ax2.set_xlabel("Time (MST)")

	#ceil = plt.imshow(flip2d(vals),origin='lower',aspect=len(times)/len(heights))
	#ceil = plt.pcolormesh(array(times),array(heights),flip2d(vals),levels=[.01*x for x in range(400)])
	ceil= plt.contourf(times,heights,flip2d(vals),levels=[-.1+.01*x for x in range(50)])
	plt.colorbar(ceil).set_label('Attenuated Backscatter $m^{-1}sr^{-1}$')
	fig_size(fig,15,8)
	ax.set_ylabel("Range (m)")
	print "saving"
	#plt.savefig('7Jan_full.png')
	plt.show()
