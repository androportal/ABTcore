#!/usr/bin/python

from twisted.web import xmlrpc, server
from twisted.internet import reactor
from sqlalchemy.orm import sessionmaker,scoped_session
from xml.etree import ElementTree as et
from time import strftime
from pysqlite2 import dbapi2 as sqlite
import datetime
import os,sys
import getopt
import dbconnect
#import rpc_organisation
import rpc_groups
import rpc_account
#import rpc_transaction
import rpc_data
#import rpc_customizable
import rpc_user
#import rpc_reports
#import rpc_getaccountsbyrule
#import rpc_inventory
from sqlalchemy.orm import join
from decimal import *
from sqlalchemy import or_
class gnukhata(xmlrpc.XMLRPC): #note that all the functions to be accessed by the client must have the xmlrpc_ prefix.
	

	def __init__(self):
		xmlrpc.XMLRPC.__init__(self)

	
	
	def xmlrpc_getOrganisationNames(self): 
	'''def xmlrpc_getOrganisationNames :purpose
		This function is used to return the list of organsations found in gnukhata.xml located at 
	   /opt. Returns a list of organisations already present in the file'''
	
		orgs = dbconnect.getOrgList() #calling the function for getting list of organisation nodes.
		orgnames = [] #initialising an empty list for organisation names
		for org in orgs:
			orgname=org.find("orgname")
			if orgname.text not in orgnames:
				orgnames.append(orgname.text)
   		return orgnames

	
	def xmlrpc_getConnection(self,queryParams):
	'''
	def xmlrpc_getConnection: purpose
		This function is used to return the client_id found in dbconnect.py 
		Returns the client_id
	'''
		self.client_id=dbconnect.getConnection(queryParams)
		return self.client_id

	
	
	def xmlrpc_Deploy(self,queryParams):
	'''
	def xmlrpc_Deploy : Purpose
		This function deploys a database instance for an organisation for a given financial year.
		The expected parameters are:
		* organisation name
		* From date
		* to date
		* organisation type (NGO or profit making)
		The function will generate the database name based on the organisation name provided
		The name of the database is a combination of,
		First character of organisation name,
		* time stap as yyyy-mm-dd-hh-MM-ss-ms
		An entry will be made in the xml file for the currosponding organisation.
	'''
		
		gnukhataconf=et.parse("/opt/gnukhata.xml")
		gnukhataroot = gnukhataconf.getroot()	
		org = et.SubElement(gnukhataroot,"organisation") #creating an organisation tag
		org_name = et.SubElement(org,"orgname")
		print queryParams
		# assigning client queryparams values to variables
		name_of_org = queryParams[0] # name of organisation
		db_from_date = queryParams[1]# from date
		db_to_date = queryParams[2] # to date
		organisationType = queryParams[3] # organisation type
		org_name.text = name_of_org #assigning orgnisation name value in orgname tag text of gnukhata.xml
		
		financial_year_from = et.SubElement(org,"financial_year_from") #creating a new tag for financial year from-to	
		financial_year_from.text = db_from_date
		financial_year_to = et.SubElement(org,"financial_year_to")
		financial_year_to.text = db_to_date
		dbname = et.SubElement(org,"dbname") 
		print "welcome"
		#creating database name for organisation		
		org_db_name=name_of_org[0:1]
		time=datetime.datetime.now()
		str_time=str(time.microsecond)	
		new_microsecond=str_time[0:2]		
		result_dbname=org_db_name + str(time.year) + str(time.month) + str(time.day) + str(time.hour) + str(time.minute) + str(time.second) + new_microsecond
		print result_dbname		
		dbname.text = result_dbname #assigning created database name value in dbname tag text of gnukhata.xml
		print result_dbname 
		gnukhataconf.write("/opt/gnukhata.xml")
		try:
			conn = sqlite.connect("/home/ashwini/db/"+result_dbname)
            		cur = conn.cursor()
            		conn.commit()
            		cur.close()
            		conn.close()
            	except:
            		print "role already exists"


		self.client_id = dbconnect.getConnection([name_of_org,db_from_date,db_to_date])
		print self.client_id
		try:
			metadata = dbconnect.Base.metadata
			metadata.create_all(dbconnect.engines[self.client_id])
		except:
			print "not work"
		Session = scoped_session(sessionmaker(bind=dbconnect.engines[self.client_id]))
		dbconnect.engines[self.client_id].execute("insert into users(username,userpassword,userrole) values('admin','admin',0);")
		connection = dbconnect.engines[self.client_id].raw_connection()
		cur = connection.cursor()
		
		Session.add_all([dbconnect.Groups('Corpus',''),dbconnect.Groups('Current Asset',''),dbconnect.Groups('Current Liability',''),dbconnect.Groups('Direct Income','Income refers to consumption opportunity gained by an entity within a specified time frame. Examples for Income are comision,discount received etc'),dbconnect.Groups('Direct Expense','This are the expenses to be incurred for operating the buisness.Examples of expensestrftime pygtks are administrative expense,selling expenses etc.'),dbconnect.Groups('Fixed Assets',''),dbconnect.Groups('Indirect Income','Income refers to consumption opportunity gained by an entity within a specified time frame. Examples for Income are comision,discount received etc'),dbconnect.Groups('Indirect Expense','This are the expenses to be incurred for operating the buisness.Examples of expensestrftime pygtks are administrative expense,selling expenses etc.'),dbconnect.Groups('Investment',''),dbconnect.Groups('Loans(Asset)',''),dbconnect.Groups('Loans(Liability)',''),dbconnect.Groups('Reserves',''),dbconnect.Groups('Miscellaneous Expenses(Asset)','')])
		Session.commit()
		
		Session.add_all([dbconnect.subGroups('2','Bank'),dbconnect.subGroups('2','Cash'),dbconnect.subGroups('2','Inventory'),dbconnect.subGroups('2','Loans & Advance'),dbconnect.subGroups('2','Sundry Debtors'),dbconnect.subGroups('3','Provisions'),dbconnect.subGroups('3','Sundry Creditors for Expense'),dbconnect.subGroups('3','Sundry Creditors for Purchase'),dbconnect.subGroups('6','Building'),dbconnect.subGroups('6','Furniture'),dbconnect.subGroups('6','Land'),dbconnect.subGroups('6','Plant & Machinery'),dbconnect.subGroups('9','Investment in Shares & Debentures'),dbconnect.subGroups('9','Investment in Bank Deposits'),dbconnect.subGroups('11','Secured'),dbconnect.subGroups('11','Unsecured')])
		
		Session.commit()

		Session.add_all([dbconnect.Flags(None,'mandatory'),dbconnect.Flags(None,'automatic')])
		Session.commit()

		print "everything is done"
		Session.close()
		connection.close()
		return True,self.client_id

