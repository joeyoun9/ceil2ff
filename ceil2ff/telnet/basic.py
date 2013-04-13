"""
	telnet.basic is a package which contains the simple 
	telnet connection which only receives data messages
	and prints them to a file, which can be specified or
	defaults to 'ceil_raw.dat'

	file is appended to, but if no file exists, the file
	will be created.

	Minimal dependencies exist for this code.

	this code CAN be run INDEPENDENTLY by specifying the
	input directly below this message
"""
# inputs for direct running of the telnet library

import telnetlib, os

import sys, time, getpass

# THESE ARE DEFAULT VALUES - CHANGE THEM TO YOUR SPECIFIC SETUP IF YOU
# ARE JUST RUNNING THIS CODE ON A CRON

HOST = '111.111.111.111'
PORT = 23
DIRECTORY = '.'
FNAME = 'ceil_raw.dat'
PW = False



def listen(host, port=23, directory='.', fname='ceil_raw.dat', pw=False):
	"""
		Open a persistent telnet connection listening for EOM/BOM messages.
		TUNED for Vaisala ceilometers, with standard EOM/BOM messages

		Saves a timestamp in Unix Epoch format BEFORE the message with the
		corresponding data.

		This does not call any translators, so, do not run it expecting it to
		do any more than create a file.
		
		>>> Inputs:
		
		host:................Reference to the location of the ceilometer
					eg. 100.123.3.2 (any valid network address)

		port:................Port on the referenced server to connect to
					defaults to 23 (std. telnet)

		directory:...........Directory where the file should be stored 
					This dir also holds the two control files

		fname:...............Filename of output file. Will be the name of the 
					file within the previously specified directory

		pw:..................A binary indicator if a password will be required
					for the unit logged into

	"""
	# now check if the last ob was less than 2 minutes
	if os.path.exists(directory + "/.runtime"):
		tc = open(directory + "/.runtime", 'r');
		stamp = tc.read()
		tc.close()
		if stamp and time.time() - int(stamp) < 120:
			exit()
	# otherwise we can go, if we made it here, then the logic is good.

	print "connecting to ", host, "\non port", port

	HOST = host
	if directory[-1] == "/":
		directory = directory[:-1]


	# open the telnet connection to the host on the port
	tn = telnetlib.Telnet(HOST, port)
	if pw:
		# if a password is required, then use the standard input method
		user = raw_input("Enter your remote account: ")
		password = getpass.getpass()


		tn.read_until("login: ")
		tn.write(user + "\n")
		if password:
		    tn.read_until("Password: ")
		    tn.write(password + "\n")

	go = True
	print "I'm Listening."
	# current = tn.read_all()
	# print current
	EOM = unichr(3)
	BOM = unichr(2)
	while go:
		# read until the end of the message
		tn.read_until(BOM)  # now it is the start of the message!
		# now we have filtered off all the pre message schlock.
		ob = BOM + tn.read_until(EOM)
		# add a timestamp, and pass the file to the raw data file

		print ob[0:100] + "..."  # this is for giggles right now, hopefully it is good

		# oh, we will need to check this ob, to see if it is useful...

		ts = time.time()  # epoch format
		raw = open(fname, 'a')
		raw.write("\n" + str(ts) + "\n" + ob.strip())  # time before ob! (plus some newlines)
		raw.close()


	tn.write("exit\n")  # attempt to close properly

if __name__ == "__main__":

	# the code is being run independently, so call the listener
	listen(HOST, PORT, DIRECTORY, FNAME, PW)



