#!/usr/bin/python

#####        RadiUID Server v2.0.0         #####
#####       Written by John W Kerns        #####
#####      http://blog.packetsar.com       #####
##### https://github.com/PackeTsar/radiuid #####

import os
import re
import sys
import time
import urllib
import urllib2
import commands
import ConfigParser

##### Inform RadiUID version here #####
version = "dev2.0.0"

##### Set default config file location #####
etcconfigfile = '/etc/radiuid/radiuid.conf'






#########################################################################
########################## USER INTERFACE CLASS #########################
#########################################################################
#######      Used by most other classes and methods to output     #######
#######         data to stdout and to write to the logfile        #######
#########################################################################
class user_interface(object):
	def __init__(self):
		##### ANSI Colors for use in CLI and logs #####
		self.black = '\033[0m'
		self.red = '\033[91m'
		self.green = '\033[92m'
		self.yellow = '\033[93m'
		self.blue = '\033[94m'
		self.magenta = '\033[95m'
		self.cyan = '\033[96m'
		self.white = '\033[97m'
	##### To be used like "print 'this is ' + color('green', green) + ' is it not?'" #####
	##### Easy method to write color to a str output then switch back to default black color #####
	def color(self, input, inputcolor):
		result = inputcolor + input + self.black
		return result
	##### Show progress bar #####
	##### The most awesome method in this program. Also the most useless #####
	def progress(self, message, seconds):
		timer = float(seconds) / 50
		currentwhitespace = 50
		currentblackspace = 0
		while currentwhitespace > -1:
			sys.stdout.flush()
			sys.stdout.write("\r" + message + "    [")
			sys.stdout.write("=" * currentblackspace)
			sys.stdout.write(" " * currentwhitespace)
			sys.stdout.write("]")
			currentwhitespace = currentwhitespace - 1
			currentblackspace = currentblackspace + 1
			time.sleep(timer)
		print "\n"
	##### Ask a 'yes' or 'no' question and check answer #####
	##### Accept 'yes', 'no', 'y', or 'n' in any case #####
	def yesorno(self, question):
		answer = 'temp'
		while answer.lower() != 'yes' and answer.lower() != 'no' and answer.lower() != 'y' and answer.lower() != 'n':
			answer = raw_input(self.color("----- " + question + " [yes or no]:", self.cyan))
			if answer.lower() == "no":
				return answer.lower()
			elif answer.lower() == "yes":
				return answer.lower()
			elif answer.lower() == "n":
				answer = "no"
				return answer
			elif answer.lower() == "y":
				answer = "yes"
				return answer
			else:
				print self.color("'Yes' or 'No' dude...", self.red)			
	##### Print out this ridiculous text-o-graph #####
	##### It took me like an hour to draw and I couldn't stand to just not use it #####
	def packetsar(self):
		print  self.color("\n                                ###############################################      \n\
			      #                                                 #    \n\
			    #                                                     #  \n\
			   #                                                       # \n\
			  #                                                         #\n\
			  #                            #                            #\n\
			  #                          # # #                          #\n\
			  #                         #  #  #                         #\n\
			  #                            #                            #\n\
			  # @@@@  @@  @@@@ @  @ @@@@ @@@@@  @@@@  @@  @@@@          #\n\
			  # @  @ @  @ @    @ @  @      @   @     @  @ @  @          #\n\
			  # @@@@ @@@@ @    @@   @@@    @   @ @ @ @@@@ @@@@          #\n\
			  # @    @  @ @    @ @  @      @       @ @  @ @ @           #\n\
			  # @    @  @ @@@@ @  @ @@@@   @   @@@@  @  @ @  @          #\n\
			  #                            #                            #\n\
			  #                                                         #\n\
			  #                      #           #                      #\n\
			  #                       #   ###   #                       #\n\
			  #    #####################  ###  #####################    #\n\
			  #                       #   ###   #                       #\n\
			  #                      #           #                      #\n\
			  #                                                         #\n\
			  #                            #                            #\n\
			  #                            #                            #\n\
			  #                            #                            #\n\
			  #                            #                            #\n\
			  #                            #                            #\n\
			  #                            #                            #\n\
			  #                            #                            #\n\
			  #                         #  #  #                         #\n\
		  	  #                          # # #                          #\n\
			  #                            #                            #\n\
			   #                                                       # \n\
			    #                                                     #  \n\
			      #                                                 #    \n\
			        ###############################################      \n", self.blue)






#########################################################################
########################## FILE MANAGEMENT CLASS ########################
#########################################################################
#######     Used by the main RadiUID methods to for changing,     #######
#######    checking, and maintaining files in the file system     #######
#########################################################################
class file_management(object):
	def __init__(self):
		##### Instantiate external object dependencies #####
		self.ui = user_interface()
	#######################################################
	####### File/Path-Based Data Processing Methods #######
	#######       No Direct File Interaction        #######
	#######################################################
	##### Add '/' to directory path if not included #####
	def directory_slash_add(self, directorypath):
		check = re.search("^.*\/$", directorypath)
		if check is None:
			result = directorypath + "/"
			return result
		else:
			result = directorypath
			return result
	##### Take filepath and give back directory path and filename in list where list[0] is directory path, list[1] is filename #####
	def strip_filepath(self, filepath):
		nestedlist = re.findall("^(.+)/([^/]+)$", filepath)
		templist = nestedlist[0]
		tempfilepath = templist[0]
		filepath = self.directory_slash_add(tempfilepath)
		filename = templist[1]
		resultlist = []
		resultlist.append(filepath)
		resultlist.append(filename)
		return resultlist
	#######################################################
	#######        File Manipulation Methods        #######
	#######         Direct File Interaction         #######
	#######################################################
	##### List all files in a directory path and subdirs #####
	##### Used to enumerate files in the FreeRADIUS accounting log path #####
	def list_files(self, path):
		filelist = []
		for root, directories, filenames in os.walk(path):
			for filename in filenames:
				entry = os.path.join(root, filename)
				filelist.append(entry)
				self.logwriter("normal", "Found File: " + entry + "...   Adding to file list")
		if len(filelist) == 0:
			self.logwriter("normal", "No Accounting Logs Found. Nothing to Do.")
			return filelist
		else:
			return filelist
	##### Delete all files in provided list #####
	##### Used to remove the FreeRADIUS log files so the next iteration of RadiUID doesn't pick up redundant information #####
	def remove_files(self, filelist):
		for filename in filelist:
			os.remove(filename)
			self.logwriter("normal", "Removed file: " + filename)
	##### Writes the new config data to the config file #####
	##### Used at the end of the wizard when new config values have been defined and need to be written to a config file #####
	def write_file(self, filepath, filedata):
		try:
			f = open(filepath, 'w')
			f.write(filedata)
			f.close()
		except IOError:
			print self.ui.color(time.strftime("%Y-%m-%d %H:%M:%S") + ":   " +"***********CANNOT OPEN FILE: " + filepath + " ***********\n", self.ui.red)
			print self.ui.color(time.strftime("%Y-%m-%d %H:%M:%S") + ":   " +"***********PLEASE MAKE SURE YOU RAN THE INSTALLER ('python radiuid.py install')***********\n", self.ui.red)
			quit()
	##### Check if specific file exists #####
	def file_exists(self, filepath):
		checkdata = commands.getstatusoutput("ls " + filepath)
		exists = ""
		for line in checkdata:
			line = str(line)
			if "No such" in line:
				exists = "no"
			else:
				exists = "yes"
		return exists
	##### Simple two-choice logic method to pick a preferred input over another #####
	##### Used to decide whether to use the radiuid.conf file in the 'etc' location, or the one in the local working directory #####
	def file_chooser(self, firstchoice, secondchoice):
		firstexists = self.file_exists(firstchoice)
		secondexists = self.file_exists(secondchoice)
		if firstexists == "yes" and secondexists == "yes":
			return firstchoice
		if firstexists == "yes" and secondexists == "no":
			return firstchoice
		if firstexists == "no" and secondexists == "yes":
			return secondchoice
		if firstexists == "no" and secondexists == "no":
			return "CHOOSERFAIL"
			quit()
	##### Get the current working directory #####
	##### Used when radiuid.py is run manually using the 'python radiuid.py <arg>' to get the working directory to help find the config file #####
	def get_working_directory(self):
		listoutput = commands.getstatusoutput("pwd")
		result = listoutput[1]
		result = self.directory_slash_add(result)
		return result
	##### Config file finder method with two modes, one to report on its activity, and one to operate silently #####
	##### Noisy mode used for verbose logging when running or starting the primary RadiUID program #####
	##### Quiet mode used for purposes like the command interface when verbose output is not desired #####
	def find_config(self, mode):
		localconfigfile = self.get_working_directory() + "radiuid.conf"
		if mode == "noisy":
			print time.strftime("%Y-%m-%d %H:%M:%S") + ":   " + "***********LOOKING FOR RADIUID CONFIG FILE...***********" + "\n"
			print time.strftime("%Y-%m-%d %H:%M:%S") + ":   " + "***********DETECTED WORKING DIRECTORY: " + self.get_working_directory() + "***********" + "\n"
			print time.strftime("%Y-%m-%d %H:%M:%S") + ":   " + "***********CHECKING LOCATION: PREFERRED LOCATION - " + etcconfigfile + "***********" + "\n"
			print time.strftime("%Y-%m-%d %H:%M:%S") + ":   " + "***********CHECKING LOCATION: ALTERNATE LOCATION IN LOCAL DIRECTORY - " + localconfigfile + "***********" + "\n"
			configfile = self.file_chooser(etcconfigfile, localconfigfile)
			print time.strftime("%Y-%m-%d %H:%M:%S") + ":   " + "***********FOUND CONFIG FILE IN LOCATION: " + configfile + "***********" + "\n"
			return configfile
		if mode == "quiet":
			configfile = self.file_chooser(etcconfigfile, localconfigfile)
			return configfile
		else:
			print "Need to set mode for find_config to 'noisy' or 'quiet'"
			quit()
	##### Pull logfile location from configfile #####
	def get_logfile(self):
		configfile = self.find_config("quiet")
		parser = ConfigParser.SafeConfigParser()
		parser.read(configfile)
		global logfile
		logfile = parser.get('Paths_and_Files', 'logfile')
	##### Core IO method for logwriter operations. Excludes mode awareness #####
	def logwriter_core(self, file, input):
		target = open(file, 'a')
		target.write(time.strftime("%Y-%m-%d %H:%M:%S") + ":   " + input + "\n")
		target.close()
	##### Writes lines to the log file in different modes #####
	##### Uses the logfile variable published to the global namespace #####
	##### Modes of use change what log_writer does when it encounters certain errors. Modes are normal #####
	def logwriter(self, mode, input):
		if mode == "normal": # Only use normal mode if you have already initialized the logfile to global namespace
			try:
				target = open(logfile, 'a')
				target.write(time.strftime("%Y-%m-%d %H:%M:%S") + ":   " + input + "\n")
				print time.strftime("%Y-%m-%d %H:%M:%S") + ":   " + input + "\n"
				target.close()
			except IOError:
				print self.color(time.strftime("%Y-%m-%d %H:%M:%S") + ":   " +"***********CANNOT OPEN FILE: " + logfile + " ***********\n", self.red)
				print self.color(time.strftime("%Y-%m-%d %H:%M:%S") + ":   " +"***********PLEASE MAKE SURE YOU RAN THE INSTALLER ('python radiuid.py install')***********\n", self.red)
				quit()
			except NameError:
				print self.ui.color(time.strftime("%Y-%m-%d %H:%M:%S") + ":   " +"*********** LOGFILE VARIABLE NOT FOUND! ***********\n", self.ui.red)
				quit()
		if mode == "cli":
			configfile = self.find_config("quiet")
			if configfile == "CHOOSERFAIL":
				print self.ui.color("***** WARNING: Could not write CLI accounting info to log file *****", self.ui.yellow)
			else:
				self.get_logfile()
				self.logwriter_core(logfile, input)
				print time.strftime("%Y-%m-%d %H:%M:%S") + ":   " + input + "\n"
		if mode == "cli-noconsole":
			configfile = self.find_config("quiet")
			if configfile == "CHOOSERFAIL":
				print self.ui.color("***** WARNING: Could not write CLI accounting info to log file *****", self.ui.yellow)
			else:
				self.get_logfile()
				self.logwriter_core(logfile, input)
				# no printing to console
		if mode == "quietfail":
			configfile = self.find_config("quiet")
			if configfile != "CHOOSERFAIL":
				self.get_logfile()
				self.logwriter_core(logfile, input)
				print time.strftime("%Y-%m-%d %H:%M:%S") + ":   " + input + "\n"






