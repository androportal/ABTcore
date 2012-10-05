from twisted.web import xmlrpc, server
from twisted.internet import reactor
from time import strftime
import pydoc
from datetime import datetime, time
from time import strftime
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func
from decimal import *
from sqlalchemy import or_
import rpc_groups
import dbconnect

class account(xmlrpc.XMLRPC):
	
	"""class name is aacount which having different store procedures"""
	def __init__(self):
		xmlrpc.XMLRPC.__init__(self)
		
	def xmlrpc_setAccount(self, queryParams, client_id):
		"""
		Purpose: Adds an account in the account table, under a selected group and optionally a subgroup.  
			account code is either auto generated or entered by the user
			Depending on the preference choosen by the user.
		description: This function inserts a row in the account table.
		          
		Function takes one parameter named queryParams which is a list containing,
		* queryParams[groupname,subgroupflag,subgroupname,accountname,accountcodetype,openingbalance,currentBalance,suggestedcode]
		Returns True
		""" 
		group = rpc_groups.groups()
		sp_params = [queryParams[0], queryParams[3]] # create sp_params list comtaining groupname , accountname 
		if queryParams[2] == "": # check for the 

			if queryParams[1] == "No Sub-Group":
				print "we are not taking subgroup "
				sp_params.append("null")
			else:
				sp_params.append(queryParams[1])
		if queryParams[1] == "Create New Sub-Group" :
			print "there is a new subgroup created"
			sp_params.append(queryParams[2])
		if queryParams[0] == "Direct Income" or queryParams[0] == "Direct Expense" or queryParams[0] == "Indirect Income" or queryParams[0] == "Indirect Expense":
			sp_params.append(0)
		else:
			sp_params.append(queryParams[5])
		now = datetime.today() # sqlite take datetime or date object for TIMESTAMP
		#date = now.strftime("%Y-%m-%d %H:%M:%S")
		sp_params.append(now)
		sp_params.append(sp_params[3])
		if queryParams[7] == "":
			sp_params.append("null")
		else:
			sp_params.append(queryParams[7])
		#execute here
		print "here is what we send to the execproc as a param list "
		print sp_params
		
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		group_code = group.xmlrpc_getGroupCodeByGroupName([sp_params[0]], client_id); 
 		if sp_params[6] == 'null':
 			maxcode = Session.query(func.count(dbconnect.Account.accountcode)).scalar()
 			print "maxcode " 
 			print maxcode
 			if maxcode == None:
				maxcode = 0
				suggested_code = int(maxcode) + 1;
			else:
				suggested_code = int(maxcode) + 1;
				
 			 
 			print "suggested code " 
 			print suggested_code
		if sp_params[2] == 'null':
			print "inside null"
			print [suggested_code,group_code[0],"",sp_params[1],sp_params[3],sp_params[4],sp_params[5]]
			Session.add(dbconnect.Account(suggested_code,group_code[0],"",sp_params[1],sp_params[3],sp_params[4],sp_params[5]))
			Session.commit()
		else:
			subgroup_code =  group.xmlrpc_getSubGroupCodeBySubGroupName([sp_params[2]], client_id)
			if subgroup_code == False :
   				group.xmlrpc_setSubGroup([sp_params[0],sp_params[2]],client_id); 
   				subgroup_code =  group.xmlrpc_getSubGroupCodeBySubGroupName([sp_params[2]], client_id); 
   				Session.add(dbconnect.Account(suggested_code,group_code[0],subgroup_code[0],sp_params[1],sp_params[3],sp_params[4],sp_params[5]))
   				Session.commit()
                Session.close()
                connection.connection.close()
		return "success"
