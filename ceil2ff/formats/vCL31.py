"""
	Read CL31 backscatter data
"""
from numpy import int,zeros,float32

def read(ob,**kwargs):
	"""
		Read a cl31 message 1 or two observation
	"""
	SCALING_FACTOR = 1.0e9
	#if not scaled: # no! it is always scaled!
	#	SCALING_FACTOR = 1
	# this is a data set, ob is a array of lines
	tm = int(ob['time'])
	data = ob['rest'].split("\n") # split into lines

	#UPDATE 5/Jan/2012 - changed data line to -1 because of .strip on the output
	prof = data[-2].strip() # important to obliterate that little guy...

	code = ob['code']
	# this is the first little bit of info at the top, very informative

	# then just grab the extra lines - since this compress tries to save everything
	# FIXME cloud data does not currently get processed!!!
	cld = 'CL31'+ob['code'].strip()+data[1].strip()+data[2].strip() +"|"

	# determine height difference by reading the last digit of the code
	height_codes = [0,10,20,5,5] #'0' is not a valid key, and will not happen
	data_lengths = [0,770,385,1500,770]
	# length betwwn 770 and 1500
	datLen = data_lengths[int(code[-1])] # figure out the expcted message length
	htMult = height_codes[int(code[-1])] # assumes that newlines and spaces have been strip()ed off
	values = zeros(datLen,dtype=float32)
	ky = 0
	for i in xrange(0,len(prof),5):
		
		ven = prof[i:i+5]
		if ven[0:2] == "ff" or ven == '00000':
			# logic: ff corresponds to >=ff000, which is ~1e6, which is beyond super high
			values[ky] = 1/SCALING_FACTOR
		else:
			values[ky] = int(ven,16) / SCALING_FACTOR # scaled to 100000sr/km (x1e9 sr/m)FYI
		ky += 1 # keep the key up to date
	out = {'t':tm,'h':htMult,'v':values,'c':cld,'l':datLen}
	return out