#########################################################################
########################## DATA PROCESSING CLASS ########################
#########################################################################
#######       Used by the main RadiUID methods to munge data      #######
#########################################################################
#########################################################################
class data_processing(object):
	def __init__(self):
		##### Instantiate external object dependencies #####
		self.ui = user_interface()
		self.filemgmt = file_management()
		####################################################
	##### Search list of files for a searchterm and uses deliniator term to count instances in file, then returns a dictionary where key=instance and value=line where term was found #####
	##### Used to search through FreeRADIUS log files for usernames and IP addresses, then turn them into dictionaries to be sent to the "push" function #####
	def search_to_dict(self, filelist, delineator, searchterm):
		dict = {}
		entry = 0
		for filename in filelist:
			self.filemgmt.logwriter("normal", 'Searching File: ' + filename + ' for ' + searchterm)
			with open(filename, 'r') as filetext:
				for line in filetext:
					if delineator in line:
						entry = entry + 1
					if searchterm in line:
						dict[entry] = line
		return dict
	##### Clean up IP addresses in dictionary #####
	##### Removes unwanted data from the lines with useful IP addresses in them #####
	def clean_ips(self, dictionary):
		newdict = {}
		ipaddress_regex = "(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
		for key, value in dictionary.iteritems():
			cleaned = re.findall(ipaddress_regex, value, flags=0)[0]
			newdict[key] = cleaned
		self.filemgmt.logwriter("normal", "IP Address List Cleaned Up!")
		return newdict
	##### Clean up user names in dictionary #####
	##### Removes unwanted data from the lines with useful usernames in them #####
	def clean_names(self, dictionary):
		newdict = {}
		username_regex = "(\'.*\')"
		for key, value in dictionary.iteritems():
			clean1 = re.findall(username_regex, value, flags=0)[0]
			cleaned = clean1.replace("'", "")
			newdict[key] = cleaned
		self.filemgmt.logwriter("normal", "Username List Cleaned Up!")
		return newdict
	##### Merge dictionary values from two dictionaries into one dictionary and remove duplicates #####
	##### Used to compile the list of users into a dictionary for use in the push function #####
	##### Deduplication is not explicitly written but is just a result of pushing the same data over and over to a dictionary #####
	def merge_dicts(self, keydict, valuedict):
		newdict = {}
		keydictkeylist = keydict.keys()
		for each in keydictkeylist:
			v = valuedict[each]
			k = keydict[each]
			newdict[k] = v
		self.filemgmt.logwriter("normal", "Dictionary values merged into one dictionary")
		return newdict






#########################################################################
##################### PAN FIREWALL INTERACTION CLASS ####################
#########################################################################
#######     Used by the main RadiUID methods to for creating      #######
#######       and making REST API calls to the PAN Firewalls      #######
#########################################################################
class palo_alto_firewall_interaction(object):
	def __init__(self):
		##### Instantiate external object dependencies #####
		self.ui = user_interface()
		self.filemgmt = file_management() #push_uids uses flmgmt to remove files after push
	#######################################################
	#######         XML Processing Methods          #######
	####### Used for PAN Interaction XML Generation #######
	#######################################################
	##### Accepts a list of IP addresses (keys) and usernames (vals) in a dictionary and outputs a list of XML formatted entries as a list #####
	##### This method outputs a list which is utilized by the xml_assembler_v67 method #####
	def xml_formatter_v67(self, ipanduserdict):
		if panosversion == '7' or panosversion == '6':
			ipaddresses = ipanduserdict.keys()
			xmllist = []
			for ip in ipaddresses:
				entry = '<entry name="%s\%s" ip="%s" timeout="%s">' % (userdomain, ipanduserdict[ip], ip, timeout)
				xmllist.append(entry)
				entry = ''
			return xmllist
		else:
			self.filemgmt.logwriter("normal", self.ui.color("PAN-OS version not supported for XML push!", self.ui.red))
			quit()
	##### Accepts a list of XML-formatted IP-to-User mappings and produces a list of complete and encoded URLs which are used to push UID data #####
	##### Each URL will contain no more than 100 UID mappings which can all be pushed at the same time by the push_uids method #####
	def xml_assembler_v67(self, ipuserxmllist):
		if panosversion == '7' or panosversion == '6':
			finishedurllist = []
			xmluserdata = ""
			iterations = 0
			while len(ipuserxmllist) > 0:
				for entry in ipuserxmllist[:100]:
					xmluserdata = xmluserdata + entry + "\n</entry>\n"
					ipuserxmllist.remove(entry)
				urldecoded = '<uid-message>\n\
	<version>1.0</version>\n\
	<type>update</type>\n\
	<payload>\n\
	<login>\n\
	' + xmluserdata + '\
	</login>\n\
	</payload>\n\
	</uid-message>'
				urljunk = urllib.quote_plus(urldecoded)
				finishedurllist.append('https://' + hostname + '/api/?key=' + pankey + extrastuff + urljunk)
				xmluserdata = ""
			return finishedurllist
		else:
			self.filemgmt.logwriter("normal", self.ui.color("PAN-OS version not supported for XML push!", self.ui.red))
			quit()
	#######################################################
	#######         PAN Interaction Methods         #######
	#######        Used for PAN Interaction         #######
	#######################################################
	##### Function to pull API key from firewall to be used for REST HTTP calls #####
	##### Used during initialization of the RadiUID main process to generate the API key #####
	def pull_api_key(self, username, password):
		encodedusername = urllib.quote_plus(username)
		encodedpassword = urllib.quote_plus(password)
		url = 'https://' + hostname + '/api/?type=keygen&user=' + encodedusername + '&password=' + encodedpassword
		response = urllib2.urlopen(url).read()
		self.filemgmt.logwriter("normal", "Pulling API key using PAN credentials: " + username + "\\" + password + "\n")
		if 'success' in response:
			self.filemgmt.logwriter("normal", self.ui.color(response, self.ui.green) + "\n")
			stripped1 = response.replace("<response status = 'success'><result><key>", "")
			stripped2 = stripped1.replace("</key></result></response>", "")
			pankey = stripped2
			return pankey
		else:
			log_writer("normal", self.ui.color('ERROR: Username\\password failed. Please re-enter in config file...' + '\n', self.ui.red))
			quit()
	##### Accepts IP-to-User mappings as a dict in, uses the xml-formatter and xml-assembler to generate a list of URLS, then opens those URLs and logs response codes  #####
	def push_uids(self, ipanduserdict, filelist):
		xml_list = self.xml_formatter_v67(ipanduserdict)
		urllist = self.xml_assembler_v67(xml_list)
		self.filemgmt.logwriter("normal", "Pushing the below IP : User mappings via " + str(len(urllist)) + " API calls")
		for entry in ipanduserdict:
			self.filemgmt.logwriter("normal", "IP Address: " + self.ui.color(entry, self.ui.cyan) + "\t\tUsername: " + self.ui.color(ipanduserdict[entry], self.ui.cyan))
		for eachurl in urllist:
			response = urllib2.urlopen(eachurl).read()
			self.filemgmt.logwriter("normal", self.ui.color(response, self.ui.green) + "\n")
		self.filemgmt.remove_files(filelist)






