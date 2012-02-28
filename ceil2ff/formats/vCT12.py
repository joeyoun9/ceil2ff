"""
	Read CT12K obs
"""
from numpy import exp,zeros,float32
def read(ob,**kwargs):
	"""
		process ct12 data
		-- this instrument formats it's data in feet, so, you must use feet
		-- however, cloud heights may not be in feet
		"""
	# check if the text you have been given is a proper ct12 message:

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
	del dls	

	# hold extra header information
	cld = 'CT12'+dl[1].strip()+dl[2].strip()
	text = "" # holds the strings
	
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

	values = zeros((1000),dtype=float32) # 1000 is the default return size! live with it.
	# the first values are heights of the beginning of the row...
	string = ob['rest'][len(dl[0]) + len(dl[1]) + 2:].replace(' ','0').replace("\n","").replace("\r","").strip() #faster?
	index = 0
	for i in xrange(2,len(string[2:])+1,2):
		if i%42 == 0: continue # height indices
		val = (int(string[i:i+2],16)-1)/50. # compute the SS value...
		values[index] = val
		index +=1 
	out = {'t':obtime,'h':15,'v':exp(values),'c':text,'l':250} # 15 m vertical resolution is the only reportable form!
	del values,il,cl,text,dl

	return out
