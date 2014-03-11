from sqlalchemy import create_engine, func, select, literal_column
from sqlalchemy import orm
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, select, Text, DECIMAL, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.types import Numeric, TIMESTAMP, Enum 
from xml.etree import ElementTree as et
import os
from sqlalchemy import *
from types import * 
from sqlite3 import dbapi2 as sqlite
engines = []
session = sessionmaker()

def getOrgList():
	""" 
	* Purpose:
		- This function create opens the configuration file abt.xml (path : opt/abt)
		- used xml.etree to cerate xml file and parsing it .
		- Write root node `<abt> </abt>`.
		- if any organisation present then and gets the list of all organisations registered on the server.

	* Output:
		- returns list of clildnode(organisaton)
	""" 	
    	print "getorglist"
	if os.path.exists("/opt/abt/abt.xml") == False:
		print "file not found trying to create one."
		try:
		    os.system("touch /opt/abt/abt.xml")
		    print "file created "
		    os.system("chmod 722 /opt/abt/abt.xml")
		    print "permissions granted "
		except:
		    print "the software is finding trouble creating file."
		    return False
		try:
		    gkconf = open("/opt/abt/abt.xml", "a")
		    gkconf.write("<abt>\n")
		    gkconf.write("</abt>")
		    gkconf.close()
		except:
		    print "we can't write to the file, sorry!"
		    return False
	#opening the abt.xml file by parsing it into a tree.	
	abtconf = et.parse("/opt/abt/abt.xml")
	#now since the file is opened we will get the root element.  
	abtroot = abtconf.getroot()
	#we will now extract the list of children (organisations ) into a variable named orgs. 
	orgs = abtroot.getchildren() 
	return orgs

def getDatabaseName(queryParams):
	"""
	* Purpose: 
		- To get database name stored in abt.xml file.
		- Given organisation name , financial from , financial to.
	* Input:
		- [orgname,financialfrom,financialto]
	* Output:
		- return string database name
	"""
	database = ""
	orgs = getOrgList()
	for org in orgs:
		orgname = org.find("orgname")
		financialyear_from = org.find("financial_year_from")#DD-MM-YYYY
		financialyear_to = org.find("financial_year_to")
		if (orgname.text == queryParams[0]
				and financialyear_from.text ==  queryParams[1]
				and financialyear_to.text ==  queryParams[2]):
			dbname = org.find("dbname")
		
			database = dbname.text
		
	return database
	
def getConnection(queryParams):
	"""
	* Purpose:
		- The getConnection function will actually establish connection and 
		- return the id of the latest engine added to the list.
		- first it will check for 
		- if this is the first time we are running the server 
		  then we need to create the ``abt.xml`` file.	
		- engine in this analogy is a connection maintained as a session.
		- so every time a new client connects to the rpc server,
		- a new engine is appended to the list and the index returned as the id.
	
	* Input:
		- [organisationame,finanialyear_from,financialyear_to]
	
	* Output:
		- returns index of last created engine as a client_id
	"""
	
	#dbname = "" #the dbname variable will hold the final database name for the given organisation. 
	database = getDatabaseName([queryParams[0],queryParams[1],queryParams[2]])
	global engines #the engine has to be a global variable so that it is accessed throughout the module.
	stmt = 'sqlite:////opt/abt/db/' + database
	engine = create_engine(stmt, echo=False) #now we will create an engine instance to connect to the given database.
	engines.append(engine)  #add the newly created engine instance to the list of engines.
	return engines.index(engine) #returning the connection number for this engine.
	

Base = declarative_base()
class Account(Base):
    __tablename__ = "account"
    accountcode = Column(String(40), primary_key=True)
    groupcode = Column(Integer, ForeignKey("groups.groupcode"), nullable=True)
    subgroupcode = Column(Integer, ForeignKey("subgroups.subgroupcode"), nullable=True) 
    accountname = Column(Text, nullable=False)
    openingbalance = Column(Numeric(13, 2))
    openingdate = Column(TIMESTAMP)
    
   

    def __init__(self, accountcode, groupcode, subgroupcode, 
    accountname, openingbalance, openingdate):
        self.accountcode = accountcode
        self.groupcode = groupcode
        self.subgroupcode = subgroupcode
        self.accountname = accountname
        self.openingbalance = openingbalance
        self.openingdate = openingdate
       
        

account_table = Account.__table__


class VoucherMaster(Base):    
    __tablename__ = "voucher_master"
    vouchercode = Column(String(40), primary_key=True)
    reference = Column(String(40), nullable=True)
    voucherdate = Column(TIMESTAMP, nullable=False)
    reffdate = Column(TIMESTAMP)
    vouchertype = Column(String(40))
    flag = Column(Integer)
    projectcode = Column(Integer)
    narration = Column(Text, nullable=False)
    cheque_no = Column(String(40),nullable=True)

    def __init__(self, vouchercode,reference, voucherdate, reffdate, 
    vouchertype, flag, projectcode, narration,cheque_no):
        self.vouchercode = vouchercode
        self.reference = reference
        self.voucherdate = voucherdate
        self.reffdate = reffdate
        self.vouchertype = vouchertype
        self.flag = flag
        self.projectcode = projectcode
        self.narration = narration
        self.cheque_no = cheque_no

vouchermaster_table = VoucherMaster.__table__

