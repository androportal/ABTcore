
import dbconnect #import the database connector and functions for stored procedure.
from twisted.web import xmlrpc, server #import the twisted modules for executing rpc calls and also to implement the server
from twisted.internet import reactor #reactor from the twisted library starts the server with a published object and listens on a given port.
from sqlalchemy.orm import join
from decimal import *
from sqlalchemy import or_

#note that all the functions to be accessed by the client must have the xmlrpc_ prefix.
#the client however will not use the prefix to call the functions. 

class groups(xmlrpc.XMLRPC): #inherit the class from XMLRPC to make it publishable as an rpc service.
	def __init__(self):
		xmlrpc.XMLRPC.__init__(self)
	
	
	def xmlrpc_setSubGroup(self,queryParams,client_id):
		'''
		xmlrpc_setSubGroup : Purpose 
			function for adding new subgroups in table subgroups	
			Parameters : groupname(datatype:text), subgroupname(datatype:text)
			Returns : returns 1 when successful, 0 when failed
			Description : Adds new subgroup to the database. 
					When successful it returns 1 otherwise it returns 0. 
		'''	
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		res = Session.query(dbconnect.Groups).filter(dbconnect.Groups.groupname == queryParams[0]).first()
		groupcode = res.groupcode
		result = Session.add_all([dbconnect.subGroups(groupcode,queryParams[1])])
		Session.close()
		connection.connection.close()
		if queryParams[1]=="null":
			return "0"
		else:
			return "1"
		
	
	def xmlrpc_getAllGroups(self,client_id):
		'''
		def xmlrpc_getAllGroups	: purpose
			input parameters : client_id from client side
			output : returns list containing group name.
		'''
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		res = Session.query(dbconnect.Groups).order_by(dbconnect.Groups.groupname).all()
		Session.close()
		connection.connection.close()
		print res
		if res == []:
			return False
		else:
			result = []
			for i in range(0,len(res)):
				result.append([res[i].groupcode, res[i].groupname, res[i].groupdesc])
			print result
			return result
	
	def xmlrpc_getGroupByName(self,queryParams,client_id):
		'''
		def xmlrpc_getGroupByName: purpose
			input parameters : grupname , client_id from client side
			output : returns list containing group name.
		'''
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		res = Session.query(dbconnect.Groups).filter(dbconnect.Groups.groupname == queryParams[0]).order_by(dbconnect.Groups.groupcode).first()
		Session.close()
		connection.connection.close()
		if res != None:
			return [res.groupcode, res.groupname, res.groupdesc]
		else:
			return False
	
	
	def xmlrpc_getGroupCodeByName(self,queryParams,client_id):
		'''
		xmlrpc_getGroupCodeByName : purpose
			input parameters : client_id from client side
			output : returns list containing groupcode if its not None else will return false.
		'''
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		res = Session.query(dbconnect.Groups.groupcode).filter(dbconnect.Groups.groupname == queryParams[0]).first()
		Session.close()
		connection.connection.close()
		if res != None:
			return res
		else:
			return False

	
	def xmlrpc_getGroupNameByAccountName(self,queryParams,client_id):
		'''
		xmlrpc_getGroupNameByAccountName :purpose 
			function for extracting groupname from group table by account name
			i/p parameters : accountname
			o/p parameters : groupname
		'''	
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		res = Session.query(dbconnect.Groups).select_from(join(dbconnect.Groups,dbconnect.Account)).filter(dbconnect.Account.accountname == queryParams[0]).first()
		Session.close()
		connection.connection.close()
		if res != None:
			return [res.groupname]
		else:
			return False
	

	def xmlrpc_getSubGroupByName(self,queryParams,client_id):
		'''
		xmlrpc_getSubGroupByName :Purpose 
			function for extracting data from subgroup table by namewise 
			i/p parameters : subgroupname
			o/p parameters :subgroupcode	
		'''	
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		res = Session.query(dbconnect.subGroups).filter(dbconnect.subGroups.subgroupname == queryParams[0]).order_by(dbconnect.subGroups.groupcode).first()
		Session.close()
		connection.connection.close()
		if res != None:
			return res.subgroupcode
		else:
			return False
	
	
	def xmlrpc_subgroupExists(self,queryParams,client_id):	
		'''
		xmlrpc_subgroupExists:purpose: 
			Checks if the new subgroup typed by the user already exists.
			This will validate and prevent any duplication.
			Description: The function takes queryParams as its parameter and contains one element, the subgroupname as string.
			Returns True if the subgroup exists and False otherwise
		'''	
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		res = Session.query(func.count(dbconnect.subGroups.subgroupname)).filter(dbconnect.subGroups.subgroupname == queryParams).all()
		Session.close()
		connection.connection.close()
		print res
		if res == []:
			return "0"
		else:
			return "1"

	
