#!/usr/bin/python
"""
import the twisted modules for executing rpc calls and also to
implement the server
"""
from twisted.web import xmlrpc, server
"""
reactor from the twisted library starts the server with a published
object and listens on a given port.
"""
from twisted.internet import reactor
from sqlalchemy.orm import sessionmaker,scoped_session
from xml.etree import ElementTree as et
from time import strftime
from pysqlite2 import dbapi2 as sqlite
import datetime
import os,sys
import getopt
import dbconnect
import rpc_organisation
import rpc_groups
import rpc_account
import rpc_transaction
import rpc_data
import rpc_user
import rpc_reports
import rpc_getaccountsbyrule
#import rpc_inventory
from sqlalchemy.orm import join
from decimal import *
from sqlalchemy import or_
from modules import blankspace
#note that all the functions to be accessed by the client must have the xmlrpc_ prefix.
class gnukhata(xmlrpc.XMLRPC): 
	

	def __init__(self):
		xmlrpc.XMLRPC.__init__(self)

	
	
	def xmlrpc_getOrganisationNames(self): 
		'''
		def xmlrpc_getOrganisationNames :

		Purpose: This function is used to return the list of
			organsations found in gnukhata.xml located at
			/opt/gkAakash/. Returns a list of
			organisations already present in the file
		'''
	
		orgs = dbconnect.getOrgList() #calling the function for getting list of organisation nodes.
		
		orgnames = [] #initialising an empty list for organisation names
		for org in orgs:
			#print "we r in getOrganisation"
			orgname=org.find("orgname")
			if orgname.text not in orgnames:
				orgnames.append(orgname.text)
		print orgnames
		return orgnames
	
	def xmlrpc_deleteOrganisation(self,queryParams): 
		'''
		def xmlrpc_deleteOrganisationName :

		Purpose: This function is used delete organisation
		         from existing organisations
			organsations found in gnukhata.xml located at
			/opt/gkAakash/. 
			also delete database details of respective
			organisation
			
		'''
		tree = et.parse("/opt/gkAakash/gnukhata.xml") # parsing gnukhata.xml file
		root = tree.getroot() # getting root node.
		orgs = root.getchildren() 
		for organisation in orgs:
		
			orgname = organisation.find("orgname").text
			financialyear_from = organisation.find("financial_year_from").text
			financialyear_to = organisation.find("financial_year_to").text
			dbname = organisation.find("dbname").text
			databasename = dbname
			
			if orgname == queryParams[0] and financialyear_from == queryParams[1] and financialyear_to == queryParams[2]:
				print "we r in"
				root.remove(organisation)
				tree.write("/opt/gkAakash/gnukhata.xml")
				os.system("rm /opt/gkAakash/db/"+databasename)
			return True	

	def xmlrpc_getFinancialYear(self,arg_orgName):
		"""
		purpose: This function will return a list of financial
		years for the given organisation.  Arguements,
		organisation name of type string.  returns, list of
		financial years in the format dd-mm-yyyy
		"""
		#get the list of organisations from the /etc/gnukhata.xml file.
		#we will call the getOrgList function to get the nodes.
		orgs = dbconnect.getOrgList()
		
		#Initialising an empty list to be filled with financial years 
		financialyearlist = []
		for org in orgs:
			orgname = org.find("orgname")
			if orgname.text == arg_orgName:
				financialyear_from = org.find("financial_year_from")
				financialyear_to = org.find("financial_year_to")
				from_and_to = [financialyear_from.text, financialyear_to.text]
				financialyearlist.append(from_and_to)
			
		#print financialyearlist
		return financialyearlist
		
	def xmlrpc_getConnection(self,queryParams):
		'''
		def xmlrpc_getConnection: purpose
			This function is used to return the client_id found in dbconnect.py 
			Returns the client_id
		Input parameters : [organisation name]
		'''
		#print queryParams
		self.client_id=dbconnect.getConnection(queryParams)
		print "getConnection method will give you client_id for existing organisation"
		return self.client_id

	
	def xmlrpc_closeConnection(self,client_id):
		print('closing connection'+str(client_id))
		dbconnect.engines[client_id].dispose()
		del dbconnect.engines[client_id]
		return True
		
		
	def xmlrpc_Deploy(self,queryParams):
		'''
		def xmlrpc_Deploy 

		Purpose: This function deploys a database instance for
			an organisation for a given financial year.
			The expected parameters are:
			queryParams[organisation name,From date,to
			date,organisation type] The function will
			generate the database name based on the
			organisation name provided The name of the
			database is a combination of, First character
			of organisation name, * time stap as
			dd-mm-yyyy-hh-MM-ss-ms An entry will be made
			in the xml file for the currosponding
			organisation.
		'''
		print queryParams
		queryParams = blankspace.remove_whitespaces(queryParams)
		print queryParams
		gnukhataconf=et.parse("/opt/gkAakash/gnukhata.xml")
		gnukhataroot = gnukhataconf.getroot()	
		org = et.SubElement(gnukhataroot,"organisation") #creating an organisation tag
		org_name = et.SubElement(org,"orgname")
		#print queryParams
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
		
		#creating database name for organisation		
		org_db_name=name_of_org[0:1]
		time=datetime.datetime.now()
		str_time=str(time.microsecond)	
		new_microsecond=str_time[0:2]		
		result_dbname=org_db_name + str(time.year) + str(time.month) + str(time.day) + str(time.hour)\
		 + str(time.minute) + str(time.second) + new_microsecond
		#print result_dbname		
		dbname.text = result_dbname #assigning created database name value in dbname tag text of gnukhata.xml
		#print result_dbname 
		gnukhataconf.write("/opt/gkAakash/gnukhata.xml")
		try:
			conn = sqlite.connect("/opt/gkAakash/db/"+result_dbname)
            		cur = conn.cursor()
            		conn.commit()
            		cur.close()
            		conn.close()
            	except:
            		print "role already exists"


		self.client_id = dbconnect.getConnection([name_of_org,db_from_date,db_to_date])
		#print "In deploy dbconnect.getConnection give you client_id"
		#print self.client_id
		try:
			metadata = dbconnect.Base.metadata
			metadata.create_all(dbconnect.engines[self.client_id])
		except:
			print "not work"
		Session = scoped_session(sessionmaker(bind=dbconnect.engines[self.client_id]))
		
		dbconnect.engines[self.client_id].execute(\
			"insert into users(username,userpassword,userrole)\
			values('admin','admin',0);")
			
		dbconnect.engines[self.client_id].execute(\
			"create view view_account as \
			select groups.groupname, account.accountcode, account.accountname, account.subgroupcode\
			from groups, account where groups.groupcode = account.groupcode\
			order by groupname;")
			
		dbconnect.engines[self.client_id].execute(\
			"create view view_voucherbook as \
			select voucher_master.vouchercode,voucher_master.flag,voucher_master.reference,\
			voucher_master.voucherdate,voucher_master.reffdate,voucher_master.vouchertype,account.accountname\
			as account_name,voucher_details.typeflag,voucher_details.amount,\
			voucher_master.narration,voucher_master.projectcode\
			from voucher_master,voucher_details,account as account \
			where voucher_master.vouchercode = voucher_details.vouchercode \
			and voucher_details.accountcode = account.accountcode;")
		dbconnect.engines[self.client_id].execute(\
			"create view view_group_subgroup as \
			select groups.groupcode, groups.groupname,subgroups.subgroupcode,subgroups.subgroupname\
			from groups, subgroups where groups.groupcode = subgroups.groupcode \
			order by groupname;")
		dbconnect.engines[self.client_id].execute(\
			"create view group_subgroup_account as select groups.groupname,\
			subgroups.subgroupname,account.accountcode,account.accountname,account.openingbalance,\
			account.balance \
			from groups join account on (groups.groupcode = account.groupcode)\
			left outer join subgroups\
			on (account.subgroupcode = subgroups.subgroupcode) order by groupname;")
		connection = dbconnect.engines[self.client_id].raw_connection()
		cur = connection.cursor()
		
		if (organisationType == "Profit Making"):

			Session.add_all([\
				dbconnect.Groups('Capital',''),\
				dbconnect.Groups('Current Asset',''),\
				dbconnect.Groups('Current Liability',''),\
				dbconnect.Groups('Direct Income','Income refers to consumption\
		opportunity gained by an entity within a specified time frame.'),\
				dbconnect.Groups('Direct Expense','This are the expenses to be incurred for\
		operating the buisness.'),\
				dbconnect.Groups('Fixed Assets',''),\
				dbconnect.Groups('Indirect Income','Income refers to consumption opportunity\
		gained by an entity within a specified time frame.'),\
				dbconnect.Groups('Indirect Expense','This are the expenses to be incurred\
		for operating the buisness.'),\
				dbconnect.Groups('Investment',''),\
				dbconnect.Groups('Loans(Asset)',''),\
				dbconnect.Groups('Loans(Liability)',''),\
				dbconnect.Groups('Reserves',''),\
				dbconnect.Groups('Miscellaneous Expenses(Asset)','')\
			])
			Session.commit()
		
		else:
			Session.add_all([\
				dbconnect.Groups('Corpus',''),\
				dbconnect.Groups('Current Asset',''),\
				dbconnect.Groups('Current Liability',''),\
				dbconnect.Groups('Direct Income','Income refers to consumption\
		opportunity gained by an entity within a specified time frame.'),\
				dbconnect.Groups('Direct Expense','This are the \
		expenses to be incurred for operating the buisness.'),\
				dbconnect.Groups('Fixed Assets',''),\
				dbconnect.Groups('Indirect Income','Income refers to consumption \
		opportunity gained by an entity within a specified time frame.'),\
				dbconnect.Groups('Indirect Expense','This are the \
		expenses to be incurred for operating the buisness.'),\
				dbconnect.Groups('Investment',''),\
				dbconnect.Groups('Loans(Asset)',''),\
				dbconnect.Groups('Loans(Liability)',''),\
				dbconnect.Groups('Reserves',''),\
				dbconnect.Groups('Miscellaneous Expenses(Asset)','')\
			])
			Session.commit()
		
		Session.add_all([\
			dbconnect.subGroups('2','Bank'),\
			dbconnect.subGroups('2','Cash'),\
			dbconnect.subGroups('2','Inventory'),\
			dbconnect.subGroups('2','Loans & Advance'),\
			dbconnect.subGroups('2','Sundry Debtors'),\
			dbconnect.subGroups('3','Provisions'),
			dbconnect.subGroups('3','Sundry Creditors for Expense'),\
			dbconnect.subGroups('3','Sundry Creditors for Purchase'),\
			dbconnect.subGroups('6','Building'),\
			dbconnect.subGroups('6','Furniture'),\
			dbconnect.subGroups('6','Land'),\
			dbconnect.subGroups('6','Plant & Machinery'),\
			dbconnect.subGroups('9','Investment in Shares & Debentures'),\
			dbconnect.subGroups('9','Investment in Bank Deposits'),\
			dbconnect.subGroups('11','Secured'),\
			dbconnect.subGroups('11','Unsecured')\
		])
		
		
		Session.commit()

		Session.add_all([\
			dbconnect.Flags(None,'mandatory'),\
			dbconnect.Flags(None,'automatic')\
		])
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
organisation = rpc_organisation.organisation()
gnukhata.putSubHandler('organisation',organisation)
transaction=rpc_transaction.transaction()
gnukhata.putSubHandler('transaction',transaction)

data=rpc_data.data()
gnukhata.putSubHandler('data',data)
reports=rpc_reports.reports()
gnukhata.putSubHandler('reports',reports)

user=rpc_user.user()
gnukhata.putSubHandler('user',user)
'''
customizable = rpc_customizable.customizable()
gnukhata.putSubHandler('customizable',customizable)
'''
getaccountsbyrule=rpc_getaccountsbyrule.getaccountsbyrule()
gnukhata.putSubHandler('getaccountsbyrule',getaccountsbyrule)
'''
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