class VoucherDetails(Base):
    __tablename__ = "voucher_details"
    cbdtcode = Column(Integer, primary_key=True)
    vouchercode = Column(String(40), ForeignKey("voucher_master.vouchercode"))
    typeflag = Column(String(10), nullable=False)
    accountcode = Column(String(40), ForeignKey("account.accountcode"), nullable=False)
    amount = Column(Numeric(13, 2), nullable=False)

    def __init__(self, vouchercode, typeflag, accountcode, amount):
        self.vouchercode = vouchercode
        self.typeflag = typeflag
        self.accountcode = accountcode
        self.amount = amount

voucherdetails_table = VoucherDetails.__table__

class BankRecon(Base):
    __tablename__ = "bankrecon"
    reconcode = Column(Integer,primary_key = True)
    vouchercode = Column(String(40),ForeignKey("voucher_master.vouchercode"))
    reffdate = Column(TIMESTAMP)
    accountcode = Column(String(40), ForeignKey("account.accountcode"), nullable=False)
    dramount = Column(Numeric(13,2))
    cramount = Column(Numeric(13,2))
    clearancedate = Column(TIMESTAMP)
    memo = Column(Text)

    def __init__(self,reconcode,vouchercode,reffdate,accountcode,
    dramount,cramount,clearancedate,memo):
        self.reconcode = reconcode
        self.vouchercode = vouchercode
        self.reffdate = reffdate
        self.accountcode = accountcode
        self.dramount = dramount
        self.cramount = cramount
        self.clearancedate = clearancedate
        self.memo = memo

bankrecon_table = BankRecon.__table__

class Organisation(Base):
    __tablename__ = 'organisation'
    orgcode = Column(Integer, primary_key=True)
    orgname = Column(Text, nullable=False)
    orgtype = Column(Text, nullable=False)
    orgcountry = Column(Text)
    orgstate = Column(Text)
    orgcity = Column(Text)
    orgaddr = Column(Text)
    orgpincode = Column(String(30))
    orgtelno = Column(Text)
    orgfax = Column(Text)
    orgwebsite = Column(Text)
    orgemail = Column(Text)
    orgpan = Column(Text)
    orgmvat = Column(Text)
    orgstax = Column(Text)
    orgregno = Column(Text)
    orgregdate = Column(Text)
    orgfcrano = Column(Text)
    orgfcradate = Column(Text)

    def __init__(self,orgname,orgtype,orgcountry,orgstate,orgcity,orgaddr,orgpincode,
     orgtelno, orgfax, orgwebsite, orgemail, orgpan, orgmvat, orgstax,
      orgregno, orgregdate, orgfcrano, orgfcradate):    
       
        self.orgname = orgname
        self.orgtype = orgtype
        self.orgcountry = orgcountry
        self.orgstate = orgstate
        self.orgcity = orgcity
        self.orgaddr = orgaddr
        self.orgpincode = orgpincode
        self.orgtelno = orgtelno
        self.orgfax = orgfax
        self.orgwebsite = orgwebsite
        self.orgemail = orgemail
        self.orgpan = orgpan
        self.orgmvat = orgmvat
        self.orgstax = orgstax
        self.orgregno = orgregno
        self.orgregdate = orgregdate
        self.orgfcrano = orgfcrano
        self.orgfcradate = orgfcradate
organisation_table = Organisation.__table__

class Projects(Base):
    __tablename__ = 'projects'
    projectcode = Column(Integer, primary_key=True)
    projectname = Column(Text)

    def __init__(self, projectcode, projectname):
        self.projectcode = projectcode
        self.projectname = projectname

projects_table = Projects.__table__

class Flags(Base):
    __tablename__ = 'flags'
    flagno = Column(Integer, primary_key=True)
    flagname = Column(Text)
    set_flag = Column(Integer)

    def __init__(self, flagno, flagname, set_flag):
        self.flagno = flagno
        self.flagname = flagname
        self.set_flag = set_flag

flags_table = Flags.__table__

 
class Groups(Base):
    __tablename__ = "groups"
    
    groupcode = Column(Integer, primary_key=True)
    groupname = Column(Text, nullable=False)
    groupdesc = Column(Text)

    def __init__(self, groupname, groupdesc):
        self.groupname = groupname
        self.groupdesc = groupdesc
        
groups_table = Groups.__table__

class subGroups(Base):
    __tablename__ = "subgroups"
    subgroupcode = Column(Integer, primary_key=True)
    groupcode = Column(Integer, ForeignKey("groups.groupcode"), nullable=False)
    subgroupname = Column(Text)
    
    def __init__(self, groupcode, subgroupname):
        self.groupcode = groupcode
        self.subgroupname = subgroupname
        
subgroups_table = subGroups.__table__

class Users(Base):
	__tablename__ = 'users'
	userid = Column(Integer, primary_key=True)
	username = Column(Text,nullable=False)
	userpassword = Column(String)
	gender = Column(String)
	userrole = Column(String)
	question = Column(Integer)
	answer = Column(String)
	login_time = Column(Text)
	logout_time = Column(Text)

	def __init__(self,username, userpassword,gender,userrole,question,answer,login_time,logout_time):
		self.userid = None
		self.username = username
		self.userpassword = userpassword
		self.gender = gender
		self.userrole = userrole
		self.question = question
		self.answer = answer
		self.login_time = login_time
		self.logout_time = logout_time

users_table = Users.__table__

class ProfitLoss(Base):
	__tablename__='profit_loss'
	plid = Column(Integer, primary_key=True)
	net_flag =  Column(String)
	opening_balance =  Column(Numeric(13, 2))
	
	def __init__(self,net_flag,opening_balance):
		self.plid = None
		self.net_flag = net_flag
		self.opening_balance = opening_balance
profit_loss = ProfitLoss.__table__
orm.compile_mappers()
