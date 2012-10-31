#import the database connector and functions for stored procedure.
import dbconnect
#import the twisted modules for executing rpc calls and also to implement the server
from twisted.web import xmlrpc, server
#reactor from the twisted library starts the server with a published object and listens on a given port.
from twisted.internet import reactor
from sqlalchemy.orm.exc import NoResultFound
from modules import blankspace
#inherit the class from XMLRPC to make it publishable as an rpc service.
class user(xmlrpc.XMLRPC):
	def __init__(self):
		xmlrpc.XMLRPC.__init__(self)
		"""
		note that all the functions to be accessed by the
		client must have the xmlrpc_ prefix.  the client
		however will not use the prefix to call the functions.
		"""	
	

	def xmlrpc_getUser(self,queryParams,client_id):
		'''
		def xmlrpc_getUser(self,queryParams,client_id):
		purpose It will provide information of user based on
		username and password return list containing useename
		, userrole if condition is true else return false
		'''
		queryParams = blankspace.remove_whitespaces(queryParams)
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		res = Session.query(dbconnect.Users).\
		filter(dbconnect.Users.username == queryParams[0]).\
		filter(dbconnect.Users.userpassword == queryParams[1]).\
		first()
		Session.close()
		connection.connection.close()
		if res != None:
			dbconnect.addUser(client_id,queryParams[0])
			lst=[res.username, res.userrole]
			print lst
			print dbconnect.userlist
   			return lst
		else:
			return False
	'''
	def xmlrpc_changePassword(self,queryParams,client_id): purpose
		It will provide information of user based on username and password
		return list containing useename , userrole if condition is true
		else return false 
			

	def xmlrpc_changePassword(self,queryParams,client_id):
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		res= session.query(Users).filter_by(dbconnect.Users.username == queryParams[0]).update(dbconnect.Users.userpassword == queryParams[1])

		
		row = res.fetchone()
		return row[0]

''' 
			
	
	
