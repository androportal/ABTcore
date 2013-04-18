import dbconnect
from twisted.web import xmlrpc, server
from twisted.internet import reactor
from modules import blankspace

class user(xmlrpc.XMLRPC):
	"""
	+ this class will do all the task related to user.
		  
	"""
	def __init__(self):
		xmlrpc.XMLRPC.__init__(self)
		
	def xmlrpc_setUser(self,queryParams,client_id):
		"""
		* Purpose: 
			- This function is to add the user details
			- it will add all the input details in the user
			  table present in the ``dbconnect.py``
		* Input:
			-[firstname,lastname,username,password,gender,userrole,question,answer]
		"""
		print queryParams
		queryParams = blankspace.remove_whitespaces(queryParams)
		print "queryParams"
		print queryParams
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		username = queryParams[0]
		password =queryParams[1].encode('base64')
		user_role = queryParams[3]
		Session.add(dbconnect.Users(\
				username,password,queryParams[2],user_role,queryParams[4],queryParams[5]))
		Session.commit()
		print "sign up"
		return "Sign up sccessfull"
		
	def xmlrpc_getUser(self,queryParams,client_id):
		'''
		* Purpose:
			- It will provide information of user based on
		          username and password return list containing username
		          userrole if condition is true else return false
		* Input: 
			- [username , password ]
			
		* Output
		       - it returns list of username and userrole
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
			
	def xmlrpc_getUserRole(self,queryParams,client_id):
		'''
		* Purpose:
			- It will provide information of user based on
		          username and password return list containing username
		          userrole if condition is true else return false
		* Input: 
			- [username , password ]
			
		* Output
		       - it returns list of username and userrole
		'''
		queryParams = blankspace.remove_whitespaces(queryParams)
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		#password = bz2.compress(queryParams[1])
		password = queryParams[1].encode('base64')
		result = Session.query(dbconnect.Users).\
						filter(dbconnect.Users.username == queryParams[0]).\
						first()
		Session.close()
		connection.connection.close()
		if result != None:
			 
   			return result.userrole
		else:
			return []
	
	def xmlrpc_isAdmin(self,client_id):
		'''
		* purpose: 
			- this function is to check if userrole ``admin`` is pesent
			  in organisaion 
		* Input:
			- [username , password , userrole]
			
		* Output:
			- if ``admin`` then return ``true`` else retrun ``false``
		'''
		
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
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
		* Purpose: 
			- function to check for valid password and userrole and
			  username 
			  
		* Input:
			- [username , password , userrole]
		* Output:
			- if username, password and userole is valid then
			  return ``True`` else return ``False``
		'''
		queryParams = blankspace.remove_whitespaces(queryParams)
		print queryParams
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		password = queryParams[1].encode('base64')
		result = Session.query(dbconnect.Users).filter(dbconnect.Users.username == queryParams[0]).\
							filter(dbconnect.Users.userpassword == password).\
							filter(dbconnect.Users.userrole == queryParams[2]).first()			
		Session.close()
		connection.connection.close()
	
		if result == None:
			return False
		else:	
			return True
			
	
	def xmlrpc_isUserUnique(self,queryParams,client_id):
		'''
		* Purpose: 
			- this function to check the given user is unique
			- this function will be usefull when add new user
			  so, it avoid duplicate username
			 
		* Input:
			- [username]
			
		* Output:
			- if given username exist the return ``true``
			  else return ``false``
		'''
		queryParams = blankspace.remove_whitespaces(queryParams)
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		result = Session.query(dbconnect.Users).filter(dbconnect.Users.username == queryParams[0]).first()
		Session.close()
		connection.close()
		
		if result == None:
			return True
		else:	
			
			return False

	def xmlrpc_changePassword(self,queryParams,client_id):
		'''
		* purpose:
			- It will provide to update password based on username
		
		* Input:
			- [username,password]
			
		* Output: 
			- return ``password updated successully``
			
		'''
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		queryParams = blankspace.remove_whitespaces(queryParams)
		password =queryParams[1].encode('base64')
		Session.query(dbconnect.Users).\
				filter(dbconnect.Users.username == queryParams[0]).\
				update({'userpassword': password})
		Session.commit()
		Session.close()
		connection.connection.close()
		
		return "password updated successfully"


			
	
	
