"""
	The telnet package provides simple resources to connect via telnet to a ceilometer
	at a specified IP address, and listen to it for data packets, and appends to a file
	the transcribed data message, using resources of this package.


	Connection will intend to be persistent, but in case of failure, it includes the ability
	to be regularly called by a crontab, and will turn back on should it not be currently running

	-- also checks processes, however, since multipple telnet sessions are not permitted, it is 
	unlikely for this to truly be an issue. Failed connections will close down the program.

	It will terminate with the value 'kill' entered in the control file, located in the directory
	where data is being saved.

	THIS WILL NOT MAKE FIGURES

	RAW DATA IS ALSO SAVED IN A DIFFERENT FILE

"""

import telnet
import signal

import sys,time

import ceil2ff.obs.IDprofile as idp


def listen(directory,ip):
	"""
		Open a persistent telnet connection listening for EOM/BOM messages.
		CURRENTLY tuned for Vaisala CT12K ceilometers.
	"""
	HOST = ip
	if directopry[-1] == "/":
		directory = directory[:-1]

	# LOGIN DECISIONS WILL BE MADE AT A LATER TIME

	user = raw_input("Enter your remote account: ")
	password = getpass.getpass()

	tn = telnetlib.Telnet(HOST)

	tn.read_until("login: ")
	tn.write(user + "\n")
	if password:
	    tn.read_until("Password: ")
	    tn.write(password + "\n")

	# so begins the ideally infinite loop
	go = True
	current = tn.read_all()
	print current
	EOM  = unichr(3)
	BOM = unichr(2)
	while go:
		# read until the end of the message
		ob = tn.read_until(EOM)
		# add a timestamp, and pass the file to the raw data file
		
		print ob # this is for giggles right now, hopefully it is good
		ts = time.time() # I am saving in EPOCH!!! VICTORY!
		raw = open(directory+"/raw_data.dat",'a')
		raw.write("\n"+str(ts)+ob)
		raw.close()
		trans_ob = idp({'time':ts,'code':[0],'rest':ob.strip()})
		dat = open(directory+"/ceil.dat",'a')
		vl  =  "" # text holer for the values
		for v in trans_ob['v']:
			# copy the values to a comma seperated list
			vl += ","+str(v)
		dat.write("\n"+str(ts)+","+str(trans_ob['h'])+vl)
		dat.close()
	
		# now, we should check the controls... but meh...
		#meh indeed. Just kill it if it needs to die...	hopefully
		command = signal.signal(signal.SIGALARM,read_raw)
		signal.alarm(1) # check for one second
		if command == "kill":
			go = False

	tn.write("exit\n")

	print tn.read_all()
	

def read_raw():
	try:
		foo = raw_input()
		return foo
	except:
		#timeout
		return