#########################################################################
####################### RADIUID MAIN PROCESS CLASS ######################
#########################################################################
#######     Contains the primary elements which pulls config      #######
#######     variables, collects log data, and pushes mappings     #######
#########################################################################
class radiuid_main_process(object):
	def __init__(self):
		##### Instantiate external object dependencies #####
		self.ui = user_interface()
		self.dpr = data_processing()
		self.pafi = palo_alto_firewall_interaction()
		self.filemgmt = file_management()
		####################################################
	##### Initialize method used to pull all necessary RadiUID information from the config file and dump the data into variables in the global namespace #####
	##### This method runs once during the initial startup of the program #####
	def initialize(self):
		print time.strftime("%Y-%m-%d %H:%M:%S") + ":   " + "***********MAIN PROGRAM INITIALIZATION KICKED OFF...***********" + "\n"
		global logfile
		global radiuslogpath
		global hostname
		global panosversion
		global panuser
		global panpassword
		global extrastuff
		global ipaddressterm
		global usernameterm
		global delineatorterm
		global userdomain
		global timeout
		##### Check if config file exists. Fail program if it doesn't #####
		configfile = self.filemgmt.find_config("noisy")
		checkfile = self.filemgmt.file_exists(configfile)
		if checkfile == 'no':
			print self.ui.color(time.strftime(
				"%Y-%m-%d %H:%M:%S") + ":   " + "ERROR: CANNOT FIND RADIUID CONFIG FILE IN TYPICAL PATHS. QUITTING PROGRAM. RE-RUN INSTALLER ('python radiuid.py install')" + "\n", self.ui.red)
			quit()
		if checkfile == 'yes':
			print time.strftime(
				"%Y-%m-%d %H:%M:%S") + ":   " + "***********USING CONFIG FILE " + configfile + " TO START RADIUID APPLICATION***********" + "\n"
			print time.strftime(
				"%Y-%m-%d %H:%M:%S") + ":   " + "***********READING IN RADIUID LOGFILE INFORMATION. ALL SUBSEQUENT OUTPUT WILL BE LOGGED TO THE LOGFILE***********" + "\n"
		##### Open the config file and read in the logfile location information #####
		parser = ConfigParser.SafeConfigParser()
		parser.read(configfile)
		logfile = parser.get('Paths_and_Files', 'logfile')
		##### Initial log entry and help for anybody starting the .py program without first installing it #####
		self.filemgmt.logwriter("normal", "***********INITIAL WRITE TO THE LOG FILE: " + logfile + "...***********")
		self.filemgmt.logwriter("normal", "***********RADIUID INITIALIZING... IF PROGRAM FAULTS NOW, MAKE SURE YOU SUCCESSFULLY RAN THE INSTALLER ('python radiuid.py install')***********")
		##### Suck in all variables from config file (only run when program is initially started, not during while loop) #####
		self.filemgmt.logwriter("normal", "***********INITIALIZING VARIABLES FROM CONFIG FILE: " + configfile + "...***********")
		self.filemgmt.logwriter("normal", "Initialized variable:" "\t" + "logfile" + "\t\t\t\t" + "with value:" + "\t" + self.ui.color(logfile, self.ui.green))
		radiuslogpath = parser.get('Paths_and_Files', 'radiuslogpath')
		self.filemgmt.logwriter("normal", "Initialized variable:" "\t" + "radiuslogpath" + "\t\t\t" + "with value:" + "\t" + self.ui.color(radiuslogpath, self.ui.green))
		hostname = parser.get('Palo_Alto_Target', 'hostname')
		self.filemgmt.logwriter("normal", "Initialized variable:" "\t" + "hostname" + "\t\t\t" + "with value:" + "\t" + self.ui.color(hostname, self.ui.green))
		panosversion = parser.get('Palo_Alto_Target', 'panosversion')
		self.filemgmt.logwriter("normal", "Initialized variable:" "\t" + "panosversion" + "\t\t\t" + "with value:" + "\t" + self.ui.color(panosversion, self.ui.green))
		panuser = parser.get('Palo_Alto_Target', 'username')
		self.filemgmt.logwriter("normal", "Initialized variable:" "\t" + "panuser" + "\t\t\t\t" + "with value:" + "\t" + self.ui.color(panuser, self.ui.green))
		panpassword = parser.get('Palo_Alto_Target', 'password')
		self.filemgmt.logwriter("normal", "Initialized variable:" "\t" + "panpassword" + "\t\t\t" + "with value:" + "\t" + self.ui.color(panpassword, self.ui.green))
		extrastuff = parser.get('URL_Stuff', 'extrastuff')
		self.filemgmt.logwriter("normal", "Initialized variable:" "\t" + "extrastuff" + "\t\t\t" + "with value:" + "\t" + self.ui.color(extrastuff, self.ui.green))
		ipaddressterm = parser.get('Search_Terms', 'ipaddressterm')
		self.filemgmt.logwriter("normal", "Initialized variable:" "\t" + "ipaddressterm" + "\t\t\t" + "with value:" + "\t" + self.ui.color(ipaddressterm, self.ui.green))
		usernameterm = parser.get('Search_Terms', 'usernameterm')
		self.filemgmt.logwriter("normal", "Initialized variable:" "\t" + "usernameterm" + "\t\t\t" + "with value:" + "\t" + self.ui.color(usernameterm, self.ui.green))
		delineatorterm = parser.get('Search_Terms', 'delineatorterm')
		self.filemgmt.logwriter("normal", "Initialized variable:" "\t" + "delineatorterm" + "\t\t\t" + "with value:" + "\t" + self.ui.color(delineatorterm, self.ui.green))
		userdomain = parser.get('UID_Settings', 'userdomain')
		self.filemgmt.logwriter("normal", "Initialized variable:" "\t" + "userdomain" + "\t\t\t" + "with value:" + "\t" + self.ui.color(userdomain, self.ui.green))
		timeout = parser.get('UID_Settings', 'timeout')
		self.filemgmt.logwriter("normal", "Initialized variable:" "\t" + "timeout" + "\t\t\t\t" + "with value:" + "\t" + self.ui.color(timeout, self.ui.green))
		##### Explicitly pull PAN key now and store API key in the main namespace #####
		self.filemgmt.logwriter("normal", "***********************************CONNECTING TO PALO ALTO FIREWALL TO EXTRACT THE API KEY...***********************************")
		self.filemgmt.logwriter("normal", "********************IF PROGRAM FREEZES/FAILS RIGHT NOW, THEN THERE IS LIKELY A COMMUNICATION PROBLEM WITH THE FIREWALL********************")
		global pankey
		pankey = self.pafi.pull_api_key(panuser, panpassword)
		self.filemgmt.logwriter("normal", "Initialized variable:" "\t" + "pankey" + "\t\t\t\t" + "with value:" + "\t" + pankey)
		self.filemgmt.logwriter("normal", "*******************************************CONFIG FILE SETTINGS INITIALIZED*******************************************")
		self.filemgmt.logwriter("normal", "***********************************RADIUID SERVER STARTING WITH INITIALIZED VARIABLES...******************************")
	##### RadiUID looper method which initializes the namespace with config variables and loops the main RadiUID program #####
	def looper(self):
		configfile = self.filemgmt.find_config("noisy")
		self.initialize()
		while __name__ == "__main__":
			filelist = self.filemgmt.list_files(radiuslogpath)
			if len(filelist) > 0:
				usernames = self.dpr.search_to_dict(filelist, delineatorterm, usernameterm)
				ipaddresses = self.dpr.search_to_dict(filelist, delineatorterm, ipaddressterm)
				usernames = self.dpr.clean_names(usernames)
				ipaddresses = self.dpr.clean_ips(ipaddresses)
				ipanduserdict = self.dpr.merge_dicts(ipaddresses, usernames)
				self.pafi.push_uids(ipanduserdict, filelist)
				del filelist
				del usernames
				del ipaddresses
				del ipanduserdict
			time.sleep(10)






