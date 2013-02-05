
import dbconnect 
from twisted.web import xmlrpc, server 
from twisted.internet import reactor 
from sqlalchemy.orm import join
from decimal import *
from sqlalchemy import or_ , func , and_
from modules import blankspace

class groups(xmlrpc.XMLRPC):
	'''
	+ This is the class ``groups`` provides the information about tha ``groups`` and ``subgroups``
	  as per accounting rule .
	+ we already have some ``groups`` and ``subgroups`` for the given organisation while deploying.
	  or creating organisation.
	+ to know present groupnames and subgroupnames see ``rpc_Deploy`` function from ``rpc_main`` module.
	+ import liabraries as needed.
	
	'''
	def __init__(self):
		xmlrpc.XMLRPC.__init__(self)
	
	
	def xmlrpc_setSubGroup(self,queryParams,client_id):
		'''
		* Purpose:
			- used ``subGroups`` table to query .
			- function for adding new subgroups in table subgroups
			
		* Input: 	
			- groupname(datatype:text), subgroupname(datatype:text) , client_id (datatype:integer)
			
		* Output: 
			- returns 1 when successful, 0 when subgroupname(datatype:text) is null
		  	- When successful it returns 1 otherwise it returns 0. 
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
		* Purpose: 
			- function to get all groups present in the groups table
			- querys the ``Groups`` table,it retrieves all rows of groups table based on groupname.
			- when successful it returns the list of lists
			- list contain each row that are retrived from groups table 
			
		* Input:
			- client_id(datatype:integer) from client side.
			
		* Output: 
			- returns list containing groupcode(datatype:integer),groupname(datatype:text),groupdescription(datatype:text).
		
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
		* Purpose:
			- function for extracting all rows of view_group_subgroup based on groupname
			- querys the ``view_group_subgroup`` which is created based on the account,
			  subgroups and groups table.	
			- it retrieves all rows of view_group_subgroup based on groupname order by subgroupname.
		
		* Input:	
			- list containing groupname(datatype:text)
			
		* Output: 
			- When successful it returns the list of lists in which 	
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
		* Purpose:
			- function for extracting groupcpde of group based on groupname.
			- query to retrive groupcode requested groupname by client.
		
		* Input:
			- groupname(datatype:text) , client_id(datatype:integer)
		
		* Output:
			- returns list containing groupcode if its not None else will return false.
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
		* Purpose:
			- function for extracting subgroupcpde of group based on subgroupname
			- query the subgroup table to retrive subgroupcode for reqested subgroupname 
			
		* Input:
			- subgroupname(datatype:text),client_id(datatype:integer)
			
		* Output:
			- returns list containing subgroupcode if its not None else will return false.
			
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
		* Purpose:
			- function for extracting groupname from group table by account name
			
		* Input:
			- accountname
			
		* Output:
			- groupname
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
		* Purpose:
			- checks if the new subgroup typed by the user already exists.
			- This will validate and prevent any duplication.
			- The function takes queryParams as its parameter and contains one element, 
			  the subgroupname as string.
		
		* Input:
			- subgroupname(datatype:text)
		
		* Output:
			- returns ``1`` if the subgroup exists else ``0``.
		'''
		queryParams = blankspace.remove_whitespaces(queryParams)	
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		result = Session.query(func.count(dbconnect.subGroups.subgroupname)).\
		      filter((func.lower(dbconnect.subGroups.subgroupname)) == queryParams[0].lower()).scalar()
		Session.close()
		connection.connection.close()
	
		if result == 0:
			return "0"
		else:
			return "1"
			
	
