"""
	peek is a quick utility which enables a simple view of 60 minutes of data from 
	a file that has been created. It is intended to be quick, but we shall see

	REQUIRES MATPLOTLIB
"""

import matplotlib.pyplot as plt
from numpy import array
from tools import flip2d

def peek(fd,time=False):
	"""
		Show a quick look at the file!
		
		fd = file's absolute location (./ceil.dat is absolute)
		time = Unix timestamp to begin. If not provided, the time will be +/- 10 minutes from ob 0
	"""
	f = open(fd)
	vals = []
	times = []
	heights = []
	if not time:
		time = int(f.readline().split(',')[0])
	f.seek(0)
	for ob in f.readlines():
		# loop through each line in the file... inefficient, but necessary I think
		od = ob.split(',')
		t = int(od[0])
		if t < time or t > time + 3600:
			continue
			# can't break, since the data may not be in order!
		else:
			# save the profile to the list of values!
			vals.append(od[3:])
			times.append(t)
			heights = [x * int(od[1]) for x in range(len(od[3:]))] # not append!
	print "Plotting"
	# and now plot
	fig = plt.figure()
	ceil = plt.pcolormesh(array(times),array(heights),flip2d(vals))
	plt.colorbar(ceil).set_label('Attenuated Backscatter $m^{-1}sr^{-1}$')
	plt.show()

def ShowLow(fd='./ceil.dat'):

	from cleanfig import *
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