#########################################################################
################### INSTALLER/MAINTENANCE METHODS CLASS #################
#########################################################################
#######            Contains methods which are used by the         #######
#######                 Installer/Maintenance Utility             #######
#########################################################################
class imu_methods(object):
	def __init__(self):
		##### Instantiate external object dependencies #####
		self.ui = user_interface()
		####################################################
	#######################################################
	#######          OS Interaction Methods           #####
	### Runs commands on the OS without file interaction ##
	#######################################################
	##### Get currently logged in user #####
	def currentuser(self):
		checkdata = commands.getstatusoutput("whoami")[1]
		return checkdata
	##### Check if a particular systemd service is installed #####
	##### Used to check if FreeRADIUS and RadiUID have already been installed #####
	def check_service_installed(self, service):
		checkdata = commands.getstatusoutput("systemctl status " + service)
		installed = 'temp'
		for line in checkdata:
			line = str(line)
			if 'not-found' in line:
				installed = 'no'
			else:
				installed = 'yes'
		return installed
	##### Check if a particular systemd service is running #####
	##### Used to check if FreeRADIUS and RadiUID are currently running #####
	def check_service_running(self, service):
		checkdata = commands.getstatusoutput("systemctl status " + service)
		running = 'temp'
		for line in checkdata:
			line = str(line)
			if 'active (running)' in line:
				running = 'yes'
			else:
				running = 'no'
		return running
	##### Restart a particular SystemD service #####
	def restart_service(self, service):
		commands.getstatusoutput("systemctl start " + service)
		commands.getstatusoutput("systemctl restart " + service)
		self.ui.progress("Starting/Restarting: ", 1)
		print "\n\n#########################################################################"
		os.system("systemctl status " + service)
		print "#########################################################################\n\n"
	##### Install FreeRADIUS server #####
	def install_freeradius(self):
		os.system('yum install freeradius -y')
		print "\n\n\n\n\n\n****************Setting FreeRADIUS as a system service...****************\n"
		self.ui.progress("Progress: ", 1)
		os.system('systemctl enable radiusd')
		os.system('systemctl start radiusd')
	#######################################################
	#######           UI Question Methods           #######
	#######   Used for asking questions in the UI   #######
	#######################################################
	##### Change variables to change settings #####
	##### Used to ask questions and set new config settings in the install/maintenance utility #####
	def change_setting(self, setting, question):
		newsetting = raw_input(self.ui.color(">>>>> " + question + " [" + setting + "]: ", self.ui.cyan))
		if newsetting == '':
			print self.ui.color("~~~ Keeping current setting...", self.ui.green)
			newsetting = setting
		else:
			print self.ui.color("~~~ Changed setting to: " + newsetting, self.ui.yellow)
		return newsetting
	##### Check that legit CIDR block was entered #####
	##### Used to check IP blocks entered into the wizard for configuration of FreeRADIUS #####
	def cidr_checker(self, cidr_ip_block):
		check = re.search("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\/(?:[0-9]|1[0-9]|2[0-9]|3[0-2]?)$", cidr_ip_block)
		if check is None:
			result = "no"
		else:
			result = "yes"
		return result
	##### Create dictionary with client IP and shared password entries for FreeRADIUS server #####
	##### Used to ask questions during install about IP blocks and shared secret to use for FreeRADIUS server #####
	def freeradius_create_changes(self):
		##### Set variables for use later #####
		keepchanging = "yes"
		addips = []
		##### Ask for IP address blocks and append each entry to a list. User can accept the example though #####
		while keepchanging != "no":
			addipexample = "10.0.0.0/8"
			goround = raw_input(
				self.ui.color('\n>>>>> Enter the IP subnet to use for recognition of RADIUS accounting sources: [' + addipexample + ']:', self.ui.cyan))
			if goround == "":
				goround = addipexample
			ipcheck = self.cidr_checker(goround)
			if ipcheck == 'no':
				print self.ui.color("~~~ Nope. Give me a legit CIDR block...", self.ui.red)
			elif ipcheck == 'yes':
				addips.append(goround)
				print self.ui.color("~~~ Added " + goround + " to list\n", self.ui.yellow)
				keepchanging = self.ui.yesorno("Do you want to add another IP block to the list of trusted sources?")
		##### List out entries #####
		print "\n\n"
		print "List of IP blocks for accounting sources:"
		for each in addips:
			print self.ui.color(each, self.ui.yellow)
		print "\n\n"
		##### Have user enter shared secret to pair with all IP blocks in output dictionary #####
		radiussecret = ""
		radiussecret = raw_input(
			self.ui.color('>>>>> Enter a shared RADIUS secret to use with the accounting sources: [password123]:', self.ui.cyan))
		if radiussecret == "":
			radiussecret = "password123"
		print self.ui.color("~~~ Using '" + radiussecret + "' for shared secret\n", self.ui.yellow)
		##### Pair each IP entry with the shared secret and put in dictionary for output #####
		radiusclientdict = {}
		for each in addips:
			radiusclientdict[each] = radiussecret
		return radiusclientdict
	#######################################################
	#######        File Interaction Methods         #######
	#######   Used to create/change/delete files    #######
	#######################################################
	#### Copy RadiUID system and config files to appropriate paths for installation #####
	def copy_radiuid(self):
		configfilepath = "/etc/radiuid/"
		binpath = "/bin/"
		os.system('mkdir -p ' + configfilepath)
		os.system('cp radiuid.conf ' + configfilepath + 'radiuid.conf')
		os.system('cp radiuid.py ' + binpath + 'radiuid')
		os.system('chmod 777 ' + binpath + 'radiuid')
		self.ui.progress("Copying Files: ", 2)
	#### Install RadiUID SystemD service #####
	def install_radiuid(self):
		#### STARTFILE DATA START #####
		startfile = "[Unit]" \
		            "\n" + "Description=RadiUID User-ID Service" \
		                   "\n" + "After=network.target" \
		                          "\n" \
		                          "\n" + "[Service]" \
		                                 "\n" + "Type=simple" \
		                                        "\n" + "User=root" \
		                                               "\n" + "ExecStart=/bin/bash -c 'cd /bin; python radiuid run'" \
		                                                                                                         "\n" + "Restart=on-abort" \
		                                                                                                                "\n" \
		                                                                                                                "\n" \
		                                                                                                                "\n" + "[Install]" \
		                                                                                                                       "\n" + "WantedBy=multi-user.target" \
		##### STARTFILE DATA STOP #####
		f = open('/etc/systemd/system/radiuid.service', 'w')
		f.write(startfile)
		f.close()
		self.ui.progress("Installing: ", 2)
		os.system('systemctl enable radiuid')
	##### Apply new settings as veriables in the namespace #####
	##### Used to write new setting values to namespace to be picked up and used by the write_file method to write to the config file #####
	def apply_setting(self, file_data, settingname, oldsetting, newsetting):
		if oldsetting == newsetting:
			print self.ui.color("***** No changes to  : " + settingname, self.ui.green)
			return file_data
		else:
			new_file_data = file_data.replace(settingname + " = " + oldsetting, settingname + " = " + newsetting)
			padlen = 50 - len("***** Changed setting: " + settingname)
			pad = " " * padlen
			print self.ui.color("***** Changed setting: " + settingname + pad + "|\tfrom: " + oldsetting + "\tto: " + newsetting, self.ui.yellow)
			return new_file_data
	##### Use dictionary of edits for FreeRADIUS and push them to the config file #####
	def freeradius_editor(self, dict_edits):
		clientconfpath = '/etc/raddb/clients.conf'
		iplist = dict_edits.keys()
		print "\n\n\n"
		print "#####About to append the below client data to the FreeRADIUS client.conf file#####"
		print "##################################################################################"
		for ip in iplist:
			newwrite = "\nclient " + ip + " {\n    secret      = " + dict_edits[
				ip] + "\n    shortname   = Created_By_RadiUID\n }\n"
			f = open(clientconfpath, 'a')
			f.write(newwrite)
			f.close()
			print newwrite
		oktowrite = self.ui.yesorno("OK to write to client.conf file?")
		if oktowrite == "yes":
			print "###############Writing the above to the FreeRADIUS client.conf file###############"
			print "##################################################################################"
			print "\n"
			self.ui.progress("Writing: ", 1)
			print "\n\n\n"
			print "****************Restarting the FreeRADIUS service to effect changes...****************\n\n"
			self.ui.progress("Starting/Restarting: ", 1)
			os.system('systemctl restart radiusd')
			os.system('systemctl status radiusd')
			checkservice = self.check_service_running('radiusd')
			if checkservice == 'no':
				print self.ui.color("\n\n***** Uh Oh... Looks like the FreeRADIUS service failed to start back up.", self.ui.red)
				print self.ui.color("***** We may have made some adverse changes to the config file.", self.ui.red)
				print self.ui.color("***** Visit the FreeRADIUS config file at " + clientconfpath + " and remove the bad changes.", self.ui.red)
				print self.ui.color("***** Then try to start the FreeRADIUS service by issuing the 'radiuid restart freeradius' command", self.ui.red)
				raw_input(self.ui.color("Hit ENTER to continue...\n\n>>>>>", self.ui.cyan))
			elif checkservice == 'yes':
				print self.ui.color("\n\n***** Great Success!! Looks like FreeRADIUS restarted and is back up now!", self.ui.green)
				print self.ui.color("***** If you need to manually edit the FreeRADIUS config file, it is located at " + clientconfpath, self.ui.green)
				raw_input(self.ui.color("\nHit ENTER to continue...\n\n>>>>>", self.ui.cyan))
		elif oktowrite == "no":
			print "~~~ OK Not writing it"






