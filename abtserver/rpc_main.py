#!/usr/bin/python
from twisted.web import xmlrpc, server
from twisted.internet import reactor
from sqlalchemy.orm import sessionmaker,scoped_session
from xml.etree import ElementTree as et
from sqlite3 import dbapi2 as sqlite
import datetime
import os,sys
import getopt
import dbconnect
import rpc_organisation
import rpc_groups
import rpc_account
import rpc_transaction
import rpc_data
import rpc_reports
import rpc_getaccountsbyrule
from sqlalchemy.orm import join
from modules import blankspace

class abt(xmlrpc.XMLRPC): 
	"""
	+ This class is the inherit class of XMLRPC base class
	+ This is the main file which implement the server and publish the object to given port 
	  and execute the xmlrpc functions.
	+ We have used twisted module to implement server and executing xmlrpc calls
	+ also to publish the object and make it to listen on the given port through reactor 
	  and start the service by running the reactor.
	+ It also create database and deploy organisation. 
	+ note that all the functions to be accessed by the client must have the xmlrpc_ prefix.
	+ the client however will not use the prefix to call the functions.
	"""
	def __init__(self):
		xmlrpc.XMLRPC.__init__(self)

	def xmlrpc_getOrganisationNames(self): 
		'''
		* Purpose:
			- function is used to return the list of
		          organsation names found in abt.xml located at /opt/abt/
		        - we have imported ``ElementTree`` for parsing xml file.
		
		* Output: 
		        - returns a list of organisation names already present in the file
		'''
		# calling the function getOrgList for getting list of organisation nodes.
		orgs = dbconnect.getOrgList() 
		# initialising an empty list for organisation names
		orgnames = [] 
		for org in orgs:
			# find orgname tag in abt.xml file
			orgname=org.find("orgname")
			# append the distinct orgname 
			if orgname.text not in orgnames:
				orgnames.append(orgname.text)
		return orgnames
	
	def xmlrpc_deleteOrganisation(self,queryParams): 
		"""
		* Purpose: 
			- This function is used delete organisation from existing 
			  organsations found in abt.xml located at /opt/abt/ 
			- also delete database details of respective organisation
			  from /opt/abt/db/
		  
		* Output: 
			 - Boolean True
		"""
		# parsing abt.xml file
		tree = et.parse("/opt/abt/abt.xml") 
		root = tree.getroot() # getting root node.
		orgs = root.getchildren() # get list children node (orgnisation)
		for organisation in orgs:
		
			orgname = organisation.find("orgname").text
			financialyear_from = organisation.find("financial_year_from").text
			financialyear_to = organisation.find("financial_year_to").text
			dbname = organisation.find("dbname").text
			databasename = dbname
			# Check respective organisation name 
			if (orgname == queryParams[0] 
				and financialyear_from == queryParams[1] 
				and financialyear_to == queryParams[2]):
				
				root.remove(organisation)
				tree.write("/opt/abt/abt.xml")
				os.system("rm /opt/abt/db/"+databasename)
		return True	

	def xmlrpc_getFinancialYear(self,arg_orgName):
		"""
		* purpose: 
			- This function will return a list of financial years for the 
			  given organisation. 
		* Input: 
		 	- [organisationname]
		* Output: 
		 	- returns financialyear list for peritcular organisation
		  	  in the format "dd-mm-yyyy"
		"""
		#get the list of organisations from the /opt/abt/abt.xml file.
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
		
		return financialyearlist
		
	def xmlrpc_getConnection(self,queryParams):
		"""
		* Purpose: 
			- This function is used to return the client_id for sqlite 
			  engine found in ``dbconnect.py``
		* Input: 
		 	- [organisation name]
		* Output: 
			- returns the client_id integer
		"""
		self.client_id=dbconnect.getConnection(queryParams)
		return self.client_id

	
	def xmlrpc_closeConnection(self,client_id):
		"""
		* Purpose: 
			- This function is used close the connetion with sqlite 
			  for client_id
			  
		* Input: 
		 	- client_id
			
		* Output: 
		 	- returns boolean True if conncetion closed
		
		"""
		dbconnect.engines[client_id].dispose()
		del dbconnect.engines[client_id]
		return True
		
		
	def xmlrpc_Deploy(self,queryParams):
		"""
		* Purpose:
			- The function will generate the database name 
			  based on the organisation name and time stap.
			- provided the name of the database is a combination of, 
			  first character of organisation name,time stap as 
			  "dd-mm-yyyy-hh-MM-ss-ms" 
			- An entry will be made in the xml file 
			  for the currosponding organisation.
			- This function deploys a database instance for
			  an organisation for a given financial year.
			- It will call to getConnection and establish the connection 
			  for created database
			- also create the metadata(tables) given in ``dbconnect`` for that organisation
			  using sqlAlchemy.
			- create the ``Views`` for the particular organisation.
			- It add manually ``groupnames`` ad ``subgroups`` to it's corresponding class
			  tables ``Groups`` and ``subGroups``
		   	
		 * Input: 
		 	- [organisation name,From date,todate,organisation_type]
		
		 * Output: 
		 	- returns boolean True and client_id
			
		"""
		queryParams = blankspace.remove_whitespaces(queryParams)
		abtconf=et.parse("/opt/abt/abt.xml")
		abtroot = abtconf.getroot()	
		org = et.SubElement(abtroot,"organisation") #creating an organisation tag
		org_name = et.SubElement(org,"orgname")
		# assigning client queryparams values to variables
		name_of_org = queryParams[0] # name of organisation
		db_from_date = queryParams[1]# from date
		db_to_date = queryParams[2] # to date
		organisationType = queryParams[3] # organisation type
		org_name.text = name_of_org #assigning orgnisation name value in orgname tag text of abt.xml
		financial_year_from = et.SubElement(org,"financial_year_from") #creating a new tag for financial year fromto	
		financial_year_from.text = db_from_date
		financial_year_to = et.SubElement(org,"financial_year_to")
		financial_year_to.text = db_to_date
		dbname = et.SubElement(org,"dbname") 
		
		#creating database name for organisation		
		org_db_name = name_of_org[0:1]
		time = datetime.datetime.now()
		str_time = str(time.microsecond)	
		new_microsecond = str_time[0:2]		
		result_dbname = org_db_name + str(time.year) + str(time.month) + str(time.day) + str(time.hour)\
		 		+ str(time.minute) + str(time.second) + new_microsecond
			
		dbname.text = result_dbname #assigning created database name value in dbname tag text of abt.xml
		
		abtconf.write("/opt/abt/abt.xml")
		# getting client_id for the given orgnisation and from and to date
		self.client_id = dbconnect.getConnection([name_of_org,db_from_date,db_to_date])
		
		try:
			metadata = dbconnect.Base.metadata
			metadata.create_all(dbconnect.engines[self.client_id])
		except:
			print "cannot create metadata"
			
		Session = scoped_session(sessionmaker(bind=dbconnect.engines[self.client_id]))
			
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
			account.balance\
			from groups join account on (groups.groupcode = account.groupcode)\
			left outer join subgroups\
			on (account.subgroupcode = subgroups.subgroupcode) order by groupname;")
		connection = dbconnect.engines[self.client_id].raw_connection()
		cur = connection.cursor()
		
		if (organisationType == "Profit Making"):

			Session.add_all([
				dbconnect.Groups('Capital',''),
				dbconnect.Groups('Current Asset',''),
				dbconnect.Groups('Current Liability',''),
				dbconnect.Groups('Direct Income','Income refers to consumption\
		opportunity gained by an entity within a specified time frame.'),
				dbconnect.Groups('Direct Expense','This are the expenses to be incurred for\
		operating the buisness.'),
				dbconnect.Groups('Fixed Assets',''),
				dbconnect.Groups('Indirect Income','Income refers to consumption opportunity\
		gained by an entity within a specified time frame.'),
				dbconnect.Groups('Indirect Expense','This are the expenses to be incurred\
		for operating the buisness.'),\
				dbconnect.Groups('Investment',''),
				dbconnect.Groups('Loans(Asset)',''),
				dbconnect.Groups('Loans(Liability)',''),
				dbconnect.Groups('Reserves',''),
				dbconnect.Groups('Miscellaneous Expenses(Asset)','')
			])
			Session.commit()
		
		else:
			Session.add_all([\
				dbconnect.Groups('Corpus',''),
				dbconnect.Groups('Current Asset',''),
				dbconnect.Groups('Current Liability',''),
				dbconnect.Groups('Direct Income','Income refers to consumption\
		opportunity gained by an entity within a specified time frame.'),
				dbconnect.Groups('Direct Expense','This are the \
		expenses to be incurred for operating the buisness.'),
				dbconnect.Groups('Fixed Assets',''),
				dbconnect.Groups('Indirect Income','Income refers to consumption \
		opportunity gained by an entity within a specified time frame.'),
				dbconnect.Groups('Indirect Expense','This are the \
		expenses to be incurred for operating the buisness.'),
				dbconnect.Groups('Investment',''),
				dbconnect.Groups('Loans(Asset)',''),
				dbconnect.Groups('Loans(Liability)',''),
				dbconnect.Groups('Reserves',''),
				dbconnect.Groups('Miscellaneous Expenses(Asset)','')
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

		Session.close()
		connection.close()
		return True,self.client_id
		
	def xmlrpc_rollover(self,queryParams,client_id):
		"""
		* Purpose:
			- This function is to forward the closing balance of current year 
			  to next financial year as opening balance 
			- it will first get the all accountname and corrosponding closing 
			  balance of current financial year.
			- then its create the schema and dump of current year's database
			  and then get the reverse pattern match from both as save to file
			  db.dump
			- then from db.dump it will only give the dump of ``account`` ``subgroups``
			  and ``organisation`` table 
			- then ``rpc_Deploy`` function will deploy new databse for given
			  newFinancialTo date and Organisation and OrganisationType
			  where ``newFinancialFrom`` date will calculate by adding one day to 
			  current ``financialTo`` date
			- and the restore all the values of ``account`` ``subgroups`` and
			  ``organisation``
			- update ``openingbalance`` of the restored ``account`` table with 
			  the calculated ``closingbalance``.
			  
		* Input: 
		 	- [organisationName,financialFrom,financialTo,newFinancialTo],client_id
		 	
		* Output:
			- boolean True
			- created new financile year and database 
			- restore accounts its closingbalance as openingbalance and subgroups 
		"""
		account = rpc_account.account()
		accounts = account.xmlrpc_getAllAccountNames(client_id)
		rollOverAccounts = {}
		for acc in accounts:
			report = rpc_reports.reports()
			closingRow = report.xmlrpc_calculateBalance([acc,queryParams[1],queryParams[2],\
									queryParams[3]],client_id)
			# [group_name,bal_brought,curbal,total_DrBal,total_CrBal,opening_baltype,baltype]
			closing_balance = 0.00
			if (str(closingRow[6])  == "Cr" 
				and (str(closingRow[0])== "Current Asset" 
				or str(closingRow[0])== "Fixed Asset" 
				or str(closingRow[0])== "Investment" 
				or str(closingRow[0])== "Loans(Asset)" 
				or str(closingRow[0])== "Miscellaneous Expenses(Asset)")):
				
				closing_balance = -int(closingRow[2])
				rollOverAccounts[acc] = closing_balance
				
			if (str(closingRow[6])  == "Dr" 
				and  (str(closingRow[0])== "Current Asset" 
				or str(closingRow[0])== "Fixed Asset" 
				or str(closingRow[0])== "Investment" 
				or str(closingRow[0])== "Loans(Asset)" 
				or str(closingRow[0])== "Miscellaneous Expenses(Asset)")):
				
				closing_balance = int(closingRow[2])
				rollOverAccounts[acc] = closing_balance
				
			if (str(closingRow[6])  == "Cr"
				and  (str(closingRow[0])== "Corpus" 
				or str(closingRow[0])== "Capital" 
				or str(closingRow[0])== "Current Liability" 
				or str(closingRow[0])== "Loans(Liability)" 
				or str(closingRow[0])== "Reserves")):
				
				closing_balance = int(closingRow[2])
				rollOverAccounts[acc[0]] = closing_balance
				
			if (str(closingRow[6])  == "Dr"
				and  (str(closingRow[0])== "Corpus" 
				or str(closingRow[0])== "Capital" 
				or str(closingRow[0])== "Current Liability" 
				or str(closingRow[0])== "Loans(Liability)"
				or str(closingRow[0])== "Reserves")):	
				
				closing_balance = -int(closingRow[2])
				rollOverAccounts[acc] = closing_balance
		
		financialFrom = queryParams[1]
		financialTo = queryParams[2]
		newFinancialTo = queryParams[3]
		orgs = dbconnect.getOrgList()
		for org in orgs:
			orgname = org.find("orgname")
			financialyear_from = org.find("financial_year_from")#DD-MM-YYYY
			financialyear_to = org.find("financial_year_to")
			if (orgname.text == queryParams[0]
					and financialyear_from.text == financialFrom 
					and financialyear_to.text == financialTo):
				dbname = org.find("dbname")
		
				database = dbname.text
		print "the current database name is " + database
		try:
			os.system("sqlite3 /opt/abt/db/"+database+" .sch > schema")
			os.system("sqlite3 /opt/abt/db/"+database+" .dump > dump")
			os.system("grep -vxw -f schema dump > /opt/abt/db/db.dump")
			os.system("grep -w 'account\|subgroups\|organisation' /opt/abt/db/db.dump > /opt/abt/db/db_dump.dump")
		except:
			print "problem to dump database"
		oneDay = datetime.timedelta(days=1)
		finalDate = datetime.date(int(financialTo[6:10]),int(financialTo[3:5]),int(financialTo[0:2]))
		newStartDate = finalDate + oneDay
		newFinancialFrom = newStartDate.strftime("%d-%m-%Y")

		dbconnect.engines[client_id].dispose()
		del dbconnect.engines[client_id]
		self.client_id = self.xmlrpc_Deploy([queryParams[0],newFinancialFrom,newFinancialTo,queryParams[4]])
		
		newOrgs = dbconnect.getOrgList()
		for newOrg in newOrgs:
			orgname = newOrg.find("orgname")
			financialyear_from = newOrg.find("financial_year_from")
			financialyear_to = newOrg.find("financial_year_to")
			
			if (orgname.text == queryParams[0] 
					and financialyear_from.text == newFinancialFrom 
					and financialyear_to.text == queryParams[3]):
					
				newdbname = newOrg.find("dbname")
				newDatabase = newdbname.text
		print "deployment is done and the new dbname is " + newDatabase
		connection = dbconnect.engines[self.client_id[1]].raw_connection()
		dbconnect.engines[self.client_id[1]].execute("delete from subgroups;")
		connection.commit()
		try:
			os.system("sqlite3 /opt/abt/db/"+ newDatabase+"< /opt/abt/db/db_dump.dump")
			for account in rollOverAccounts.keys():
				editStatement = "update account set openingbalance = "+str(rollOverAccounts[account])+\
						" where accountname = '" + account + "'"
				dbconnect.engines[self.client_id[1]].execute(editStatement)
		
			connection.commit()
		except:
			print "problem to restore data in to new database"
			
		return True	

def runabt():
	"""
	+ As we have imported all the nested XMLRPC resource,so that create one handler ``abt`` 
	  calls another if a method with a given prefix is called.
	+ and publish that handelr instance ``abt`` to server .
	+ this is ``def runabt()`` which is outside ``class abt():``.
	"""
	import rpc_main
	# create the instance of class abt
	abt = rpc_main.abt()
	groups=rpc_groups.groups()
	abt.putSubHandler('groups',groups)

	account=rpc_account.account()
	abt.putSubHandler('account',account)

	organisation = rpc_organisation.organisation()
	abt.putSubHandler('organisation',organisation)

	transaction=rpc_transaction.transaction()
	abt.putSubHandler('transaction',transaction)

	data=rpc_data.data()
	abt.putSubHandler('data',data)

	reports=rpc_reports.reports()
	abt.putSubHandler('reports',reports)

	# user=rpc_user.user()
	# abt.putSubHandler('user',user)

	getaccountsbyrule=rpc_getaccountsbyrule.getaccountsbyrule()
	abt.putSubHandler('getaccountsbyrule',getaccountsbyrule)

	print "initialising application"
	#the code to daemonise published instance.
	
 	# Daemonizing abt
	# Accept commandline arguments
	# A workaround for debugging
	def usage():
		print "Usage: %s [d|debug] [h|help]\n" % (sys.argv[0])
		print "\td (debug)\tStart server in debug mode. Do not fork a daemon."
		print "\td (help)\tShow this help"

	try:
		opts, args = getopt.getopt(sys.argv[1:], "hd", ["help","debug"])
	except getopt.GetoptError:
		usage()
		os._exit(2)

	debug = 0
	for opt, arg in opts:
		if opt in ("h", "help"):
			usage()
			os.exit(0)
		elif opt in ("d", "debug"):
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
		# stdout, and stderr to /dev/null.  This is done to prevent sideeffects
		# from reads and writes to the standard I/O file descriptors.

		# This call to open is guaranteed to return the lowest file descriptor,
		# which will be 0 (stdin), since it was closed above.
		os.open(REDIRECT_TO, os.O_RDWR)	# standard input (0)

		# Duplicate standard input to standard output and standard error.
		os.dup2(0, 1)			# standard output (1)
		os.dup2(0, 2)			# standard error (2)
	
	#publish the object and make it to listen on the given port through reactor
	print "starting server"
	reactor.listenTCP(7081, server.Site(abt))
	#start the service by running the reactor.
	reactor.run()
	
