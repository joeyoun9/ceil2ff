"""
	Read CL31 backscatter data
"""
from numpy import int

def read(ob,**kwargs):
	"""
		Read a cl31 message 1 or two observation
	"""
	SCALING_FACTOR = 1.0e9
	#if not scaled: # no! it is always scaled!
	#	SCALING_FACTOR = 1
	# this is a data set, ob is a array of lines
	# FIXME cloud data does not currently get processed!!!
	tm = int(ob['time'])
	data = ob['rest'].split("\n") # split into lines

	#UPDATE 5/Jan/2012 - changed data line to -1 because of .strip on the output
	prof = data[-1].strip() # important to obliterate that little guy...

	code = ob['code']

	# then just grab the extra lines - since this compress tries to save everything
	cld = 'CL31'+ob['code'].strip()+data[1].strip()+data[2].strip()

	# determine height difference by reading the last digit of the code
	height_codes= [0,10,20,5,5] #'0' is not a valid key, and will not happen
	htMult = height_codes[int(code[-1])] # assumes that newlines and spaces have been strip()ed off
	hts = []
	values = []

	for i in xrange(0,len(prof),5):
		ven = prof[i:i+5]
		if ven[0:2] == "ff" or ven == '00000':
			# logic: ff corresponds to >=ff000, which is ~1e6, which is beyond super high
			values.append(1e-8)
		else:
			values.append(int(ven,16) / SCALING_FACTOR) # scaled to 100000sr/km (x1e9 sr/m)FYI

	out = {'t':tm,'h':htMult,'v':values,'c':cld}
	return out

