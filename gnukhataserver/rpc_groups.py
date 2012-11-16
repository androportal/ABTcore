
import dbconnect #import the database connector and functions for stored procedure.
from twisted.web import xmlrpc, server #import the twisted modules for executing rpc calls and also to implement the server
from twisted.internet import reactor #reactor from the twisted library starts the server with a published object and listens on a given port.
from sqlalchemy.orm import join
from decimal import *
from sqlalchemy import or_ , func , and_
import rpc_main
from modules import blankspace
#note that all the functions to be accessed by the client must have the xmlrpc_ prefix.
#the client however will not use the prefix to call the functions. 

class groups(xmlrpc.XMLRPC): #inherit the class from XMLRPC to make it publishable as an rpc service.
	def __init__(self):
		xmlrpc.XMLRPC.__init__(self)
	
	
	def xmlrpc_setSubGroup(self,queryParams,client_id):
		'''
		Purpose :function for adding new subgroups in table subgroups	
		Parameters : groupname(datatype:text), subgroupname(datatype:text) , client_id (datatype:integer)
		Returns : returns 1 when successful, 0 when subgroupname(datatype:text) is null
		Description : Adds new subgroup to the database. 
			When successful it returns 1 otherwise it returns 0. 
		'''
		queryParams = blankspace.remove_whitespaces(queryParams)
		# call getGroupCodeByGroupName func to get groupcode
		result = self.xmlrpc_getGroupCodeByGroupName([queryParams[0]],client_id) 
		# call getSubGroupCodeBySubGroupName fun to get subgroupcode
		#result = self.xmlrpc_getSubGroupCodeBySubGroupName([queryParams[1]],client_id) 
		if result != None:
			group_code = result[0]
			#print group_code
			connection = dbconnect.engines[client_id].connect()
                	Session = dbconnect.session(bind=connection)
                	Session.add_all([dbconnect.subGroups(group_code,queryParams[1])])
                	Session.commit()
                	Session.close()
                	connection.connection.close()
                	if queryParams[1]=="null":
				return "0"
			else:
				return "1"
                else:
			return []
		
	def xmlrpc_getAllGroups(self,client_id):
		'''
		purpose : function to get all groups present in the groups table
		input parameters : client_id(datatype:integer) from client side
		output : returns list containing group groupcode(datatype:integer),
			          groupname(datatype:text),groupdescription(datatype:text).
		Description : Querys the Groups table.
			      It retrieves all rows of groups table  based on groupname.
			      When successful it returns the list of lists , 
			      in which each list contain each row that are retrived from groups table 
			      otherwise it returns false.
		'''
		
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		result = Session.query(dbconnect.Groups).order_by(dbconnect.Groups.groupname).all()
		Session.close()
		connection.connection.close()
		#print result
		if result == []:
			return result
		else:
			grouplist = []
			for i in range(0,len(result)):
				grouplist.append([result[i].groupcode, result[i].groupname, result[i].groupdesc])
			#print grouplist
			return grouplist
			
	def xmlrpc_getSubGroupsByGroupName(self,queryParams,client_id):
		'''
		Purpose :function for extracting all rows of view_group_subgroup based on groupname	
		Parameters : QueryParams, list containing groupname(datatype:text)
		Returns : List of all subgroups when successful, else list containing strings 
		Description : Querys the view_group_subgroup which is created based on the account ,subgroups and groups table.
			      It retrieves all rows of view_group_subgroup based on groupname order by subgroupname.
			      When successful it returns the list of lists in which 
			      each list contain each row that are retrived from view otherwise 
			      it returns list in which two default subgroup strings. 
		
		'''
		queryParams = blankspace.remove_whitespaces(queryParams)
		statement = "select subgroupname\
			from view_group_subgroup\
			where groupname ='"+queryParams[0]+"'\
			order by subgroupname"
			
		result=dbconnect.engines[client_id].execute(statement).fetchall()
		subgrouplist = []
		if result == []:
			subgrouplist.append("No Sub-Group")
			subgrouplist.append("Create New Sub-Group")
			#print subgrp
			return subgrouplist
		else:
			subgrouplist.append("No Sub-Group")
			for l in range(0,len(result)): 
				subgrouplist.append(result[l][0])
			subgrouplist.append("Create New Sub-Group")
			#print subgrp
			return subgrouplist
		
			
	def xmlrpc_getGroupCodeByGroupName(self,queryParams,client_id):
		'''
		 purpose: function for extracting groupcpde of group based on groupname
			
			input parameters : groupname(datatype:text) , client_id(datatype:integer)
			output : returns list containing groupcode if its not None else will return false.
			Description : query to retrive groupcode requested groupname  by client
		'''
		queryParams = blankspace.remove_whitespaces(queryParams)
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		result = Session.query(dbconnect.Groups).\
		      filter(dbconnect.Groups.groupname == queryParams[0]).\
		      first()
		Session.close()
		connection.connection.close()
		if result != None:
			
			return [result.groupcode]
		else:
			return []
			
	def xmlrpc_getSubGroupCodeBySubGroupName(self,queryParams,client_id):
		'''
		purpose: function for extracting subgroupcpde of group based on subgroupname
			input parameters : subgroupname(datatype:text) , client_id(datatype:integer)
			output : returns list containing subgroupcode if its not None else will return false.
			Description : query the subgroup table to retrive subgroupcode for reuested subgroupname 
		'''
		queryParams = blankspace.remove_whitespaces(queryParams)
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		result = Session.query(dbconnect.subGroups).\
		      filter(dbconnect.subGroups.subgroupname == queryParams[0]).\
		      first()
		Session.close()
		connection.connection.close()
		if result != None:
			
			return [result.subgroupcode]
		else:
			return []
			
	def xmlrpc_getGroupNameByAccountName(self,queryParams,client_id):
		'''
		xmlrpc_getGroupNameByAccountName :purpose 
			function for extracting groupname from group table by account name
			i/p parameters : accountname
			o/p parameters : groupname
		'''	
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		result = Session.query(dbconnect.Groups).select_from(join(dbconnect.Groups,dbconnect.Account)).\
			filter(and_(dbconnect.Account.accountname == queryParams[0],\
			dbconnect.Groups.groupcode == dbconnect.Account.groupcode)).\
			first()
		Session.close()
		connection.connection.close()
		if result != None:
			return [result.groupname]
		else:
			return []
			
	def xmlrpc_subgroupExists(self,queryParams,client_id):	
		'''
		purpose: Checks if the new subgroup typed by the user already exists.
		input parameters : subgroupname(datatype:text)	
		output : Returns True if the subgroup exists and False otherwise
		Description: This will validate and prevent any duplication.
		The function takes queryParams as its parameter and contains one element, the subgroupname as string.
		'''
		queryParams = blankspace.remove_whitespaces(queryParams)	
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		result = Session.query(func.count(dbconnect.subGroups.subgroupname)).\
		      filter(dbconnect.subGroups.subgroupname == queryParams[0]).scalar()
		Session.close()
		connection.connection.close()
		print "subgroup exist"
		print result
		if result == 0:
			return "0"
		else:
			return "1"
			
	'''			
	def xmlrpc_getGroupByName(self,queryParams,client_id):
		
		def xmlrpc_getGroupByName: purpose
			input parameters : grupname , client_id from client side
			output : returns list containing group name.
		
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		result = Session.query(dbconnect.Groups).filter(dbconnect.Groups.groupname == queryParams[0]).\
		order_by(dbconnect.Groups.groupcode).first()
		Session.close()
		connection.connection.close()
		if result != None:
			return [result.groupcode, result.groupname, result.groupdesc]
		else:
			return False
	
	
	

	
	
	

	def xmlrpc_getSubGroupByName(self,queryParams,client_id):
		
		xmlrpc_getSubGroupByName :Purpose 
			function for extracting data from subgroup table by namewise 
			i/p parameters : subgroupname
			o/p parameters :subgroupcode	
		
		print queryParams,client_id
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		result = Session.query(dbconnect.subGroups).filter(dbconnect.subGroups.subgroupname == queryParams[0]).\
		order_by(dbconnect.subGroups.groupcode).first()
		Session.close()
		connection.connection.close()
		if result != None:
			return result.subgroupcode
		else:
			return False'''
	
	
	

	
