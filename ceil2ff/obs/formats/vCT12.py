"""
	Read CT12K obs
"""
from numpy import exp
from ceil2ff.obs import *
#FIXME - ARRRGGG

def read(ob,**kwargs):
	"""
		process ct12 data
		-- this instrument formats it's data in feet, so, you must use feet
		-- however, cloud heights may not be in feet
		"""
	# check if the text you have been given is a proper ct12 message:
	if ob['rest'][0] == '3': # then sky is fully obsured, so skip - fog/warmup/major error
		# then the system is warming up, and we should skip
		return False
	SCALING_FACTOR = 1.0e7
	obtime = int(ob['time'])
	dl = ob['rest'].split("\n")
	if len(dl) > 15 or ":" in ob['rest']:
		return False
	# hold extra header information
	cld = 'CT12'+dl[1].strip()+dl[2].strip()
	"""
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
	"""

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

			# sadly, there is a small glitch in the way these messages are saved
			if l[i:i+2] == '  ' or badline:
				badline = True # then the rest of this line is bad
				values.append(nan)
				hts.append(hght)
				continue
			# compute the backscattered value!
			# format : raw - minV = exp((DD/50) - 1) So, it will be normalized...
			val = (int(l[i:i+2],16) - 1)/50.
			values.append(val) #lets try the value squared...
	out = {'t':obtime,'h':15,'v':exp(values),'c':cld} # 15 m vertical resolution is the only reportable form!
	return out



