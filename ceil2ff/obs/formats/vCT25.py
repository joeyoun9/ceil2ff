"""
	Read CT25 Ceilometer backscatter obs
"""

def read(ob,scaled=True,max_ht=3500,extra=False,write=False,**kwargs):
	"""
		Read CT25 Observations
	"""
	SCALING_FACTOR = 1.0e7
	if not scaled:
		SCALING_FACTOR = 1
	#FIXME - also not grabbing clouds at this time...
	cld = []
	data = ob['rest'].split("\n")
	if extra == 'compress':
		# then just grab the extra lines - since this compress tries to save everything
		cld = 'CT25'+ob['code'].strip()+data[1].strip()+data[2].strip()
		if ob['code'].strip()[-2] == '7':
			cld += data[19]
	# the code line does not indicate anything, except message number [-2]
	# that changes what the very lasst line is, nothing more (7 has a last line [s/c])
	prof = data[3:18]
	hts = []
	values = []
	for l in prof:
		# the line is HHHD0D1D2D3D4...
		l=l.strip()
		#FIXME - check for high values!!
		for i in xrange(3,len(l),4):
			val = l[i:i+4]
			if val[0] == 'F':
				values.append(1e-7)
			else:
				values.append(int(val,16)/SCALING_FACTOR)
		""""""
	out = {'t':ob['time'],'h':30,'v':values,'c':cld} # yes, 30 m resolution! how terrible!
	if write:
		# then write the data, and do not return
		# the line should be formatted tm|hts,|vals,|cld\n
		strh = ""
		strv = ""
		for i in range(len(hts)):
			strh += str(hts[i])+","
			strv += str(values[i])+","
		write.write(str(ob['time'])+'|'+strh+"|"+strv+"|"+cld+'\n')
		return False # This will trigger no response, even though the job was done
	return out

