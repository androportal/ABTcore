#import the database connector and functions for stored procedure.
import dbconnect
#import the twisted modules for executing rpc calls and also to implement the server
from twisted.web import xmlrpc, server
#reactor from the twisted library starts the server with a published object and listens on a given port.
from twisted.internet import reactor
import xmlrpclib
import rpc_account
from datetime import datetime, time

from sqlalchemy import func
from multiprocessing.connection import Client
from rpc_organisation import organisation


#inherit the class from XMLRPC to make it publishable as an rpc service.
class transaction(xmlrpc.XMLRPC):
	def __init__(self):

		xmlrpc.XMLRPC.__init__(self)
		'''
		note that all the functions to be accessed by the client must have the xmlrpc_ prefix.
		the client however will not use the prefix to call the functions.
		'''
	
	def xmlrpc_setTransaction(self,queryParams_master,queryParams_details,client_id):
		"""
		Purpose: adds a new voucher in the database given its reference number 
		and transaction details (dr and cr), along with narration and the date.
		This function is used to create a new voucher.  
		The entire transaction is recorded in terms of Dr and Cr and the respected amounts.
		The function call 3 funtions from same file rpc_transation.py
		1 . xmlrpc_getProjectcodeByProjectName  
		2 . xmlrpc_setVoucherMaster
		3 . xmlrpc_setVoucherDetails 
		
		and call 1 function from rpc_account.py "to get accountcode by accountname"
		1 . xmlrpc_getAccountCodeByAccountName
		
		queryParams_master list will contain :
		* reference Number
		* the actual transaction date
		* Voucher type
		* project name
		* Narration
		
		queryParams_details list will contain :
		
		* DrCr flag,
		* AccountName (from which account code will be procured by the getProjectcodeByProjectName )
		* the amount for the respective account.
		The function returns "success" .
		"""
		projectcode = self.xmlrpc_getProjectcodeByProjectName([str(queryParams_master[3])],client_id)
		
		params_master = [queryParams_master[0],queryParams_master[1],queryParams_master[2],projectcode,queryParams_master[4]]
		print "params master"
		print params_master
		vouchercode = self.xmlrpc_setVoucherMaster(params_master,client_id)
		
		print "query for masters is successful and voucher code is " + str(vouchercode)
		for detailRow in queryParams_details:
			
			account = rpc_account.account();
			accountcode = account.xmlrpc_getAccountCodeByAccountName([detailRow[1]],client_id);
			params_details = [vouchercode,str(detailRow[0]),str(accountcode),float(detailRow[2])]
			self.xmlrpc_setVoucherDetails(params_details,client_id)
		return 1
	
	def xmlrpc_setVoucherMaster(self,queryParams,client_id):
		"""
		Purpose: adds a new voucher in the database given its reference number 
		and transaction details (dr and cr), along with narration and the date.
		This function is used to create a new voucher.  
		The entire transaction is recorded in terms of Dr and Cr and the respected amounts.
		queryParams list will contain :
		* reference Number
		* the actual transaction date
		* Voucher type
		* project name
		* Narration
		It will return vouchercode
		"""
		print "into setVoucher"
		# execute here
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		VoucherCode = Session.query(func.count(dbconnect.VoucherMaster.vouchercode)).scalar()
		if VoucherCode == None:
			VoucherCode = 0
			VoucherCode = VoucherCode + 1
		else:
			VoucherCode = VoucherCode + 1
		print VoucherCode
		system_date = datetime.today() # sqlite take datetime or date object for TIMESTAMP
		reffdate =  datetime.strptime(str(queryParams[1]),"%d-%m-%Y")
		# add all values in the account table
		print "quet"
		print queryParams
		Session.add(dbconnect.VoucherMaster(\
			VoucherCode,queryParams[0],system_date,reffdate,queryParams[2],1,queryParams[3],queryParams[4]))
			
		Session.commit()
		Session.close()
                connection.connection.close()
		
		return VoucherCode	
		
	def xmlrpc_getProjectcodeByProjectName(self,queryParams,client_id):
		"""
		Purpose: function to get projectcode acouding to projectname
		input parameters: It will take only one input projectname
		output parameters : it will return project if projectname match
			else returns 0
		"""
		# execute here
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		result = Session.query(dbconnect.Projects.projectcode).\
		      filter(dbconnect.Projects.projectname == queryParams[0]).first()
		Session.close()
		connection.connection.close()
		projectCode = result[0]
		if projectCode == None:
			return 0
		else:
			return projectCode 
			
	def xmlrpc_setVoucherDetails(self,queryParams,client_id):
	
		"""
		Purpose: It set voucher details which will be use in setTransaction
		Input parameters : 
			queryParams_details list will contain :
		
			* Dr or Cr flag,
			* AccountName
			* the amount for the respective account.
		Output parameters : 
			It returns "success " as string 
		"""
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		Session.add(dbconnect.VoucherDetails(\
			queryParams[0],queryParams[1],queryParams[2],queryParams[3]))
			
		Session.commit()
		Session.close()
                connection.connection.close()
                return "success"
		
		
