""" 
RPC module for organisation.  This module will handle entry and
updates of organisation and also getting the data for a given
organisation
""" 
#import the database connector 
import dbconnect
#import the twisted modules for executing rpc calls and also to implement the server
from twisted.web import xmlrpc, server
#reactor from the twisted library starts the server with a published object and listens on a given port.
from twisted.internet import reactor
#inherit the class from XMLRPC to make it publishable as an rpc service.
from modules import blankspace
class organisation(xmlrpc.XMLRPC):

	"""
	Performs all the operations related to organisation details
	and setting up preferences
	"""
	def __init__(self):
		xmlrpc.XMLRPC.__init__(self)
		"""
		note that all the functions to be accessed by the
		client must have the xmlrpc_ prefix.  the client
		however will not use the prefix to call the functions.
		"""
	
	def xmlrpc_setPreferences(self,queryParams,client_id):
		"""
		Purpose: function for update flags for project
		         ,manually created account code and voucher
		         reference number i/p parameters: Flag
		         No(datatype:integer) , FlagName
		         (datatype:text) o/p parameter : True

		Description : if flag no is "2" then will update
				accountcode flag value as either
				"manually" or "automatic"(default) if
				flag no is "1" then will update refeno
				flag value as either "mandatory" or
				"optional"
		"""
		queryParams = blankspace.remove_whitespaces(queryParams)
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		Session.query(dbconnect.Flags).\
			filter(dbconnect.Flags.flagno == queryParams[0]).\
			update({'flagname':queryParams[1]})
		Session.commit()
		Session.close()
		connection.connection.close()
		return True
	
	def xmlrpc_getPreferences(self,queryParams,client_id):
		"""
		Purpose: finding the appropriate preferences i/p
		parameters: flagno o/p parameter : flagname

		Description : if flag no is "2" then will return
			      accountcode flag value. If flag no is
			      "1" then will return refeno flag value
		"""
		queryParams = blankspace.remove_whitespaces(queryParams)
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		print queryParams[0]
		result = Session.query(dbconnect.Flags).\
				filter(dbconnect.Flags.flagno == queryParams[0]).\
				first()
		#print res.flagname
		if result == []:
			return result
		else:
			print result.flagname
			return result.flagname

		Session.commit()
		Session.close()
		connection.connection.close()
		
	def xmlrpc_setProjects(self,queryParams,client_id):
		"""
		Purpose: function for set projects for a particular
		organisation i/p parameters: projectname
		(datatype:text) o/p parameter : Boolean True
		"""
		queryParams = blankspace.remove_whitespaces(queryParams)
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		Session.add_all([dbconnect.Projects(None,queryParams[0])])
		Session.commit()
		description='Created Project '+queryParams[0]
		#dbconnect.setLog([6,description],client_id)

		return True
		
	def xmlrpc_getAllProjects(self,client_id):
		"""
		Purpose: function for get all projects for a
		particular organisation i/p parameters:client_id o/p
		parameter :if list is blank then return False else
		list of list projectcaode(datatype:Integer) and
		projectname(datatype:text)
		"""
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		result = Session.query(dbconnect.Projects).order_by(dbconnect.Projects.projectname).all()
		Session.close()
		connection.connection.close()
		if result == []:
			return result
		else:
			projects = []
			for i in range(0,len(result)):
				projects.append([result[i].projectcode, result[i].projectname])
			return projects
		
		
	def xmlrpc_setOrganisation(self,queryParams,client_id):
		'''
		Purpose : function for add organisation details in database
		if orgtype is 'NGO then				
			i/p parameters : orgtype,orgname,orgaddress,orgcity,orgpincode,orgstate,
					 orgcountry,orgtelno,orgfax,orgwebsite,orgemail,
					 orgpan,"","",orgregno,orgregdate,
					 orgfcrano,orgfcradate,client_id
		else 
			i/p parameters : orgtype,orgname,orgaddress,orgcity,orgpincode,orgstate,
					 orgcountry,orgtelno,orgfax,orgwebsite,orgemail,
					 orgpan,orgmvat,orgstax,"","",
					 "","",client_id
		
		o/p parameter : true or false
		'''
		queryParams = blankspace.remove_whitespaces(queryParams)
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		print queryParams
		Session.add_all([\
				dbconnect.Organisation(\
					queryParams[0],queryParams[1],queryParams[2],queryParams[3],\
					queryParams[4],queryParams[5],queryParams[6],queryParams[7],\
					queryParams[8],queryParams[9],queryParams[10],queryParams[11],\
					queryParams[12],queryParams[13],queryParams[14],\
					queryParams[15],queryParams[16],queryParams[17])\
				])
		
		Session.commit()
		Session.close()
		connection.connection.close()
		return True 
	
	def xmlrpc_getorgTypeByname(self, queryParams, client_id):   
		'''
		Purpose   : Function for getting if an orgtype with supplied
		        orgname.    
		Parameters : queryParams which is a list containing one element,
		        orgname as string.
		Returns :  orgtype if orgname match else eturn false string
		Description : Querys the Organisation table and sees if an orgname
		    similar to one provided as a parameter.
		    if it exists then it will return orgtype related orgname
		'''
		print  queryParams[0]
		queryParams = blankspace.remove_whitespaces(queryParams)
		connection = dbconnect.engines[client_id].connect()
	        Session = dbconnect.session(bind=connection)
	        result = Session.query(dbconnect.Organisation).\
	           		 filter(dbconnect.Organisation.orgname == queryParams[0]).\
	               		 first()
		Session.close()
	        connection.connection.close()
		
		if result == None:
		    return "0"   
		else:
		    return result.orgtype
            
	def xmlrpc_getOrganisation(self,client_id):
		'''
		Purpose:function to get all the details of organisation from database					
		i/p parameters : client_id
		o/p parameter : true if result contain value else false
		'''
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		result = Session.query(dbconnect.Organisation).all()
		Session.close()
		connection.connection.close()
		if result == []:
			return result
		else:
			orgdetail_list = []
			for l in result:
				orgdetail_list.append([\
						l.orgcode,l.orgtype,l.orgname,l.orgaddr,\
						l.orgcity,l.orgpincode,l.orgstate,l.orgcountry,\
						l.orgtelno,l.orgfax,l.orgwebsite,l.orgemail,\
						l.orgpan,l.orgmvat,l.orgstax,l.orgregno,\
						l.orgregdate,l.orgfcrano,l.orgfcradate\
						])
			return orgdetail_list
			
	def xmlrpc_updateOrg(self,queryParams,client_id):
		'''
		Purpose: updating the orgdetails after edit organisation
		i/p parameters:
				orgcode,orgaddress,orgcountry,orgstate,
				orgcity,orgpincode,orgtelno,orgfax,orgemail,
				orgwebsite,orgmvat,orgstax,orgregno,
				orgregdate,orgfcrano,orgfcradate,orgpan,
				client_id
		o/p parameter : string
		'''
		queryParams = blankspace.remove_whitespaces(queryParams)
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		statement = "update organisation set orgaddr='"+queryParams[1]+"',\
						orgcountry='"+queryParams[2]+"',\
						orgstate='"+queryParams[3]+"',\
						orgcity='"+queryParams[4]+"',\
						orgpincode='"+queryParams[5]+"',\
						orgtelno='"+queryParams[6]+"',\
						orgfax='"+queryParams[7]+"',\
						orgemail='"+queryParams[8]+"',\
						orgwebsite='"+queryParams[9]+"',\
						orgmvat='"+queryParams[10]+"',\
						orgstax='"+queryParams[11]+"',\
						orgregno='"+queryParams[12]+"',\
						orgregdate='"+queryParams[13]+"',\
						orgfcrano='"+queryParams[14]+"',\
						orgfcradate='"+queryParams[15]+"',\
						orgpan='"+queryParams[16]+"'\
						where orgcode='"+queryParams[0]+"'"	
		dbconnect.engines[client_id].execute(statement)
		Session.commit()
		Session.close()
		connection.connection.close()
		return "upadte successfully"



