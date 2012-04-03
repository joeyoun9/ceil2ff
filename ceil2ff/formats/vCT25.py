"""
	Read CT25 Ceilometer backscatter obs
"""
from numpy import zeros,float32
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
		cld = ob['code'].strip()+data[1].strip()+data[2].strip()
		if ob['code'].strip()[-2] == '7':
			cld += data[19]
	text = ""
	for i in cld:
		text += str(i)+"|"
	# the code line does not indicate anything, except message number [-2]
	# that changes what the very lasst line is, nothing more (7 has a last line [s/c])
	prof = data[3:18]#.strip().replace("\n",'').replace("\r","")
	index = 0
	values = zeros(250,dtype=float32)
	for l in prof:
		# the line is HHHD0D1D2D3D4...
		l=l.strip()
		#FIXME - check for high values!!
		for i in xrange(3,len(l),4):
			val = l[i:i+4]
			if val[0] == 'F' or val == '0000':
				values[index]= 1
			else:
				values[index] = int(val,16)
			index +=1
		""""""
	values = values#/SCALING_FACTOR # remove the scaling factor...
	out = {'t':ob['time'],'h':30,'v':values,'c':text,'l':250} # yes, 30 m resolution! how terrible!
	return out