#########################################################################
################### INSTALLER/MAINTENANCE UTILITY CLASS #################
#########################################################################
#######           Contains the main method which runs the         #######
#######                 Installer/Maintenance Utility             #######
#########################################################################
class installer_maintenance_utility(object):
	def __init__(self):
		##### Instantiate external object dependencies #####
		self.ui = user_interface()
		self.filemgmt = file_management()
		self.imum = imu_methods()
		####################################################
	def im_utility(self):
		'''
		############# LEGEND FOR TEXUTAL CUES USED IN INSTALLER/MAINTENANCE UTILITY #############
		#########################################################################################
		****************Status....what program is doing..****************
		***** Informational
		----- Yes or No question
		~~~~~ Acknowledgement of an answer to a question
		>>>>> Command to enter information
		#########################################################################################
		'''
		self.ui.packetsar()
		self.ui.progress("Running RadiUID in Install/Maintenance Mode:", 3)
		print "\n\n\n\n\n\n\n\n"
		print '                       ##########################################################' \
				'\n' + '                       ##### Install\Maintenance Utility for RadiUID Server #####' \
				'\n' + '                       #####                 Version ' + version + '                  #####' \
				'\n' + '                       #####             Please Use Carefully!              #####' \
				'\n' + '                       ##########################################################' \
				'\n' + '                       ##########################################################' \
				'\n' + '                       ##########################################################' \
				'\n' + '                       ##########       Written by John W Kerns        ##########' \
				'\n' + '                       ##########      http://blog.packetsar.com       ##########' \
				'\n' + '                       ########## https://github.com/PackeTsar/radiuid ##########' \
				'\n' + '                       ##########################################################' \
				'\n' + '                       ##########################################################' \
				'\n' + '                       ##########################################################' \
	 \
	
		print "\n\n\n"
		print "****************First, we will check if FreeRADIUS and RadiUID are installed yet...****************\n"
		raw_input(self.ui.color("\n\n>>>>> Hit ENTER to continue...\n\n>>>>>", self.ui.cyan))
		print "\n\n\n\n\n\n\n"
		#########################################################################
		###Check if FreeRADIUS is installed and running already
		#########################################################################
		print "\n\n\n\n\n\n****************Checking if FreeRADIUS is installed...****************\n"
		freeradiusinstalled = self.imum.check_service_installed('radiusd')
		freeradiusrunning = self.imum.check_service_running('radiusd')
		if freeradiusinstalled == 'yes' and freeradiusrunning == 'yes':
			print self.ui.color("***** Looks like the FreeRADIUS service is already installed and running...skipping the install of FreeRADIUS", self.ui.green)
		if freeradiusinstalled == 'yes' and freeradiusrunning == 'no':
			freeradiusrestart = self.ui.yesorno("Looks like FreeRADIUS is installed, but not running....want to start it up?")
			if freeradiusrestart == 'yes':
				self.imum.restart_service('radiusd')
				freeradiusrunning = self.imum.check_service_running('radiusd')
				if freeradiusrunning == 'no':
					print self.ui.color("***** It looks like FreeRADIUS failed to start up. You may need to change its settings and restart it manually...", self.ui.red)
					print self.ui.color("***** Use the command 'radiuid edit clients' to open and edit the FreeRADIUS client settings file manually", self.ui.red)
				if freeradiusrunning == 'yes':
					print self.ui.color("***** Very nice....Great Success!!!", self.ui.green)
			if freeradiusrestart == 'no':
				print self.ui.color("~~~ OK, leaving it off...", self.ui.yellow)
		if freeradiusinstalled == 'no' and freeradiusrunning == 'no':
			freeradiusinstall = self.ui.yesorno(
				"Looks like FreeRADIUS is not installed. It is required by RadiUID. Is it ok to install FreeRADIUS?")
			if freeradiusinstall == 'yes':
				self.imum.install_freeradius()
				checkservice = self.imum.check_service_running('radiusd')
				if checkservice == 'no':
					print self.ui.color("\n\n***** Uh Oh... Looks like the FreeRADIUS service failed to install or start up.", self.ui.red)
					print self.ui.color("***** It is possible that the native package manager is not able to download the install files.", self.ui.red)
					print self.ui.color("***** Make sure that you have internet access and your package manager is able to download the FreeRADIUS install files", self.ui.red)
					raw_input(self.ui.color("Hit ENTER to quit the program...\n", self.ui.cyan))
					quit()
				elif checkservice == 'yes':
					print self.ui.color("\n\n***** Great Success!! Looks like FreeRADIUS installed and started up successfully.", self.ui.green)
					print self.ui.color("***** We will be adding client IP and shared secret info to FreeRADIUS later in this wizard.", self.ui.green)
					print self.ui.color("***** If you need to manually edit the FreeRADIUS config file later, you can run 'radiuid edit clients' in the CLI", self.ui.green)
					print self.ui.color("***** You can also manually open the file for editing. It is located at /etc/raddb/clients.conf", self.ui.green)
					raw_input(self.ui.color("\n***** Hit ENTER to continue...\n\n>>>>>", self.ui.cyan))
			if freeradiusinstall == 'no':
				print self.ui.color("***** FreeRADIUS is required by RadiUID. Quitting the installer", self.ui.red)
				quit()
		#########################################################################
		###Check if RadiUID is installed and running already
		#########################################################################
		print "\n\n\n\n\n\n****************Checking if RadiUID is already installed...****************\n"
		radiuidinstalled = self.imum.check_service_installed('radiuid')
		radiuidrunning = self.imum.check_service_running('radiuid')
		if radiuidinstalled == 'yes' and radiuidrunning == 'yes':
			print self.ui.color("***** Looks like the RadiUID service is already installed and running...skipping the install of RadiUID\n", self.ui.green)
			radiuidreinstall = self.ui.yesorno("Do you want to re-install the RadiUID service?")
			if radiuidreinstall == 'yes':
				print self.ui.color("***** You are about to re-install the RadiUID service...", self.ui.yellow)
				print self.ui.color("***** If you continue, you will have to proceed with the wizard to the next step where we configure the settings in the config file...", self.ui.yellow)
				raw_input(self.ui.color(">>>>> Hit CTRL-C to quit. Hit ENTER to continue\n>>>>>", self.ui.cyan))
				print "\n\n****************Re-installing the RadiUID service...****************\n"
				self.imum.copy_radiuid()
				self.imum.install_radiuid()
				print "\n\n****************We will start up the RadiUID service once we configure the .conf file****************\n"
			if radiuidreinstall == 'no':
				print "~~~ Yea, probably best to leave it alone..."
		if radiuidinstalled == 'yes' and radiuidrunning == 'no':
			print "\n"
			print self.ui.color("***** Looks like RadiUID is installed, but not running....", self.ui.yellow)
			radiuidrestart = self.ui.yesorno("Do you want to start it up?")
			if radiuidrestart == 'yes':
				self.imum.restart_service('radiuid')
				self.ui.progress('Checking for Successful Startup', 3)
				os.system("systemctl status radiuid")
				radiuidrunning = self.imum.check_service_running('radiuid')
				if radiuidrunning == "yes":
					print self.ui.color("***** Very nice....Great Success!!!", self.ui.green)
				if radiuidrunning == "no":
					print self.ui.color("***** Looks like the startup failed...", self.ui.red)
					radiuidreinstall = self.ui.yesorno("Do you want to re-install the RadiUID service?")
					if radiuidreinstall == 'yes':
						print "\n\n****************Re-installing the RadiUID service...****************\n"
						self.imum.copy_radiuid()
						self.imum.install_radiuid()
						print "\n\n****************We will start up the RadiUID service once we configure the .conf file****************\n"
			if radiuidrestart == 'no':
				print self.ui.color("~~~ OK, leaving it off...", self.ui.yellow)
		if radiuidinstalled == 'no' and radiuidrunning == 'no':
			print "\n"
			radiuidinstall = self.ui.yesorno("Looks like RadiUID is not installed. Is it ok to install RadiUID?")
			if radiuidinstall == 'yes':
				print "\n\n****************Installing the RadiUID service...****************\n"
				self.imum.copy_radiuid()
				self.imum.install_radiuid()
				print "\n\n****************We will start up the RadiUID service once we configure the .conf file****************\n"
	
			if radiuidinstall == 'no':
				print self.ui.color("***** The install of RadiUID is required. Quitting the installer", self.ui.red)
				quit()
		print "\n\n\n\n"
		#########################################################################
		###Read current .conf settings into interpreter
		#########################################################################
		editradiuidconf = self.ui.yesorno("Do you want to edit the settings in the RadiUID .conf file (if you just installed or reinstalled RadiUID, then you need to do this)?")
		if editradiuidconf == "yes":
			configfile = self.filemgmt.find_config("noisy")
			checkfile = self.filemgmt.file_exists(configfile)
			if checkfile == 'no':
				print self.ui.color("ERROR: Config file (radiuid.conf) not found. Make sure the radiuid.conf file exists in same directory as radiuid.py", self.ui.red)
				quit()
			print "Configuring File: " + self.ui.color(configfile, self.ui.green) + "\n"
			print "\n\n\n****************Now, we will import the settings from the " + configfile + " file...****************\n"
			print "*****************The current values for each setting are [displayed in the prompt]****************\n"
			print "****************Leave the prompt empty and hit ENTER to accept the current value****************\n"
			raw_input(self.ui.color("\n\n>>>>> Hit ENTER to continue...\n\n>>>>>", self.ui.cyan))
			print "\n\n\n\n\n\n\n"
			print "**************** Reading in current settings from " + configfile + " ****************\n"
			self.ui.progress('Reading:', 1)
			parser = ConfigParser.SafeConfigParser()
			parser.read(configfile)
			f = open(configfile, 'r')
			config_file_data = f.read()
			f.close()
			logfile = parser.get('Paths_and_Files', 'logfile')
			radiuslogpath = parser.get('Paths_and_Files', 'radiuslogpath')
			hostname = parser.get('Palo_Alto_Target', 'hostname')
			panosversion = parser.get('Palo_Alto_Target', 'panosversion')
			username = parser.get('Palo_Alto_Target', 'username')
			password = parser.get('Palo_Alto_Target', 'password')
			extrastuff = parser.get('URL_Stuff', 'extrastuff')
			ipaddressterm = parser.get('Search_Terms', 'ipaddressterm')
			usernameterm = parser.get('Search_Terms', 'usernameterm')
			delineatorterm = parser.get('Search_Terms', 'delineatorterm')
			userdomain = parser.get('UID_Settings', 'userdomain')
			timeout = parser.get('UID_Settings', 'timeout')			
			#########################################################################
			###Ask questions to the console for editing the .conf file settings
			#########################################################################
			print "\n\n\n\n\n\n****************Please enter values for the different settings in the radiuid.conf file****************\n"
			newlogfile = self.imum.change_setting(logfile, 'Enter full path to the new RadiUID Log File')
			print "\n"
			newradiuslogpath = self.imum.change_setting(radiuslogpath, 'Enter path to the FreeRADIUS Accounting Logs')
			print "\n"
			newhostname = self.imum.change_setting(hostname, 'Enter IP address or hostname for target Palo Alto firewall')
			print "\n"
			newpanosversion = self.imum.change_setting(panosversion, 'Enter PAN-OS software version on target firewall (only PAN-OS 6 and 7 are currently supported)')
			print "\n"
			newusername = self.imum.change_setting(username, 'Enter administrative username for Palo Alto firewall')
			print "\n"
			newpassword = self.imum.change_setting(password, 'Enter administrative password for Palo Alto firewall (entered text will be shown in the clear)')
			while newpassword.find("%") != -1:
				newpassword = self.imum.change_setting(password, 'The "%" sign is not allowed in the password. Please enter a password without it')
			print "\n"
			newuserdomain = self.imum.change_setting(userdomain, 'Enter the user domain to be prefixed to User-IDs')
			print "\n"
			newtimeout = self.imum.change_setting(timeout, 'Enter timeout period for pushed UIDs (in minutes)')
			#########################################################################
			###Pushing settings to .conf file with the code below
			#########################################################################
			print "\n\n\n\n\n\n****************Applying entered settings into the radiuid.conf file...****************\n"
			new_config_file_data = config_file_data
			self.ui.progress('Applying:', 1)
			new_config_file_data = self.imum.apply_setting(new_config_file_data, 'logfile', logfile, newlogfile)
			new_config_file_data = self.imum.apply_setting(new_config_file_data, 'radiuslogpath', radiuslogpath, newradiuslogpath)
			new_config_file_data = self.imum.apply_setting(new_config_file_data, 'hostname', hostname, newhostname)
			new_config_file_data = self.imum.apply_setting(new_config_file_data, 'panosversion', panosversion, newpanosversion)
			new_config_file_data = self.imum.apply_setting(new_config_file_data, 'username', username, newusername)
			new_config_file_data = self.imum.apply_setting(new_config_file_data, 'password', password, newpassword)
			new_config_file_data = self.imum.apply_setting(new_config_file_data, 'userdomain', userdomain, newuserdomain)
			new_config_file_data = self.imum.apply_setting(new_config_file_data, 'timeout', timeout, newtimeout)
			self.filemgmt.write_file(etcconfigfile, new_config_file_data)
			newlogfiledir = self.filemgmt.strip_filepath(newlogfile)[0][0]
			os.system('mkdir -p ' + newlogfiledir)
			print "\n\n****************Starting/Restarting the RadiUID service...****************\n"
			self.imum.restart_service('radiuid')
			radiuidrunning = self.imum.check_service_running('radiuid')
			if radiuidrunning == "yes":
				print self.ui.color("***** RadiUID successfully started up!!!", self.ui.green)
			raw_input(self.ui.color(">>>>> Hit ENTER to continue...\n\n>>>>>", self.ui.cyan))
			if radiuidrunning == "no":
				print self.ui.color("***** Something went wrong. Looks like the installation or startup failed... ", self.ui.red)
				print self.ui.color("***** Please make sure you are installing RadiUID on a support platform", self.ui.red)
				print self.ui.color("***** You can manually edit the RadiUID config file by entering 'radiuid edit config' in the CLI", self.ui.red)
				raw_input(self.ui.color("Hit ENTER to quit the program...\n\n>>>>>", self.ui.cyan))
				quit()
		else:
			print "~~~ OK... Leaving the .conf file alone"
		#########################################################################
		###Make changes to FreeRADIUS config file
		#########################################################################
		print "\n\n\n\n\n\n****************Let's make some changes to the FreeRADIUS client config file****************\n"
		editfreeradius = self.ui.yesorno("Do you want to make changes to FreeRADIUS by adding some IP blocks for accepted accounting clients?")
		if editfreeradius == "yes":
			freeradiusedits = self.imum.freeradius_create_changes()
			self.imum.freeradius_editor(freeradiusedits)
		#########################################################################
		###Trailer/Goodbye
		#########################################################################
		print "\n\n\n\n\n\n***** Thank you for using the RadiUID installer/management utility"
		raw_input(self.ui.color(">>>>> Hit ENTER to see the tail of the RadiUID log file before you exit the utility\n\n>>>>>", self.ui.cyan))
		##### Read in logfile path from found config file #####
		configfile = self.filemgmt.find_config("quiet")
		parser = ConfigParser.SafeConfigParser()
		parser.read(configfile)
		f = open(configfile, 'r')
		config_file_data = f.read()
		f.close()
		logfile = parser.get('Paths_and_Files', 'logfile')
		#######################################################
		print "\n\n############################## LAST 50 LINES FROM " + logfile + "##############################"
		print "########################################################################################################"
		os.system("tail -n 50 " + logfile)
		print "########################################################################################################"
		print "########################################################################################################"
		print "\n\n\n\n***** Looks like we are all done here...\n"
		raw_input(
			self.ui.color(">>>>> Hit ENTER to exit the Install/Maintenance Utility\n\n>>>>>", self.ui.cyan))
		quit()






