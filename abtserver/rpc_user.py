#import the database connector and functions for stored procedure.
import dbconnect
#import the twisted modules for executing rpc calls and also to implement the server
from twisted.web import xmlrpc, server
#reactor from the twisted library starts the server with a published object and listens on a given port.
from twisted.internet import reactor
#import bz2
from modules import blankspace
#inherit the class from XMLRPC to make it publishable as an rpc service.
class user(xmlrpc.XMLRPC):
	def __init__(self):
		'''
		+  Note that all the functions to be accessed by the
		   client must have the xmlrpc_ prefix.  the client
		   however will not use the prefix to call the functions.
		'''
		xmlrpc.XMLRPC.__init__(self)
		
	def xmlrpc_setUser(self,queryParams,client_id):
		'''
		* Input:
			-[firstname,lastname,username,password,gender,userrole]
		'''
		queryParams = blankspace.remove_whitespaces(queryParams)
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		username = queryParams[2]
		#password = bz2.compress(queryParams[1])
		password =queryParams[3].encode('base64')
		user_role = queryParams[5]
		Session.add(dbconnect.Users(queryParams[0],queryParams[1],username,password,queryParams[4],user_role))
		Session.commit()
		return "Sign up sccessfully"
		
	def xmlrpc_getUser(self,queryParams,client_id):
		'''
		* Purpose:
			- It will provide information of user based on
		          username and password return list containing username
		          userrole if condition is true else return false
		* Input: 
			- username , password 
			
		* Output
		       - 
		'''
		queryParams = blankspace.remove_whitespaces(queryParams)
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		#password = bz2.compress(queryParams[1])
		password = queryParams[1].encode('base64')
		result = Session.query(dbconnect.Users).\
						filter(dbconnect.Users.username == queryParams[0]).\
						filter(dbconnect.Users.userpassword == password).\
						first()
		Session.close()
		connection.connection.close()
		if result != None:
			#dbconnect.addUser(client_id,queryParams[0])
			userlist =[result.username,result.userrole]
			print userlist
			
   			return userlist
		else:
			return []
	
	def xmlrpc_isAdmin(self,client_id):
		'''
		* Input:
			- [username , password , userrole]
		'''
		
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		#password = bz2.compress(queryParams[1])
		#password = queryParams[1].encode('base64')
		result = Session.query(dbconnect.Users).filter(dbconnect.Users.userrole == "admin").first()			
		Session.close()
		connection.connection.close()
		print "admin exist"
		print result
		if result == None:
			return False
		else:	
			return True
				
		
	def xmlrpc_isUserExist(self,queryParams,client_id):
		'''
		* Input:
			- [username , password , userrole]
		'''
		queryParams = blankspace.remove_whitespaces(queryParams)
		print queryParams
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		#password = bz2.compress(queryParams[1])
		password = queryParams[1].encode('base64')
		result = Session.query(dbconnect.Users).filter(dbconnect.Users.username == queryParams[0]).\
							filter(dbconnect.Users.userpassword == password).\
							filter(dbconnect.Users.userrole == queryParams[2]).first()			
		Session.close()
		connection.connection.close()
		print "user exist"
		print result
		if result == None:
			return False
		else:	
			return True
			
	
	def xmlrpc_isUserUnique(self,queryParams,client_id):
		queryParams = blankspace.remove_whitespaces(queryParams)
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		result = Session.query(dbconnect.Users).filter(dbconnect.Users.username == queryParams[0]).first()
		Session.close()
		connection.close()
		print "user n password"
		print result
		if result == None:
			return True
		else:	
			
			return False

	
	

	def xmlrpc_changePassword(self,queryParams,client_id):
		'''
		purpose
		It will provide information of user based on username and password
		return list containing useename , userrole if condition is true
		else return false 
			
		'''
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		queryParams = blankspace.remove_whitespaces(queryParams)
		password =queryParams[1].encode('base64')
		result= session.query(Users).filter_by(dbconnect.Users.username == queryParams[0]).\
						update(dbconnect.Users.userpassword == password)

		
		row = result.fetchone()
		return row[0]


			
	
	
