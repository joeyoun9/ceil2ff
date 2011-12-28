"""
	A standard module of useful tools for conversions and array manipulation.
	Some are not used, and will be discarded soon.
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

