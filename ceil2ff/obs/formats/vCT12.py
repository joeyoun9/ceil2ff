"""
	Read CT12K obs
"""
from numpy import exp,zeros,float16
from ceil2ff.obs import *
from StringIO import StringIO as strio
def read(ob,**kwargs):
	"""
		process ct12 data
		-- this instrument formats it's data in feet, so, you must use feet
		-- however, cloud heights may not be in feet
		"""
	# check if the text you have been given is a proper ct12 message:
	#FIXME - this may not be apropriate!!!
	###if ob['rest'][0] == '3': # then sky is fully obsured, so skip - fog/warmup/major error
	###	# then the system is warming up, and we should skip
	###	return False

	obtime = int(ob['time'])
	dls = ob['rest'].split("\n")
	dl = []
	if len(dls) < 15 or ":" in ob['rest']:
		return False

	# purify the ob so that i dont have to care about formatting
	for l in dls:
		if len(l.strip()) > 3:
			# then i guess there is content
			dl.append(l) #NOT STRIP!!
	# ok, let's hope that is good
		

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
	# get extra information!!!
	text = "" # holds the strings
	#tl = dls[0].strip()
	
	cl = dl[0].strip()
	data = [
	cl[0:1],
	cl[4:9],
	cl[10:15],
	cl[16:21],
	cl[22:27]
	] + [x for x in cl[28:39]]
	il = dl[1].strip()
	data += [
	il[0:1],
	il[2:3],
	il[4:8],
	il[9:12],
	il[13:16],
	il[17:20],
	il[21:25],
	il[26:31],
	il[32:34],
	il[35:37],
	]
	for d in data:
		text += d+"|" # use pipes to seperate these values, to be simpler.
	# ok, now text holds the necessary values!

	#print "CT12K Data ...",ob[4].strip(),obtime,'sdfds'
	values = zeros((1000)) # 1000 is the default return size! live with it.
	# data are lines (keys) 4 - 16 # 2 digit hex, (rounded) FF = overflow
	# the first values are heights of the beginning of the row...
	string = ob['rest'][len(dl[0]) + len(dl[1]) + 2:].replace(' ','0').replace("\n","").replace("\r","").strip() #faster?
	index = 0
	for i in xrange(2,len(string[2:])+1,2):
		if i%42 == 0: continue # height indices
		val = (int(string[i:i+2],16)-1)/50. # compute the SS value...
		values[index] = val
		index +=1 
	out = {'t':obtime,'h':15,'v':exp(values),'c':text} # 15 m vertical resolution is the only reportable form!
	del values
	return out


	"""
	# the last 2 is for the \n characters nixed in the stripping process
	#values = fromstring(string,dtype='S1',count=262,delim=2)
	values = loadtxt(strio(string),dtype=int16)
	print ob['rest'],values,"\n",string
	exit()
	"""
	for l in dl[2:15]:
		l = l.rstrip()
		#print l
		h0 = int(l[0:2])*1000 # FEET!
		_ = -1 # this is the multiplier for each ob per line
		# each ob is 50 feet higher than h0 
		#print l[2:2+2]," L:",l
		badline = False # new line, hopefully, things have improved
		for i in xrange(2,len(l[2:])+1, 2):

			#FIXME - need a better way to check for this silly error
			# sadly, there is a small glitch in the way these messages are saved
			"""
			if l[i:i+2] == '  ' or badline:
				badline = True # then the rest of this line is bad
				values.append(nan)
				continue
			"""
			# compute the backscattered value!
			# format : raw - minV = exp((DD/50) - 1) So, it will be normalized...
			val = (int(l[i:i+2],16) - 1)/50.
			#print l[i:i+2],val
			values.append(val)
	#print len(values) # should be 250
	out = {'t':obtime,'h':15,'v':exp(array(values)),'c':text} # 15 m vertical resolution is the only reportable form!
	del values
	return out



