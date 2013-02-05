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
	+ This file provides accoutnames as per transaction rule.
	+ In acounting there are different type of voucher and each of 
	  them has different rule 
	"""
	def __init__(self):
		xmlrpc.XMLRPC.__init__(self)
	#note that all the functions to be accessed by the client must
	#have the xmlrpc_ prefix.  the client however will not use the
	#prefix to call the functions.

	def xmlrpc_getContraAccounts(self,client_id):
		"""
		Purpose: 
			- fetches the list of all accounts which are
			  used in a ``contra voucher``. 
			- takes no arguments and returns list of accounts. 
			  if no accounts are found for contra then returns false.
			- this function is called for populating
			  the account's list with all the accounts for contra.
			- Note that contra voucher only involves cash and bank
			  accounts.
			  
		* Input:
		 	- no input parameters
		 	
		* Output:
			- return list containing accountname which comes under
			  ``cash`` and ``bank`` 
		"""
		statement = "select accountname\
		        from group_subgroup_account\
		        where subgroupname \
		        in ('Cash','Bank') order by accountname"
		result = dbconnect.engines[client_id].execute(statement).fetchall()
		
		if result == []:
			return result
		else:
			contraAccounts = []
			for row in result:
				contraAccounts.append(row[0])
			
			return contraAccounts
	

	def xmlrpc_getJournalAccounts(self,client_id):
		"""
		* Purpose:
			- fetches the list of all accounts which are
			  used in a ``journal voucher``. 
			- takes no arguments and returns list of accounts. 
			- if no accounts are found for journal then returns false.
			- this function is called for populating
			  the account's list with all the accounts for journal.
			- Note that journal voucher involves all accounts,
			  except cash and bank accounts.
			  
		* Input:
		 	- no input parameters
		 	
		* Output:
			- return list containing accountname which except
			  ``cash`` and ``bank`` 
		"""
		statement = "select accountname\
		        from group_subgroup_account\
		        where subgroupname is null\
		        or subgroupname != 'Cash' and subgroupname != 'Bank' order by accountname"
		result = dbconnect.engines[client_id].execute(statement).fetchall()
		if result == []:
			return result
		else:
			journalAccounts = []
			for row in result:
				journalAccounts.append(row[0])
			return journalAccounts

	def xmlrpc_getReceivableAccounts(self,queryParams,client_id):
		"""
		* Purpose: 
			- fetches the list of all accounts which are
			  used in a ``Receivable voucher``.
			- take one argument Cr or Dr and returns list of
			  accounts according.  
		  
		* Output:
			- if no accounts are found for Receivable then returns false.  
			- this function is called for populating
			  the account's list with all the accounts for Receivable.  
			- if account type is ``Cr`` then it will returns
			  account name list, except ``cash`` and ``bank`` accounts.  
			- if account type is ``Dr`` then return only ``cash`` and ``bank`` accounts.
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
			return result
		else:	 
			recievableAccounts = []
			for row in result:
				recievableAccounts.append(row[0])
			return recievableAccounts
			
	def xmlrpc_getPaymentAccounts(self,queryParams,client_id):
		'''
		Purpose: 
			- fetches the list of all accounts which are
			  used in a ``Payment voucher``.
			- take one argument ``Cr`` or ``Dr`` and 
			  returns list of accounts accordingly.  
		  
		* Output:
			- if no accounts are found for payment then returns false.  
			- this function is called for populating
			  the account's list with all the accounts for payment.
			- if type is ``Dr`` then it will returns list of account
			  names, except ``cash`` and ``bank`` accounts.  
			- if type is ``Cr`` then returns only ``cash`` and ``bank`` accounts.
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
			return result
		else:
			paymentAccounts = []
			for row in result:
				paymentAccounts.append(row[0])
			return paymentAccounts
	
		
	def xmlrpc_getDebitNoteAccounts(self,queryParams,client_id):
		"""
		* Purpose: 
			- get the list of accounts for debit note
			  either for credit or debit side.  
			- function takes one parameter cr_dr_flag.
		* Input:
			- [cr_dr flag]
		* Output:
			- returns a list of accounts pertaining to
			  debit note.  
			- if the input parameter is ``Cr`` then returns account
			  under the groupnames ``Direct Expense`` ``Fixed Assets`` 
			  ``Indirect Expense``
			- else returns accountname under subgroupnames 
			  ``Sundry Creditors for Expense`` ``Sundry Creditors for Purchase``.
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
			return result
		else:
			debitnoteAccounts = []
			for row in result:
				debitnoteAccounts.append(row[0])
			return debitnoteAccounts
	

	def xmlrpc_getCreditNoteAccounts(self,queryParams,client_id):
		"""
		* Purpose: 
			- gets the list of accounts for credit note either for credit or debit side.
		* Input:
			- [cr_dr flag]
			
		* Output: 
			- returns a list of accounts pertaining to credit note.  
			- if the input parameter is ``Cr`` then returns the accountnames under subgroupname
			  ``Sundry Debtors``.
			- else returns account under groupname ``Direct Income`` ``Indirect Income``.
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
			return result
		else:
			creditnoteAccounts = []
			for row in result:
				creditnoteAccounts.append(row[0])
			return creditnoteAccounts


	def xmlrpc_getSalesAccounts(self,queryParams,client_id):
		"""
		* Purpose: 
			- gets the list of accounts for sales accounts
			  either for credit or debit side.  
		
		* Input:
			- [cr_dr flag] 
		
		* Output: 
			- returns a list of accounts pertaining to
			  sales accounts.  
			- if the input parameter in queryParams[0] is ``Cr``
			  then return the accountname under groupname ``Direct
			  Income`` ``Indirect Income`` 
			- else returns accountname under subgroupname ``Bank`` ``Cash``
			  ``Sundry Debtor``.
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
			return result
		else:
			salesAccounts = []
			for row in result:
				salesAccounts.append(row[0])
			return salesAccounts
		
	def xmlrpc_getPurchaseAccounts(self,queryParams,client_id):
		"""
		
		Purpose: 
			- gets the list of accounts for purchase
			  accounts either for credit or debit side. 
		  
		* Input:
			- [cr_dr flag]
			
		* Output: 
			- returns a list of accounts pertaining to
			  purchase accounts.  
			- if the input parameter in queryParams[0] is ``Cr`` then 
			  returns accountnames under subgroupname ``Bank`` ``Cash`` 
			  ``Sundry Creditors for Expense`` ``Sundry Creditors for Purchase`` 
			- else returns acountnames under groupnames ``Direct Expense`` ``Indirect Expense``.
		 
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
			return result
		else:
			purchaseAccounts = []
			for row in result:
				purchaseAccounts.append(row[0])
			return purchaseAccounts

	
	def xmlrpc_getSalesReturnAccounts(self,queryParams,client_id):
		"""
		* Purpose: 
			- gets the list of accounts for ``salesreturn``
			  either for credit or debit side. 
		  
		* Input:
			- [cr_dr flag]
			
		* Output: 
			- returns a list of accounts pertaining to
			  sales return accounts.  
			- If the input parameter in queryParams[0] is ``Cr`` 
			  then returns the accountname under subgroupname ``Sundry Debtors``
			- else returns accountnames under groupname ``Direct Expense`` 
			  ``Indirect Expense`` .
		
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
			return result
		else:
			salesreturnAccounts = []
			for row in result:
				salesreturnAccounts.append(row[0])
			return salesreturnAccounts
		
		
	def xmlrpc_getPurchaseReturnAccounts(self,queryParams,client_id):
		"""
		* Purpose: 
			- gets the list of accounts for ``purchases
			  return`` either for credit or debit side.  
		
		* Input:
			- [cr_dr flag]
			  
		* Output:
			- returns a list of accounts pertaining to
			  ``purchases return``.  
			- if the input parameter in queryParams[0] is ``Cr`` 
			  then returns accuntnames under groupname ``Direct
			  Income`` ``Indirect Income``
			- else returns accountname under subgroupname 
			  ``Sundry Creditors for Expense`` ``Sundry Creditors for Purchase`` .
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
			return result
		else:
			purchasereturnAccounts = []
			for row in result:
				purchasereturnAccounts.append(row[0])
			return purchasereturnAccounts
			
			
		
