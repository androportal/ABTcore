import dbconnect
from twisted.web import xmlrpc, server
from twisted.internet import reactor
from modules import blankspace
from datetime import datetime,time

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
		
		queryParams = blankspace.remove_whitespaces(queryParams)
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		username = queryParams[0]
		password = blankspace.remove_whitespaces([queryParams[1].encode('base64').rstrip()])
		
		user_role = queryParams[3]
		Session.add(dbconnect.Users(\
				username,password[0],queryParams[2],user_role,queryParams[4],queryParams[5],"",""))
		Session.commit()
		print "sign up"
		return "Sign up sccessfull"
		
	def xmlrpc_getUserNemeOfManagerRole(self,client_id):
		'''
		* Purpose:
			- It will provides list of all manager's present
			  in user table
		 
		* Output
		       - it returns list of  usernames
		'''
		
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		
		result = Session.query((dbconnect.Users.username),(dbconnect.Users.login_time),(dbconnect.Users.logout_time)).\
						filter(dbconnect.Users.userrole == "manager").all()
		Session.close()
		connection.connection.close()
		resultList = []
		if result != []:
			for row in result:
				userlist = []
				userlist.append(row.username)
				userlist.append(row.login_time)
				userlist.append(row.logout_time)
				resultList.append(userlist)
			print "user list"
			print resultList
   			return resultList
		else:
			return []
	
	def xmlrpc_getUserNemeOfOperatorRole(self,client_id):
		'''
		* Purpose:
			- It will provides list of all operator's present
			  in user table
		 
		* Output
		       - it returns list of usernames
		'''
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		
		result = Session.query(dbconnect.Users.username,(dbconnect.Users.login_time),(dbconnect.Users.logout_time)).\
						filter(dbconnect.Users.userrole == "operator").all()
		Session.close()
		connection.connection.close()
		resultList = []
		if result != []:
			for row in result:
				userlist = []
				userlist.append(row.username)
				userlist.append(row.login_time)
				userlist.append(row.logout_time)
				resultList.append(userlist)
			print "user list"
			print resultList
   			return resultList
		else:
			return result
					
			
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
		password = blankspace.remove_whitespaces([queryParams[1].encode('base64').rstrip()])
		result = Session.query(dbconnect.Users).filter(dbconnect.Users.username == queryParams[0]).\
							filter(dbconnect.Users.userpassword == password[0]).\
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
			- if given username exist the return ``True``
			  else return ``False``
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
			
	def xmlrpc_changeUserName(self,queryParams,client_id):
		'''
		* Purpose:
			- It will facilitate user to change username 
			  based on there old_username and password 
		* Input: 
			- [old_username,new_username,password,userrole]
			
		* Output:
		        - return ``False`` if given user is not present with old_password,userrole
                          else it update username and return ``True`` 
		
		'''
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
                queryParams = blankspace.remove_whitespaces(queryParams)
                password = blankspace.remove_whitespaces([queryParams[2].encode('base64').rstrip()])
                result = Session.query(dbconnect.Users.userid).filter(dbconnect.Users.username == queryParams[0]).\
                                                       filter(dbconnect.Users.userpassword == password[0]).\
                                                       filter(dbconnect.Users.userrole == queryParams[3]).first()
                
                if result == None:
                	Session.close()
               		connection.connection.close()
               		return False
               	else:
               		
                        result = Session.query(dbconnect.Users).filter(dbconnect.Users.userid == result.userid).\
               		 					update({'username':queryParams[1]})
               
               		Session.commit()
              		Session.close()
               		connection.connection.close()
               		return True                               

	def xmlrpc_setLoginLogoutTiming(self,queryParams,client_id):
		'''
		* Purpose: 
			- function to update login and logout timing of user
			  
		* Input:
			- [username , userrole, login_time, logout_time]
		* Output:
			- return ``True``
		'''
		queryParams = blankspace.remove_whitespaces(queryParams)
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		
		login_time =  str(datetime.strptime(str(queryParams[2]),"%d-%m-%Y %H:%M:%S"))
		logout_time =  str(datetime.strptime(str(queryParams[3]),"%d-%m-%Y %H:%M:%S"))
		
       		#update
                result = Session.query(dbconnect.Users).filter(dbconnect.Users.username == queryParams[0]).\
						filter(dbconnect.Users.userrole == queryParams[1]).\
       		 				update({'login_time':login_time,'logout_time':logout_time})
               
               	Session.commit()						
		Session.close()
		connection.connection.close()
		return True
		
		
	def xmlrpc_getLastLoginTiming(self,queryParams,client_id):
		'''
		* Purpose: 
			- function to get the last login timing of user
			  
		* Input:
			- [username , userrole]
		* Output:
			- return time
		'''
		queryParams = blankspace.remove_whitespaces(queryParams)
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		
                result = Session.query(dbconnect.Users).\
						filter(dbconnect.Users.userrole == queryParams[0]).\
						filter(dbconnect.Users.username == queryParams[1]).\
						first()
               						
		Session.close()
		connection.connection.close()
		if result != None:
			 
   			return result.login_time
		else:
			return []

	def xmlrpc_changePassword(self,queryParams,client_id):
               '''
               * purpose:
                       - It will provide to update password based on username, old password and userrole
               
               * Input:
                       - [username,old_password,new_password,userrole]
                       
               * Output:
                       - return ``False`` if given user is not present with old_password,userole
                         else it update new_password and return ``True``
                       
               '''
               connection = dbconnect.engines[client_id].connect()
               Session = dbconnect.session(bind=connection)
               queryParams = blankspace.remove_whitespaces(queryParams)
               
               old_password = blankspace.remove_whitespaces([queryParams[1].encode('base64').rstrip()])
               new_password = blankspace.remove_whitespaces([queryParams[2].encode('base64').rstrip()])
               result = Session.query(dbconnect.Users.userid).filter(dbconnect.Users.username == queryParams[0]).\
                                                       filter(dbconnect.Users.userpassword == old_password[0]).\
                                                       filter(dbconnect.Users.userrole == queryParams[3]).first()
                   
                                                
               if result == None:
               		Session.close()
               		connection.connection.close()
               		return False
               else:
               		
               		result = Session.query(dbconnect.Users).filter(dbconnect.Users.userid == result.userid).\
               		 					update({'userpassword': new_password[0]})
               
               		Session.commit()
              		Session.close()
               		connection.connection.close()
               		return True
               
	def xmlrpc_AdminForgotPassword(self,queryParams,client_id):
		'''
		* purpose:
		       - this function is to check if userrole ``admin`` is pesent
			 and provide access to organisation by cross checking
			 security question and anwer provided in case of forgotten password.
		* Input:
		       - [question , answer , userrole]
		       
		* Output:
		       - if ``admin`` then return ``true`` else retrun ``false``
		'''

		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		role_exist = Session.query(dbconnect.Users).filter(dbconnect.Users.userrole == "admin").\
								first()                        

		if role_exist != None:
		       result = Session.query(dbconnect.Users).filter(dbconnect.Users.question == queryParams[0]).\
				                       filter(dbconnect.Users.answer == queryParams[1]).\
				                       filter(dbconnect.Users.userrole == queryParams[2]).first()
		Session.close()
		connection.connection.close()
		if result == None:
		       return False
		else:        
		       
		       return True
         

	def xmlrpc_resetPassword(self,queryParams,client_id):
               '''
               * purpose:
                       - It will provide to reset password based on username, old password and userrole
               
               * Input:
                       - [username,new_password,userrole]
                       
               * Output:
                       - return ``False`` if given user is not present with old_password,userole
                         else it update new_password and return ``True``
                       
               '''
               connection = dbconnect.engines[client_id].connect()
               Session = dbconnect.session(bind=connection)
               queryParams = blankspace.remove_whitespaces(queryParams)
               
              
               new_password = blankspace.remove_whitespaces([queryParams[1].encode('base64').rstrip()])
               result = Session.query(dbconnect.Users.userid).filter(dbconnect.Users.username == queryParams[0]).\
                                                       filter(dbconnect.Users.userrole == queryParams[2]).first()
                   
                                                
               if result == None:
               		Session.close()
               		connection.connection.close()
               		return False
               else:
               		
               		result = Session.query(dbconnect.Users).filter(dbconnect.Users.userid == result.userid).\
               		 					update({'userpassword': new_password[0]})
               
               		Session.commit()
              		Session.close()
               		connection.connection.close()
               		return True
			
	
	
