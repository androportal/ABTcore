#import the database connector 
import dbconnect
#import the twisted modules for executing rpc calls and also to implement the server
from twisted.web import xmlrpc, server
#reactor from the twisted library starts the server with a published object and listens on a given port.
from twisted.internet import reactor
from sqlalchemy import or_
from sqlalchemy import not_
from sqlalchemy import and_
from sqlalchemy.orm import join

#inherit the class from XMLRPC to make it publishable as an rpc service.
class getaccountsbyrule(xmlrpc.XMLRPC):
	"""
	will retrive all the accounts on the basis of transaction rules
	"""
	def __init__(self):
		xmlrpc.XMLRPC.__init__(self)
	#note that all the functions to be accessed by the client must
	#have the xmlrpc_ prefix.  the client however will not use the
	#prefix to call the functions.

	def xmlrpc_getContraAccounts(self,client_id):
		"""
		Purpose: fetches the list of all accounts which are
		used in a contra voucher. Takes no arguments and
		returns list of accounts. If no accounts are found for
		contra then returns false.

		description: This function is called for populating
		the account's list with all the accounts for contra.
		Note that contra voucher only involves cash and bank
		accounts.
		
		"""
		statement = "select accountname\
		        from group_subgroup_account\
		        where subgroupname \
		        in ('Cash','Bank') order by accountname"
		result = dbconnect.engines[client_id].execute(statement).fetchall()
		print result
		
		
		if result == []:
			return False
		else:
			contraAccounts = []
			for row in result:
				contraAccounts.append(row[0])
			print contraAccounts
			return contraAccounts
	

	def xmlrpc_getJournalAccounts(self,client_id):
		"""
		Purpose: fetches the list of all accounts which are
		used in a journal voucher. Takes no arguments and
		returns list of accounts. If no accounts are found
		for journal then returns false.

		description: This function is called for populating
		the account's list with all the accounts for journal.
		Note that journal voucher involves all accounts,
		except cash and bank accounts.
		"""
		statement = "select accountname\
		        from group_subgroup_account\
		        where subgroupname is null\
		        or subgroupname != 'Cash' and subgroupname != 'Bank' order by accountname"
		result = dbconnect.engines[client_id].execute(statement).fetchall()
		if result == []:
			return False
		else:
			journalAccounts = []
			for row in result:
				journalAccounts.append(row[0])
			return journalAccounts

	def xmlrpc_getReceivableAccounts(self,queryParams,client_id):
		"""
		Purpose: fetches the list of all accounts which are
		used in a Receivable voucher.
		  
		Take one argument Cr or Dr and returns list of
		accounts according.  If no accounts are found for
		Receivable then returns false.  

		description: This function is called for populating
		the account's list with all the accounts for
		Receivable.  If type is "Cr" then it will returns
		account name list, except cash and bank accounts.  if
		"Dr" then return only cash and bank accounts.
		"""
		if  queryParams[0] == 'Cr':
			statement = "select accountname\
				from group_subgroup_account\
				where subgroupname is null\
				or subgroupname != 'Cash' and subgroupname != 'Bank' order by accountname"
				
			#result = dbconnect.engines[client_id].execute(statement).fetchall()
		else :
			statement = "select accountname\
				from group_subgroup_account\
				where subgroupname \
				in ('Cash','Bank') order by accountname"
			   
		result = dbconnect.engines[client_id].execute(statement).fetchall()
	
		if result == []:
			return False
		else:	 
			recievableAccounts = []
			for row in result:
				recievableAccounts.append(row[0])
			return recievableAccounts
			
	def xmlrpc_getPaymentAccounts(self,queryParams,client_id):
		'''
		Purpose: fetches the list of all accounts which are
		used in a Payment voucher.
		  
		Take one argument Cr or Dr and returns list of
		accounts accordingly.  If no accounts are found for
		payment then returns false.  

		Description: This function is called for populating
		the account's list with all the accounts for payment.
		If type is "Cr" then it will returns list of account
		names, except cash and bank accounts.  If type is
		"Dr", then returns only cash and bank accounts.
		'''
		
		if  queryParams[0] == 'Cr':
		 	statement = "select accountname\
				from group_subgroup_account\
				where subgroupname \
				in ('Cash','Bank') order by accountname"
			   
			#result = dbconnect.engines[client_id].execute(statement).fetchall()
		else:
			statement = "select accountname\
				from group_subgroup_account\
				where subgroupname is null\
				or subgroupname != 'Cash' and subgroupname != 'Bank' order by accountname"
				
		result = dbconnect.engines[client_id].execute(statement).fetchall()
		if result == []:
			return False
		else:
			paymentAccounts = []
			for row in result:
				paymentAccounts.append(row[0])
			return paymentAccounts
	
		
	def xmlrpc_getDebitNoteAccounts(self,queryParams,client_id):
		"""
		Purpose: get the list of accounts for debit note
		either for credit or debit side.  Function takes one
		parameter queryParams which is a list containing only
		one element, cr_dr_flag.  Returns list of accounts
		else false if not found.
		
		Description: returns a list of accounts pertaining to
		debit note.  If the input parameter in queryParams[0]
		is Cr then only the('Direct Expense','Fixed
		Assets','Indirect Expense')of accounts is returned
		else ('Sundry Creditors for Expense','Sundry Creditors
		for Purchase') of accounts is returned in form of
		list.
		
		"""   
		
		if  queryParams[0] == 'Cr':
		 	statement = "select accountname\
				from group_subgroup_account\
				where groupname \
				in ('Direct Expense','Fixed Assets','Indirect Expense') order by accountname"
				
		else:
			statement = "select accountname\
				from group_subgroup_account\
				where subgroupname \
				in ('Sundry Creditors for Expense','Sundry Creditors for Purchase') order by accountname"

		result = dbconnect.engines[client_id].execute(statement).fetchall()
		if result == []:
			return False
		else:
			debitnoteAccounts = []
			for row in result:
				debitnoteAccounts.append(row[0])
			return debitnoteAccounts
	

	def xmlrpc_getCreditNoteAccounts(self,queryParams,client_id):
		"""
		Purpose: gets the list of accounts for credit note
		either for credit or debit side.  Function takes one
		parameter queryParams which is a list containing only
		one element, cr_dr_flag.  Returns list of accounts
		else false if not found.

		Description: returns a list of accounts pertaining to
		credit note.  If the input parameter in queryParams[0]
		is Cr then only the ('Sundry Debtors') of accounts is
		returned else ('Direct Income','Indirect Income') of
		accounts is returned in form of list.
		
		"""   
		if  queryParams[0] == 'Cr':
		 	statement = "select accountname\
				from group_subgroup_account\
				where subgroupname \
				in ('Sundry Debtors') order by accountname"
				
		else:
			statement = "select accountname\
				from group_subgroup_account\
				where groupname \
				in ('Direct Income','Indirect Income') order by accountname"
				
		result = dbconnect.engines[client_id].execute(statement).fetchall()		
		if result == []:
			return False
		else:
			creditnoteAccounts = []
			for row in result:
				creditnoteAccounts.append(row[0])
			return creditnoteAccounts


	def xmlrpc_getSalesAccounts(self,queryParams,client_id):
		"""
		Purpose: gets the list of accounts for sales accounts
		either for credit or debit side.  Function takes one
		parameter queryParams which is a list containing only
		one element, cr_dr_flag.  Returns list of accounts
		else false if not found.

		description: returns a list of accounts pertaining to
		sales accounts.  If the input parameter in
		queryParams[0] is Cr then only the ('Direct
		Income','Indirect Income') of accounts is returned
		else ('Bank','Cash','Sundry Debtors') of accounts is
		returned in form of list.  .
		""" 
		if  queryParams[0] == 'Cr':
		 	statement = "select accountname\
				from group_subgroup_account\
				where groupname \
				in ('Direct Income','Indirect Income') order by accountname"
				
		else:
			statement = "select accountname\
				from group_subgroup_account\
				where subgroupname \
				in ('Bank','Cash','Sundry Debtors') order by accountname"
				  
		result = dbconnect.engines[client_id].execute(statement).fetchall()	
		if result == []:
			return False
		else:
			salesAccounts = []
			for row in result:
				salesAccounts.append(row[0])
			return salesAccounts
		
	def xmlrpc_getPurchaseAccounts(self,queryParams,client_id):
		"""
		Purpose: gets the list of accounts for purchase
		accounts either for credit or debit side.  Function
		takes one parameter queryParams which is a list
		containing only one element, cr_dr_flag.  Returns list
		of accounts else false if not found.

		description: returns a list of accounts pertaining to
		purchase accounts.  If the input parameter in
		queryParams[0] is Cr then only the
		('Bank','Cash','Sundry Creditors for Expense','Sundry
		Creditors for Purchase') of accounts is returned else
		('Direct Expense','Indirect Expense') of accounts is
		returned in form of list.
		
		"""  
		if  queryParams[0] == 'Cr':
		 	statement = "select accountname\
				from group_subgroup_account\
				where subgroupname \
				in ('Bank','Cash','Sundry Creditors for Expense','Sundry Creditors for Purchase') order by accountname"
				
		else:
			statement = "select accountname\
				from group_subgroup_account\
				where groupname \
				in ('Direct Expense','Indirect Expense') order by accountname" 
				
		result = dbconnect.engines[client_id].execute(statement).fetchall()
		if result == []:
			return False
		else:
			purchaseAccounts = []
			for row in result:
				purchaseAccounts.append(row[0])
			return purchaseAccounts

	
	def xmlrpc_getSalesReturnAccounts(self,queryParams,client_id):
		"""
		Purpose: gets the list of accounts for salesreturn
		either for credit or debit side.  Function takes one
		parameter queryParams which is a list containing only
		one element, cr_dr_flag.  Returns list of accounts
		else false if not found.

		description: returns a list of accounts pertaining to
		sales return accounts.  If the input parameter in
		queryParams[0] is Cr then only the ('Sundry Debtors')
		of accounts is returned else ('Direct
		Expense','Indirect Expense') of accounts is returned
		in form of list.
		
		"""   
		if  queryParams[0] == 'Cr':
		 	statement = "select accountname\
				from group_subgroup_account\
				where subgroupname \
				in ('Sundry Debtors') order by accountname"
				
		else:
			statement = "select accountname\
				from group_subgroup_account\
				where groupname \
				in ('Direct Expense','Indirect Expense') order by accountname"
		result = dbconnect.engines[client_id].execute(statement).fetchall()
		if result == []:
			return False
		else:
			salesreturnAccounts = []
			for row in result:
				salesreturnAccounts.append(row[0])
			return salesreturnAccounts
		
		
	def xmlrpc_getPurchaseReturnAccounts(self,queryParams,client_id):
		"""
		Purpose: gets the list of accounts for purchases
		return either for credit or debit side.  Function
		takes one parameter queryParams which is a list
		containing only one element, cr_dr_flag.  Returns list
		of accounts else false if not found.

		description: returns a list of accounts pertaining to
		purchases return.  If the input parameter in
		queryParams[0] is Cr then only the('Direct
		Income','Indirect Income'of accounts is returned else
		('Sundry Creditors for Expense','Sundry Creditors for
		Purchase') of accounts is returned in form of list.
		
		"""  
		if  queryParams[0] == 'Cr':
		 	statement = "select accountname\
				from group_subgroup_account\
				where groupname \
				in ('Direct Income','Indirect Income') order by accountname"
				
		else:
			statement = "select accountname\
				from group_subgroup_account\
				where subgroupname \
				in ('Sundry Creditors for Expense','Sundry Creditors for Purchase')  order by accountname" 
		result = dbconnect.engines[client_id].execute(statement).fetchall()
		if result == []:
			return False
		else:
			purchasereturnAccounts = []
			for row in result:
				purchasereturnAccounts.append(row[0])
			return purchasereturnAccounts
			
			
		