#########################################################################
#################### RADIUID COMMAND LINE INTERPRETER ###################
#########################################################################
####### Contains the code which interprets arguments to the shell #######
#######       and runs the proper part of code in the source      #######
#########################################################################
class command_line_interpreter(object):
	def __init__(self):
		##### Instantiate external object dependencies #####
		self.ui = user_interface()
		self.radiuid = radiuid_main_process()
		self.imu = installer_maintenance_utility()
		self.imum = imu_methods()
		self.filemgmt = file_management()
		####################################################
	##### Create str sentence out of list seperated by spaces and lowercase everything #####
	##### Used for recognizing arguments when running RadiUID from the CLI #####
	def cat_list(self, listname):
		result = ""
		counter = 0
		#listlen = len(listname)
		for word in listname:
			result = result + listname[counter].lower() + " "
			counter = counter + 1
		result = result[:len(result) - 1:]
		return result
	######################### RadiUID Command Interpreter #############################
	def interpreter(self):
		arguments = self.cat_list(sys.argv[1:])
		######################### RUN #############################
		if arguments == "run":
			self.radiuid.looper()
		######################### INSTALL #############################
		elif arguments == "install":
			self.filemgmt.logwriter("cli-noconsole", "##### COMMAND '" + arguments + "' ISSUED FROM CLI BY USER '" + self.imum.currentuser()+ "' #####")
			print "\n\n\n"
			self.imu.im_utility()
		######################### SHOW #############################
		elif arguments == "show" or arguments == "show ?":
			print "\n - show log         |     Show the RadiUID log file"
			print " - show run         |     Show the RadiUID config file"
			print " - show config      |     Show the RadiUID config file"
			print " - show clients     |     Show the FreeRADIUS client config file"
			print " - show status      |     Show the RadiUID and FreeRADIUS service statuses"
		elif arguments == "show log":
			self.filemgmt.logwriter("cli", "##### COMMAND '" + arguments + "' ISSUED FROM CLI BY USER '" + self.imum.currentuser()+ "' #####")
			self.filemgmt.get_logfile()
			configfile = self.filemgmt.find_config("quiet")
			header = "########################## OUTPUT FROM FILE " + logfile + " ##########################"
			print self.ui.color(header, self.ui.magenta)
			print self.ui.color("#" * len(header), self.ui.magenta)
			os.system("more " + logfile)
			print self.ui.color("#" * len(header), self.ui.magenta)
			print self.ui.color("#" * len(header), self.ui.magenta)
		elif arguments == "show run":
			self.filemgmt.logwriter("cli", "##### COMMAND '" + arguments + "' ISSUED FROM CLI BY USER '" + self.imum.currentuser()+ "' #####")
			self.filemgmt.get_logfile()
			configfile = self.filemgmt.find_config("quiet")
			header = "########################## OUTPUT FROM FILE " + configfile + " ##########################"
			print self.ui.color(header, self.ui.magenta)
			print self.ui.color("#" * len(header), self.ui.magenta)
			os.system("more " + configfile)
			print self.ui.color("#" * len(header), self.ui.magenta)
			print self.ui.color("#" * len(header), self.ui.magenta)
		elif arguments == "show config":
			self.filemgmt.logwriter("cli", "##### COMMAND '" + arguments + "' ISSUED FROM CLI BY USER '" + self.imum.currentuser()+ "' #####")
			self.filemgmt.get_logfile()
			configfile = self.filemgmt.find_config("quiet")
			header = "########################## OUTPUT FROM FILE " + configfile + " ##########################"
			print self.ui.color(header, self.ui.magenta)
			print self.ui.color("#" * len(header), self.ui.magenta)
			os.system("more " + configfile)
			print self.ui.color("#" * len(header), self.ui.magenta)
			print self.ui.color("#" * len(header), self.ui.magenta)
		elif arguments == "show clients":
			self.filemgmt.logwriter("cli", "##### COMMAND '" + arguments + "' ISSUED FROM CLI BY USER '" + self.imum.currentuser()+ "' #####")
			self.filemgmt.get_logfile()
			configfile = self.filemgmt.find_config("quiet")
			header = "########################## OUTPUT FROM FILE /etc/raddb/clients.conf ##########################"
			print self.ui.color(header, self.ui.magenta)
			print self.ui.color("#" * len(header), self.ui.magenta)
			os.system("more /etc/raddb/clients.conf")
			print self.ui.color("#" * len(header), self.ui.magenta)
			print self.ui.color("#" * len(header), self.ui.magenta)
		elif arguments == "show status":
			self.filemgmt.logwriter("cli", "##### COMMAND '" + arguments + "' ISSUED FROM CLI BY USER '" + self.imum.currentuser()+ "' #####")
			header = "########################## OUTPUT FROM COMMAND: 'systemctl status radiuid' ##########################"
			print self.ui.color(header, self.ui.magenta)
			print self.ui.color("#" * len(header), self.ui.magenta)
			os.system("systemctl status radiuid")
			print self.ui.color("#" * len(header), self.ui.magenta)
			print self.ui.color("#" * len(header), self.ui.magenta)
			serviceinstalled = self.imum.check_service_installed("radiuid")
			if serviceinstalled == "no":
				print self.ui.color("\n\n********** RADIUID IS NOT INSTALLED YET **********\n\n", self.ui.yellow)
			elif serviceinstalled == "yes":
				checkservice = self.imum.check_service_running("radiuid")
				if checkservice == "yes":
					print self.ui.color("\n\n********** RADIUID IS CURRENTLY RUNNING **********\n\n", self.ui.green)
				elif checkservice == "no":
					print self.ui.color("\n\n********** RADIUID IS CURRENTLY NOT RUNNING **********\n\n", self.ui.yellow)
			header = "########################## OUTPUT FROM COMMAND: 'systemctl status radiusd' ##########################"
			print self.ui.color(header, self.ui.magenta)
			print self.ui.color("#" * len(header), self.ui.magenta)
			os.system("systemctl status radiusd")
			print self.ui.color("#" * len(header), self.ui.magenta)
			print self.ui.color("#" * len(header), self.ui.magenta)
			serviceinstalled = self.imum.check_service_installed("radiusd")
			if serviceinstalled == "no":
				print self.ui.color("\n\n********** FREERADIUS IS NOT INSTALLED YET **********\n\n", self.ui.yellow)
			elif serviceinstalled == "yes":
				checkservice = self.imum.check_service_running("radiusd")
				if checkservice == "yes":
					print self.ui.color("\n\n********** FREERADIUS IS CURRENTLY RUNNING **********\n\n", self.ui.green)
				elif checkservice == "no":
					print self.ui.color("\n\n********** FREERADIUS IS CURRENTLY NOT RUNNING **********\n\n", self.ui.yellow)
		######################### TAIL #############################
		elif arguments == "tail" or arguments == "tail ?":
			print "\n - tail log         |     Watch the RadiUID log file in real time\n"
		elif arguments == "tail log":
			self.filemgmt.logwriter("cli", "##### COMMAND '" + arguments + "' ISSUED FROM CLI BY USER '" + self.imum.currentuser()+ "' #####")
			self.filemgmt.get_logfile()
			configfile = self.filemgmt.find_config("quiet")
			header = "########################## OUTPUT FROM FILE " + logfile + " ##########################"
			print self.ui.color(header, self.ui.magenta)
			print self.ui.color("#" * len(header), self.ui.magenta)
			os.system("tail -fn 25 " + logfile)
			print self.ui.color("#" * len(header), self.ui.magenta)
			print self.ui.color("#" * len(header), self.ui.magenta)
		######################### CLEAR #############################
		elif arguments == "clear" or arguments == "clear ?":
			print "\n - clear log         |     Delete the content in the log file\n"
		elif arguments == "clear log":
			self.filemgmt.get_logfile()
			configfile = self.filemgmt.find_config("quiet")
			print self.ui.color("********************* You are about to clear out the RadiUID log file... (" + logfile + ") ********************", self.ui.yellow)
			raw_input("Hit CTRL-C to quit. Hit ENTER to continue\n>>>>>")
			os.system("rm -f "+ logfile)
			self.filemgmt.write_file(logfile, "***********Logfile cleared via RadiUID command by " + self.imum.currentuser() + "***********\n")
			print self.ui.color("********************* Cleared logfile: " + logfile + " ********************", self.ui.yellow)
		######################### EDIT #############################
		elif arguments == "edit" or arguments == "edit ?":
			print "\n - edit config      |     Edit the RadiUID config file"
			print " - edit clients     |     Edit list of client IPs for FreeRADIUS\n"
		elif arguments == "edit config":
			self.filemgmt.logwriter("cli", "##### COMMAND '" + arguments + "' ISSUED FROM CLI BY USER '" + self.imum.currentuser()+ "' #####")
			self.filemgmt.get_logfile()
			configfile = self.filemgmt.find_config("quiet")
			print self.ui.color("****************** You are about to edit the RadiUID config file in VI ******************", self.ui.yellow)
			print self.ui.color("********************* Confirm that you know how to use the VI editor ********************", self.ui.yellow)
			raw_input("Hit CTRL-C to quit. Hit ENTER to continue\n>>>>>")
			os.system("vi " + configfile)
		elif arguments == "edit clients":
			self.filemgmt.logwriter("cli", "##### COMMAND '" + arguments + "' ISSUED FROM CLI BY USER '" + self.imum.currentuser()+ "' #####")
			print self.ui.color("****************** You are about to edit the FreeRADIUS client file in VI ******************", self.ui.yellow)
			print self.ui.color("*********************** Confirm that you know how to use the VI editor ********************", self.ui.yellow)
			raw_input("Hit CTRL-C to quit. Hit ENTER to continue\n>>>>>")
			os.system("vi /etc/raddb/clients.conf")
		######################### RADIUID SERVICE CONTROL #############################
		elif arguments == "start" or arguments == "start ?":
			print "\n - start radiuid       |     Start the RadiUID system service"
			print " - start freeradius    |     Start the FreeRADIUS system service"
			print " - start all           |     Start the RadiUID and FreeRADIUS system services"
		elif arguments == "stop" or arguments == "stop ?":
			print "\n - stop radiuid        |     Stop the RadiUID system service"
			print " - stop freeradius     |     Stop the FreeRADIUS system service"
			print " - stop all            |     Stop the RadiUID and FreeRADIUS system services"
		elif arguments == "restart" or arguments == "restart ?":
			print "\n - restart radiuid     |     Restart the RadiUID system service"
			print " - restart freeradius  |     Restart the FreeRADIUS system service"
			print " - restart all         |     Restart the RadiUID and FreeRADIUS system services"
		elif arguments == "start radiuid":
			self.filemgmt.logwriter("cli", "##### COMMAND '" + arguments + "' ISSUED FROM CLI BY USER '" + self.imum.currentuser()+ "' #####")
			os.system("systemctl start radiuid")
			os.system("systemctl status radiuid")
			checkservice = self.imum.check_service_running("radiuid")
			if checkservice == "yes":
				print self.ui.color("\n\n********** RADIUID SUCCESSFULLY STARTED UP! **********\n\n", self.ui.green)
			elif checkservice == "no":
				print self.ui.color("\n\n********** RADIUID STARTUP UNSUCCESSFUL. SOMETHING MUST BE WRONG... **********\n\n", red)
		elif arguments == "stop radiuid":
			self.filemgmt.logwriter("cli", "##### COMMAND '" + arguments + "' ISSUED FROM CLI BY USER '" + self.imum.currentuser()+ "' #####")
			header = "########################## CURRENT RADIUID SERVICE STATUS ##########################"
			print self.ui.color(header, self.ui.magenta)
			print self.ui.color("#" * len(header), self.ui.magenta)
			os.system("systemctl status radiuid")
			print self.ui.color("\n\n***** ARE YOU SURE YOU WANT TO STOP IT?", self.ui.yellow)
			raw_input(self.ui.color("\n\nHit CTRL-C to quit. Hit ENTER to continue\n>>>>>", self.ui.cyan))
			os.system("systemctl stop radiuid")
			os.system("systemctl status radiuid")
			print self.ui.color("\n\n********** RADIUID STOPPED **********\n\n", self.ui.yellow)
		elif arguments == "restart radiuid":
			self.filemgmt.logwriter("cli", "##### COMMAND '" + arguments + "' ISSUED FROM CLI BY USER '" + self.imum.currentuser()+ "' #####")
			header = "########################## CURRENT RADIUID SERVICE STATUS ##########################"
			print self.ui.color(header, self.ui.magenta)
			print self.ui.color("#" * len(header), self.ui.magenta)
			os.system("systemctl status radiuid")
			print self.ui.color("\n\n***** ARE YOU SURE YOU WANT TO RESTART IT?", self.ui.yellow)
			raw_input(self.ui.color("\n\nHit CTRL-C to quit. Hit ENTER to continue\n>>>>>", self.ui.cyan))
			os.system("systemctl stop radiuid")
			os.system("systemctl status radiuid")
			print self.ui.color("\n\n********** RADIUID STOPPED **********\n\n", self.ui.yellow)
			self.ui.progress("Preparing to Start Up:", 2)
			print "\n\n\n"
			os.system("systemctl start radiuid")
			os.system("systemctl status radiuid")
			checkservice = self.imum.check_service_running("radiuid")
			if checkservice == "yes":
				print self.ui.color("\n\n********** RADIUID SUCCESSFULLY RESTARTED! **********\n\n", self.ui.green)
			elif checkservice == "no":
				print self.ui.color("\n\n********** RADIUID STARTUP UNSUCCESSFUL. SOMETHING MUST BE WRONG... **********\n\n", red)
		######################### FREERADIUS SERVICE CONTROL #############################
		elif arguments == "start freeradius":
			self.filemgmt.logwriter("cli", "##### COMMAND '" + arguments + "' ISSUED FROM CLI BY USER '" + self.imum.currentuser()+ "' #####")
			os.system("systemctl start radiusd")
			os.system("systemctl status radiusd")
			checkservice = self.imum.check_service_running("radiusd")
			if checkservice == "yes":
				print self.ui.color("\n\n********** FREERADIUS SUCCESSFULLY STARTED UP! **********\n\n", self.ui.green)
			elif checkservice == "no":
				print self.ui.color("\n\n********** FREERADIUS STARTUP UNSUCCESSFUL. SOMETHING MUST BE WRONG... **********\n\n", red)
		elif arguments == "stop freeradius":
			self.filemgmt.logwriter("cli", "##### COMMAND '" + arguments + "' ISSUED FROM CLI BY USER '" + self.imum.currentuser()+ "' #####")
			header = "########################## CURRENT FREERADIUS SERVICE STATUS ##########################"
			print self.ui.color(header, self.ui.magenta)
			print self.ui.color("#" * len(header), self.ui.magenta)
			os.system("systemctl status radiusd")
			print self.ui.color("\n\n***** ARE YOU SURE YOU WANT TO STOP IT?", self.ui.yellow)
			raw_input(self.ui.color("\n\nHit CTRL-C to quit. Hit ENTER to continue\n>>>>>", self.ui.cyan))
			os.system("systemctl stop radiusd")
			os.system("systemctl status radiusd")
			print self.ui.color("\n\n********** FREERADIUS STOPPED **********\n\n", self.ui.yellow)
		elif arguments == "restart freeradius":
			self.filemgmt.logwriter("cli", "##### COMMAND '" + arguments + "' ISSUED FROM CLI BY USER '" + self.imum.currentuser()+ "' #####")
			header = "########################## CURRENT FREERADIUS SERVICE STATUS ##########################"
			print self.ui.color(header, self.ui.magenta)
			print self.ui.color("#" * len(header), self.ui.magenta)
			os.system("systemctl status radiusd")
			print self.ui.color("\n\n***** ARE YOU SURE YOU WANT TO RESTART IT?", self.ui.yellow)
			raw_input(self.ui.color("\n\nHit CTRL-C to quit. Hit ENTER to continue\n>>>>>", self.ui.cyan))
			os.system("systemctl stop radiusd")
			os.system("systemctl status radiusd")
			print self.ui.color("\n\n********** FREERADIUS STOPPED **********\n\n", self.ui.yellow)
			self.ui.progress("Preparing to Start Up:", 2)
			print "\n\n\n"
			os.system("systemctl start radiusd")
			os.system("systemctl status radiusd")
			checkservice = self.imum.check_service_running("radiusd")
			if checkservice == "yes":
				print self.ui.color("\n\n********** FREERADIUS SUCCESSFULLY RESTARTED! **********\n\n", self.ui.green)
			elif checkservice == "no":
				print self.ui.color("\n\n********** FREERADIUS STARTUP UNSUCCESSFUL. SOMETHING MUST BE WRONG... **********\n\n", red)
		######################### COMBINED SERVICE CONTROL #############################
		elif arguments == "start all":
			self.filemgmt.logwriter("cli", "##### COMMAND '" + arguments + "' ISSUED FROM CLI BY USER '" + self.imum.currentuser()+ "' #####")
			os.system("systemctl start radiusd")
			os.system("systemctl status radiusd")
			checkservice = self.imum.check_service_running("radiusd")
			if checkservice == "yes":
				print self.ui.color("\n\n********** FREERADIUS SUCCESSFULLY STARTED UP! **********\n\n", self.ui.green)
			elif checkservice == "no":
				print self.ui.color("\n\n********** FREERADIUS STARTUP UNSUCCESSFUL. SOMETHING MUST BE WRONG... **********\n\n", red)
			print "\n\n\n"
			os.system("systemctl start radiuid")
			os.system("systemctl status radiuid")
			checkservice = self.imum.check_service_running("radiuid")
			if checkservice == "yes":
				print self.ui.color("\n\n********** RADIUID SUCCESSFULLY STARTED UP! **********\n\n", self.ui.green)
			elif checkservice == "no":
				print self.ui.color("\n\n********** RADIUID STARTUP UNSUCCESSFUL. SOMETHING MUST BE WRONG... **********\n\n", red)
		elif arguments == "stop all":
			self.filemgmt.logwriter("cli", "##### COMMAND '" + arguments + "' ISSUED FROM CLI BY USER '" + self.imum.currentuser()+ "' #####")
			header = "########################## CURRENT RADIUID SERVICE STATUS ##########################"
			print self.ui.color(header, self.ui.magenta)
			print self.ui.color("#" * len(header), self.ui.magenta)
			os.system("systemctl status radiuid")
			header = "########################## CURRENT FREERADIUS SERVICE STATUS ##########################"
			print self.ui.color(header, self.ui.magenta)
			print self.ui.color("#" * len(header), self.ui.magenta)
			os.system("systemctl status radiusd")
			print self.ui.color("\n\n***** ARE YOU SURE YOU WANT TO ALL SERVICES?", self.ui.yellow)
			raw_input(self.ui.color("\n\nHit CTRL-C to quit. Hit ENTER to continue\n>>>>>", self.ui.cyan))
			os.system("systemctl stop radiuid")
			os.system("systemctl status radiuid")
			print self.ui.color("\n\n********** RADIUID STOPPED **********\n\n", self.ui.yellow)
			print "\n\n\n"
			os.system("systemctl stop radiusd")
			os.system("systemctl status radiusd")
			print self.ui.color("\n\n********** FREERADIUS STOPPED **********\n\n", self.ui.yellow)
		elif arguments == "restart all":
			self.filemgmt.logwriter("cli", "##### COMMAND '" + arguments + "' ISSUED FROM CLI BY USER '" + self.imum.currentuser()+ "' #####")
			header = "########################## CURRENT RADIUID SERVICE STATUS ##########################"
			print self.ui.color(header, self.ui.magenta)
			print self.ui.color("#" * len(header), self.ui.magenta)
			os.system("systemctl status radiuid")
			header = "########################## CURRENT FREERADIUS SERVICE STATUS ##########################"
			print self.ui.color(header, self.ui.magenta)
			print self.ui.color("#" * len(header), self.ui.magenta)
			os.system("systemctl status radiusd")
			print self.ui.color("\n\n***** ARE YOU SURE YOU WANT TO RESTART SERVICES?", self.ui.yellow)
			raw_input(self.ui.color("\n\nHit CTRL-C to quit. Hit ENTER to continue\n>>>>>", self.ui.cyan))
			os.system("systemctl stop radiuid")
			os.system("systemctl status radiuid")
			print self.ui.color("\n\n********** RADIUID STOPPED **********\n\n", self.ui.yellow)
			self.ui.progress("Preparing to Start Up:", 2)
			print "\n\n\n"
			os.system("systemctl start radiuid")
			os.system("systemctl status radiuid")
			checkservice = self.imum.check_service_running("radiuid")
			if checkservice == "yes":
				print self.ui.color("\n\n********** RADIUID SUCCESSFULLY RESTARTED! **********\n\n", self.ui.green)
			elif checkservice == "no":
				print self.ui.color("\n\n********** RADIUID STARTUP UNSUCCESSFUL. SOMETHING MUST BE WRONG... **********\n\n", red)
			os.system("systemctl stop radiusd")
			os.system("systemctl status radiusd")
			print self.ui.color("\n\n********** FREERADIUS STOPPED **********\n\n", self.ui.yellow)
			self.ui.progress("Preparing to Start Up:", 2)
			print "\n\n\n"
			os.system("systemctl start radiusd")
			os.system("systemctl status radiusd")
			checkservice = self.imum.check_service_running("radiusd")
			if checkservice == "yes":
				print self.ui.color("\n\n********** FREERADIUS SUCCESSFULLY RESTARTED! **********\n\n", self.ui.green)
			elif checkservice == "no":
				print self.ui.color("\n\n********** FREERADIUS STARTUP UNSUCCESSFUL. SOMETHING MUST BE WRONG... **********\n\n", red)
		######################### VERSION #############################
		elif arguments == "version":
			self.filemgmt.logwriter("cli", "##### COMMAND '" + arguments + "' ISSUED FROM CLI BY USER '" + self.imum.currentuser()+ "' #####")
			header = "########################## CURRENT RADIUID AND FREERADIUS VERSIONS ##########################"
			print self.ui.color(header, self.ui.magenta)
			print "------------------------------------------ RADIUID -------------------------------------------"
			print "***** Currently running RadiUID "+ self.ui.color(version, self.ui.green) + " *****"
			print "----------------------------------------------------------------------------------------------\n"
			print "----------------------------------------- FREERADIUS -----------------------------------------"
			os.system("radiusd -v | grep ersion")
			print "----------------------------------------------------------------------------------------------\n"
			print self.ui.color("#" * len(header), self.ui.magenta)
			print self.ui.color("#" * len(header), self.ui.magenta)
		######################### GUIDE #############################
		else:
			print self.ui.color("\n\n\n########################## Below are the supported RadiUID Commands: ##########################", self.ui.magenta)
			print self.ui.color("###############################################################################################\n\n", self.ui.magenta)
			print "----------------------------------------------------------------------------------------------"
			print " - run                 |     Run the RadiUID main program in shell mode begin pushing User-ID information"
			print "----------------------------------------------------------------------------------------------\n"
			print " - install             |     Run the RadiUID Install/Maintenance Utility"
			print "----------------------------------------------------------------------------------------------\n"
			print " - show log            |     Show the RadiUID log file"
			print " - show run            |     Show the RadiUID config file"
			print " - show config         |     Show the RadiUID config file"
			print " - show clients        |     Show the FreeRADIUS client config file"
			print " - show status         |     Show the RadiUID and FreeRADIUS service statuses"
			print "----------------------------------------------------------------------------------------------\n"
			print " - tail log            |     Watch the RadiUID log file in real time"
			print "----------------------------------------------------------------------------------------------\n"
			print " - clear log           |     Delete the content in the log file"
			print "----------------------------------------------------------------------------------------------\n"
			print " - edit config         |     Edit the RadiUID config file"
			print " - edit clients        |     Edit list of client IPs for FreeRADIUS"
			print "----------------------------------------------------------------------------------------------\n"
			print " - start radiuid       |     Start the RadiUID system service"
			print " - stop radiuid        |     Stop the RadiUID system service"
			print " - restart radiuid     |     Restart the RadiUID system service"
			print "----------------------------------------------------------------------------------------------\n"
			print " - start freeradius    |     Start the FreeRADIUS system service"
			print " - stop freeradius     |     Stop the FreeRADIUS system service"
			print " - restart freeradius  |     Restart the FreeRADIUS system service"
			print "----------------------------------------------------------------------------------------------\n"
			print " - start all           |     Start the RadiUID and FreeRADIUS system services"
			print " - stop all            |     Stop the RadiUID and FreeRADIUS system services"
			print " - restart all         |     Restart the RadiUID and FreeRADIUS system services"
			print "----------------------------------------------------------------------------------------------\n"
			print " - version             |     Show the current version of RadiUID and FreeRADIUS"
			print "----------------------------------------------------------------------------------------------\n\n\n"


if __name__ == "__main__":
	cli = command_line_interpreter()
	cli.interpreter()
