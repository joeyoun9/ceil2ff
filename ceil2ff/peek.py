"""
	peek is a quick utility which enables a simple view of 30 minutes of data from 
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
		if t < time or t > time + 1800:
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
	ax = fig.gca()
	ceil = plt.pcolormesh(array(times),array(heights),flip2d(vals))
	plt.colorbar(ceil).set_label('Attenuated Backscatter $m^{-1}sr^{-1}$')
	plt.show()