gnukhata = gnukhata()

groups=rpc_groups.groups()
gnukhata.putSubHandler('groups',groups)
account=rpc_account.account()
gnukhata.putSubHandler('account',account)
'''transaction=rpc_transaction.transaction()
gnukhata.putSubHandler('transaction',transaction)'''
data=rpc_data.data()
gnukhata.putSubHandler('data',data)
'''
reports=rpc_reports.reports()
gnukhata.putSubHandler('reports',reports)'''
user=rpc_user.user()
gnukhata.putSubHandler('user',user)
'''
customizable = rpc_customizable.customizable()
gnukhata.putSubHandler('customizable',customizable)
getaccountsbyrule=rpc_getaccountsbyrule.getaccountsbyrule()
gnukhata.putSubHandler('getaccountsbyrule',getaccountsbyrule)
inventory=rpc_inventory.inventory()
gnukhata.putSubHandler('inventory',inventory)'''


def rungnukhata():
	print "initialising application"
	#the code to daemonise published instance.
	print "starting server"
 	# Daemonizing GNUKhata

	# Accept commandline arguments
	# A workaround for debugging
	def usage():
		print "Usage: %s [-d|--debug] [-h|--help]\n" % (sys.argv[0])
		print "\t-d (--debug)\tStart server in debug mode. Do not fork a daemon."
		print "\t-d (--help)\tShow this help"


	try:
		opts, args = getopt.getopt(sys.argv[1:], "hd", ["help","debug"])
	except getopt.GetoptError:
		usage()
		os._exit(2)

	debug = 0

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			os.exit(0)
		elif opt in ("-d", "--debug"):
			debug = 1

	# Do not fork if we are debug mode
	if debug == 0:
		try:
			pid = os.fork()
		except OSError, e:
			raise Exception, "Could not fork a daemon: %s" % (e.strerror)

		if pid != 0:
			os._exit(0)

		# Prevent it from being orphaned
		os.setsid()
	
		# Change working directory to root
		os.chdir("/")

		# Change umask
		os.umask(0)

		# All prints should be replaced with logging, preferrably into syslog
		# The standard I/O file descriptors are redirected to /dev/null by default.
		if (hasattr(os, "devnull")):
			REDIRECT_TO = os.devnull
		else:
			REDIRECT_TO = "/dev/null"

		# Redirect the standard I/O file descriptors to the specified file.  Since
		# the daemon has no controlling terminal, most daemons redirect stdin,
		# stdout, and stderr to /dev/null.  This is done to prevent side-effects
		# from reads and writes to the standard I/O file descriptors.

		# This call to open is guaranteed to return the lowest file descriptor,
		# which will be 0 (stdin), since it was closed above.
		os.open(REDIRECT_TO, os.O_RDWR)	# standard input (0)

		# Duplicate standard input to standard output and standard error.
		os.dup2(0, 1)			# standard output (1)
		os.dup2(0, 2)			# standard error (2)
	
	#publish the object and make it to listen on the given port through reactor

	reactor.listenTCP(7081, server.Site(gnukhata))
	#start the service by running the reactor.
	reactor.run()
