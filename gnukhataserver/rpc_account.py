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
import rpc_transaction
import dbconnect
from modules import blankspace
class account(xmlrpc.XMLRPC):
	
	"""class name is aacount which having different store procedures"""
	def __init__(self):
		xmlrpc.XMLRPC.__init__(self)
		
	def xmlrpc_setAccount(self, queryParams, client_id):
		"""
		Purpose: Adds an account in the account table, under a selected 
		group and optionally a subgroup.  
		account code is either auto generated or entered by the user
		Depending on the preference choosen by the user.
		description: This function inserts a row in the account table.
		          
		Function takes one parameter named queryParams which is a list containing,
		* queryParams[groupname,subgroupname,newsubgroupname,accountname,
		accountcodetype,openingbalance,currentBalance,suggestedcode]
		Returns True
		""" 
		group = rpc_groups.groups()
		
		queryParams = blankspace.remove_whitespaces(queryParams)
		sp_params = [queryParams[0], queryParams[3]] # create sp_params list contain  groupname , accountname 
		if queryParams[2] == "": # check for the new-subgroupname if blank then 

			if queryParams[1] == "No Sub-Group": # check for the subgroupname if "No Sub-Group" 
				print "we are not taking subgroup "
				sp_params.append("null")  # append null to sp_params list as 3rd parameter else 
			else:
				sp_params.append(queryParams[1]) # else append subgroupname sp_params list as 3rd parameter
				
		if queryParams[1] == "Create New Sub-Group" : # subgroupname is "Create New Sub-Group" then
			print "there is a new subgroup created"
			sp_params.append(queryParams[2]) # append new-subgroupname to sp_params list as 4rd parameter
		if queryParams[0] == "Direct Income" or queryParams[0] == "Direct Expense"\
		   or queryParams[0] == "Indirect Income" or queryParams[0] == "Indirect Expense": # check for groupname
		   
			sp_params.append(0) # if above groupname then append 0 as opening balance 
		else:
			sp_params.append(queryParams[5]) 
			
		now = datetime.today() # sqlite take datetime or date object for TIMESTAMP
		#date = now.strftime("%Y-%m-%d %H:%M:%S")
		sp_params.append(now) # append the current date of system while setting account
		sp_params.append(sp_params[3]) # append accountname
		
		if queryParams[7] == "": # chech for suggested account code
		
			sp_params.append("null") # if blank then append "null"
		else:
			sp_params.append(queryParams[7]) # else append suggestedcode
		
		# execute here
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		# call getGroupCodeByGroupName() pass param groupname will return groupcode
		group_code = group.xmlrpc_getGroupCodeByGroupName([sp_params[0]], client_id); 
		# check for accountcode if null
		
 		if sp_params[6] == 'null': # then
 			
 			result = Session.query(dbconnect.Account.accountcode).\
		      	 		order_by(dbconnect.Account.accountcode).\
		      		all()
		      	accountcode = []
		      	print "result"
		      	print result
			if result == []:
				maxcode = []
			else:
				for row in result:
					accountcode.append(int(row.accountcode))
					maxcode = accountcode
 			
 			
 			if maxcode == []:
				maxcode = 0
				sp_params[6] = int(maxcode) + 1;
			else:
				maxcode = max(maxcode)
				sp_params[6] = int(maxcode) + 1;
		# check for new-subgropname if null	
		if sp_params[2] == 'null': # then 
			# add all values in the account table
			Session.add(dbconnect.Account(\
						sp_params[6],group_code[0],"",sp_params[1],sp_params[3],sp_params[4],sp_params[5]))
			Session.commit()
		else:
			# if new-subgroupname is present then call getSubGroupCodeBySubGroupName pass params new-subgroupname
			# it will return subgroupcode or False
			
			subgroup_code =  group.xmlrpc_getSubGroupCodeBySubGroupName([sp_params[2]], client_id)
			# check for subgroupcode if False 
			
			if subgroup_code == [] : # then 
			        # call setSubGroup pass params groupname , new-subgroupname , client-id
   				group.xmlrpc_setSubGroup([sp_params[0],sp_params[2]],client_id); 
   				# call getSubGroupCodeBySubGroupName pass params new-subgroupname return subgroupcode
   				subgroup_code =  group.xmlrpc_getSubGroupCodeBySubGroupName([sp_params[2]], client_id); 
   			# add all the values in the account table 
   			Session.add(dbconnect.Account(\
   						sp_params[6],group_code[0],subgroup_code[0],sp_params[1],\
   						sp_params[3],sp_params[4],sp_params[5]))
   				
   			Session.commit()
                	Session.close()
                	connection.connection.close()
                	
		return "success"
		
		
	def xmlrpc_getCrOpeningBalance(self, client_id):
		"""
		Purpose: calculates the total credit opening balance for 
		all accounts with Cr opening balance.  
		Functions takes no arguement and returns a float value.
		Description:
		when adding an account we tend to know what is the total of 
		all debit and credit opening balances.
		This function calculates the total for all accounts with Cr as 
		opening balance.
		function executes `stmt` for the expected result as float.
		refer rpc_mai.py for the said group_subgroup_account view.
		"""
		stmt = "select sum(openingbalance) as totalcrbal \
		        from group_subgroup_account \
		        where groupname \
		        in ('Corpus','Capital','Current Liability','Loans(Liability)','Reserves')"
		
		res=dbconnect.engines[client_id].execute(stmt).fetchone()
		
		if res.totalcrbal == None:
			return '%.2f'%(0.00)
		else:
			return '%.2f'%(res.totalcrbal)
		
	
	def xmlrpc_getDrOpeningBalance(self, client_id):
		"""
		Purpose: calculates the total debit opening balance for all 
		accounts with Dr opening balance. 
		Functions takes no arguement and returns a float value.
		Description:
		when adding an account we tend to know what is the total of 
		all debit and credit opening balances.
		This function calculates the total for all accounts with Dr 
		as opening balance.
		function executes the `stmt` for the expected result as float.
		refer rpc_main.py for the said group_subgroup_account view
		"""
	
		stmt = "select sum(openingbalance) as totaldrbal\
		        from group_subgroup_account\
		        where groupname \
		        in ('Current Asset','Fixed Assets','Investment','Loans(Asset)','Miscellaneous Expenses(Asset)')"
		res=dbconnect.engines[client_id].execute(stmt).fetchone()
		
		if res.totaldrbal == None:
			return '%.2f'%(0.00)
		else:
			return '%.2f'%(res.totaldrbal)
			
	def xmlrpc_getSuggestedCode(self,queryParams,client_id):
		"""
		purpose: decides the code to be suggested on the basis of provided 3 characters at list 
		queryParams[0] 2 from group and 1 from the account name
		returns a string containing the suggested code.
		description:
		function takes the 2 characters of selected group and first character of account.
		The 2 characters of the selected group are determined in the front end.
		The first character of the entered account is then appended to the former.
		For example,
		an account SBI in group Current Asset will send CAS as the 3 characters as queryParams[0]
		The function then executes a stored procedure getSuggestedCode and checks 
		if an account exists with a code starting with the given 3 characters.
		if an account did exist then the given 3 characters will be postfixed 
		with total count of existing similar account codes + 100.
		If no such account is found then 100 will be concatinated to the first 3 chars.
		for example if no account exists with an account code starting with CAS, 
		then the suggested code will be CAS100.
		Next time an account with 3 chars as CAS is entered, then it will be CAS101.
		
		"""	
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		queryParams = blankspace.remove_whitespaces(queryParams)
		SuggestedAccountCode = Session.query(func.count(dbconnect.Account.accountcode)).\
		filter(dbconnect.Account.accountcode.like(str(queryParams[0])+'%')).scalar()
		
		if SuggestedAccountCode == 0:
			return str(queryParams[0] + "100")
		else:
			SuggestedAccount = SuggestedAccountCode + 100 
			return str(queryParams[0]) + str(SuggestedAccount)
		Session.commit()
		Session.close()
		connection.connection.close()
	
	def xmlrpc_getAccountCodeByAccountName(self, queryParams, client_id):	
		'''
		Purpose   : Function for getting if an accountcode with supplied 
				accountname. 	
		Parameters : queryParams which is a list containing one element, 
				accountname as string.
		Returns :  acountcode if accoutname match else eturn false string
		Description : Querys the account table and sees if an account name 
			similar to one provided as a parameter.
			if it exists then it will return accountcode related accountname
		'''
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		result = Session.query(dbconnect.Account.accountcode).\
		      	 	filter(dbconnect.Account.accountname == queryParams[0]).\
		      		first()
		Session.commit()
		Session.close()
		connection.connection.close()
		print result
		if result == None:
			return []
		else:
			return result[0]
			
	def xmlrpc_getAllAccountNames(self, client_id):
		"""
		purpose: returns the list of all accountnames in the database.
		Input Parameters : It will take any i/p parameters
		description: returns the list of name of all accounts.
		if there are no accounts to return then returns 0.
		"""
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		result = Session.query(dbconnect.Account.accountname).\
		      	 		order_by(dbconnect.Account.accountname).\
		      		all()
		Session.commit()
		Session.close()
		connection.connection.close()
			
		accountnames = []
		if result == None:
			return []
		for row in result:
			accountnames.append(row.accountname)
		
		return accountnames
	
	def xmlrpc_getAllAccountCodes(self,client_id):
		"""
		purpose: returns the list of all accountcode in the database.
		Input Parameters : It will take any i/p parameters
		description: returns the list of code of all accounts.
		if there are no accounts to return then returns 0.
		"""
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		result = Session.query(dbconnect.Account.accountcode).\
		      	 		order_by(dbconnect.Account.accountcode).\
		      		all()
		Session.commit()
		Session.close()
		connection.connection.close()
				
		accountcodes = []
		if result == None:
			return []
		for row in result:
			accountcodes.append(row.accountcode)
		
		return accountcodes
		
	def xmlrpc_getAllBankAccounts(self,client_id):
		'''
		Purpose: To get all accountnames which is under Bank subgroup
		'''
		statement = "select accountname\
			     		from group_subgroup_account\
			     		where subgroupname ='Bank'\
					order by accountname"  
		getallbankaccounts = dbconnect.engines[client_id].execute(statement).fetchall()
		
		if getallbankaccounts == []:
			return []
		else:
			bankaccount = []
			for row in getallbankaccounts:
				bankaccount.append(row[0])
			return bankaccount 
			
	def xmlrpc_getCashFlowOpening(self,client_id):
		'''
		output parameters:accountname,openingbalance
		Purpose: to get all accountnames which is in 
		under Bank and cash subgroup
		'''
		statement = "select accountname,openingbalance\
				from group_subgroup_account\
				where subgroupname \
				in ('Bank','Cash') order by accountname"
		result = dbconnect.engines[client_id].execute(statement).fetchall()
		cashflow = []
		for row in result:
			cashflow.append([row[0],row[1]])
		
		return cashflow 
		
	def xmlrpc_getCashFlowReceivedAccounts(self,queryParams,client_id):
		'''
		input parameters: cfaccountname,cbaccountname,startdate,enddate
		output parameters: cfamount
		Purpose: to get sum of amount which in startdate and todate
		
		'''
		financial_fromdate = str(datetime.strptime(str(queryParams[2]),"%d-%m-%Y"))
		financial_enddate =  str(datetime.strptime(str(queryParams[3]),"%d-%m-%Y"))
		statement = "select sum(amount)\
				from view_voucherbook\
				where account_name = '"+queryParams[0]+"' \
				and vouchercode \
				in(select vouchercode from view_voucherbook \
				where typeflag = 'Dr' \
				and account_name = '"+queryParams[1]+"'\
				and reffdate >= '"+financial_fromdate+"'\
				and reffdate <= '"+financial_enddate+"'\
				and flag = 1)\
				group by account_name"
		result = dbconnect.engines[client_id].execute(statement).fetchone()
		
		CashFlowReceived = []
		if result == None:
			return result
		else:
			for row in result:
				CashFlowReceived.append(row)
			return CashFlowReceived 			
	
	def xmlrpc_getCashFlowPaidAccounts(self,queryParams,client_id):
		'''
		input parameters: cfaccountname,cbaccountname,startdate,enddate
		output parameters: cfamount
		Purpose: to get sum of amount which in startdate and todate
		
		'''
		financial_fromdate = str(datetime.strptime(str(queryParams[2]),"%d-%m-%Y"))
		financial_enddate =  str(datetime.strptime(str(queryParams[3]),"%d-%m-%Y"))
		
		statement = "select sum(amount)\
				from view_voucherbook\
				where account_name ='"+queryParams[0]+"'\
				and vouchercode \
				in(select vouchercode from view_voucherbook \
				where typeflag = 'Cr' \
				and account_name = '"+queryParams[1]+"'\
				and reffdate >= '"+financial_fromdate+"' \
				and reffdate <= '"+financial_enddate+"'\
				and flag = 1)\
				group by account_name"
		result = dbconnect.engines[client_id].execute(statement).fetchone()
		
		getCashFlowPaid = []
		if result == None:
			return result
		else:
			for row in result:
				getCashFlowPaid.append(row)
			
			return getCashFlowPaid 
		
	
	def xmlrpc_accountExists(self, queryParams, client_id):
		'''
		Purpose   : Function for finding if an account already exists 
		with the supplied name. 	
		Parameters : queryParams which is a list containing one element, 
		accountname as string.
		Returns :  1 if account name exists and 0 if not.
		Description : Querys the account table and sees if an account 
		name similar to one provided 
		as a parameter exists.
		We can ensure that no duplicate account is ever entered because 
		if a similar account exists 
		like the one in queryparams[0] then we won't allow another 
		entry with same name.
		'''
		queryParams = blankspace.remove_whitespaces(queryParams)
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		result = Session.query(func.count(dbconnect.Account.accountname)).\
		      filter(dbconnect.Account.accountname == queryParams[0]).\
		      scalar()
		      
		Session.commit()
		Session.close()
		connection.connection.close()
		
		if result == 0:
			return "0"
		else:
			return "1"
			
	def xmlrpc_accountCodeExists(self, queryParams, client_id):
		'''
		Purpose   : Function for finding if an accountcode already 
		exists with the supplied code. 	
		Parameters : queryParams which is a list containing one element, 
		accountcode as string.
		Returns :  1 if account code exists and 0 if not.
		Description : Querys the account table and sees if an account 
		code similar to one provided 
		as a parameter exists.
		We can ensure that no duplicate account is ever entered because 
		if a similar accountcode exists 
		like the one in queryparams[0] then we won't allow another 
		entry with same code.
		'''
		queryParams = blankspace.remove_whitespaces(queryParams)
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		result = Session.query(func.count(dbconnect.Account.accountcode)).\
		      filter(dbconnect.Account.accountcode == queryParams[0]).\
		      scalar()
		Session.close()
		connection.connection.close()
		
		if result == 0:
			return "0"
		else:
			return "1"
			
	def xmlrpc_editAccount(self, queryParams, client_id):
		"""
		purpose: modifies an account based on account code.  
		alters account name and opening balance.
		function takes one parameter queryParams
		
		Input parameters :
		[accountname, accountcode, groupname and new_opening_balance]
		
		Output parametres :
		[Current_balance]
		
		description: This function will edit an account and change 
		either account name, oepning balance or both.
		the account is fetched internally by the software on the basis 
		of account code, even if it was searched by client using account
		name. If the function is successful,it will return the newly 
		updated current balance.If the groupname sent in the queryParams
		is direct or indirect income, or direct or indirect expence, 
		then the oepning balance is sent as 0.
		
		"""
		queryParams = blankspace.remove_whitespaces(queryParams)
		spQueryParams = [queryParams[0], queryParams[1]]
		if queryParams[2] == "Direct Income" or \
			queryParams[2] == "Indirect Income" \
			or queryParams[2] == "Direct Expense" \
			or queryParams[2] == "Indirect Expense":
			
			print "sending openingbalance as 0"
			spQueryParams.append(0)
		else: 
			spQueryParams.append(float(queryParams[3]))
			
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		result = Session.query(dbconnect.Account).\
			filter(dbconnect.Account.accountcode == spQueryParams[1]).first()
		resultParams = [float(result.openingbalance),float(result.balance)]
		if resultParams[0] == spQueryParams[2]:
		
			result = Session.query(dbconnect.Account).\
				filter(dbconnect.Account.accountcode == spQueryParams[1]).\
				update({'accountname': spQueryParams[0]})
		else:
			final_balance = (spQueryParams[2] - resultParams[0]) + resultParams[1]; 
			result = Session.query(dbconnect.Account).\
				filter(dbconnect.Account.accountcode == spQueryParams[1]).\
				update({'accountname': spQueryParams[0],'openingbalance': spQueryParams[2],'balance': final_balance})
			
		Session.commit()
		Session.close()
		connection.connection.close()
		
		return final_balance
		
		
	def xmlrpc_getAccount(self, queryParams, client_id):
		"""
		purpose: Searches and returns account details.  
		Search is based on either accountcode or account name.
		function takes one parameter queryParams of type list containing,
		* searchFlag as integer (1 means search by account code and 2 means account name )
		* searchValue as text (value depends on the searchFlag)
		description:This function queries the group_subgroup_account 
		view and fetches the following.
		* groupname
		* subgroupname (if any )
		* accountcode
		* accountname
		* openingbalance
		
		"""
		
		if queryParams[0] == 1:
			statement = "select groupname,subgroupname,accountcode,accountname,openingbalance\
			     		from group_subgroup_account\
			     		where accountcode = '"+queryParams[1]+"'"
		else:	     	
			statement = "select groupname,subgroupname,accountcode,accountname,openingbalance\
			     		from group_subgroup_account\
			     		where accountname = '"+queryParams[1]+"'"	
		result = dbconnect.engines[client_id].execute(statement).fetchone()
		
		print 
		print "groupname getaccount"
		
		if result[1] == None:
			return [result[2], result[0],"No subgroup", result[3], result[4]]
		else:
			return [result[2], result[0], result[1], result[3], result[4]]
			
	
	def xmlrpc_getAccountNamesByGroupCode(self,queryParams,client_id):
		'''
		Purpose : get accouname accoding to groupcode
		Input parameters : [groupcode]
		Output Parameters : [accountname]
		'''
		print queryParams[0]
		print "groupcode"
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)	
		result = Session.query(dbconnect.Account.accountname).\
				filter(dbconnect.Account.groupcode == queryParams[0]).\
				order_by(dbconnect.Account.accountname).all()
		Session.commit()
		Session.close()
		connection.connection.close()
		
		accountnames = []
		if result == []:
			return result
		else:
			for account in result:
				accountnames.append(str(account[0]))
			
			return accountnames
		
	def xmlrpc_getAccountNamesByProjectName(self,queryParams,client_id):
		'''
		Purpose : This function will return list of accountnames
		for particular projectname
		Input parameters: projectname
		output : list of accountnames
	
		'''
		transaction = rpc_transaction.transaction()
		projectcode = transaction.xmlrpc_getProjectcodeByProjectName(queryParams,client_id)
		statement = "select distinct(account_name)\
		     		from view_voucherbook\
		     		where projectcode = '"+str(projectcode)+"'\
				and flag = 1\
				order by account_name"  
		result = dbconnect.engines[client_id].execute(statement).fetchall()
		accountname = []
		for Row in result:
			accountname.append(Row[0])
		print accountname	
		return accountname       
	
	
	def xmlrpc_deleteAccount(self, queryParams, client_id):
		'''
		Purpose   : Function for deleting account name
		Parameters : queryParams is a account name as string.
		Returns :  returns 1 when account is deleted
		'''
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		result = Session.query(dbconnect.Account).\
		      	 	filter(dbconnect.Account.accountname == queryParams[0]).\
		      		delete()
		Session.commit()
		Session.close()
		connection.connection.close()	
		return "1"
		
		
	def xmlrpc_hasOpeningBalance(self, queryParams, client_id):
		'''
		Purpose   : Function to find out whether the given account 
		has opening balance or not
		Parameters : queryParams is a account name as string.
		Returns : if opening balance of that account name is 
		equal to 0 then return 0 or else return 1
		'''
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		result = Session.query(dbconnect.Account.openingbalance).\
	      	 		filter(dbconnect.Account.accountname == queryParams[0]).\
	      			scalar()
		Session.close()
		connection.connection.close()
		if result == 0:
			return "0"
		else:	
			return "1"
			
	
	def xmlrpc_hasTransactions(self, queryParams, client_id):
		'''
		Purpose : Function to find out whether the given account 
		has any transactions or not
		
		Parameters: queryParams is a account name as string.
		
		Returns : if there is any voucher entry of that accountname 
		return 1 or else return 0
		'''
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		
		statement = "select count(vouchercode) as vouchercodeCount\
			     		from view_voucherbook\
			     		where account_name ='"+str(queryParams[0])+"'"
		
		result = dbconnect.engines[client_id].execute(statement).fetchone()
		Session.close()
		connection.connection.close()
		if result[0] == 0:
			return 0
		if result[0]  > 0:
			return 1
		
		
	def xmlrpc_deleteAccountNameMaster(self,queryParams,client_id):
		'''
		i/p: A list containing first element as accountname or accountcode and
				second element is flag(if first element is accountname, flag is 1 and
				if if fist element is accountcode, flag is 2)
				
		Purpose   : Function for deleting accounts. 
		
		For this we have used hasOpeningBalance,hasTransactions & deleteAccount 
		rpc functions. 
		With the help of hasTransactions we are able to find out whether 
		the given account has any transactions or not. 
		It tells that if there is any voucher entry of that accountname 
		return 1 or else return 0
		
		The function hasOpeningBalance returns 1 if opening balance 
		for that account exists or else returns 0
		and third function deleteAccount deletes that particular accountname
		Parameters : queryParams is a account name as string.
		
		Returns :  if hasOpenibalance is 0 and hasTransaction is 0
		returns string "account deleted"
		
		if hasOpenibalance is 1 and hasTransaction is 1
		returns string "has both opening balance and trasaction" 
		
		'''
		connection = dbconnect.engines[client_id].connect()
        	Session = dbconnect.session(bind=connection)
        	#if flag is 1, that means first element is account name
        	if queryParams[1] == 1:
        		accName = str(queryParams[0])
    			hasOpeningBalance = self.xmlrpc_hasOpeningBalance([accName],client_id)
    			hasTransactions = self.xmlrpc_hasTransactions([accName],client_id)
    		else:
    			#if flag is 2, that means first element is account code,
    			#we have to get accountname by accountcode
    			accName = self.xmlrpc_getAccountNameByAccountCode([str(queryParams[0])],client_id)
    			hasOpeningBalance = self.xmlrpc_hasOpeningBalance([accName],client_id)
    			hasTransactions = self.xmlrpc_hasTransactions([accName],client_id)
        	Session.close()
        	connection.connection.close()
		if(str(hasOpeningBalance) == "0" and str(hasTransactions) == "0"):
		    self.xmlrpc_deleteAccount([accName],client_id)
		    return "account deleted"
		elif(str(hasOpeningBalance) == "1" and str(hasTransactions) == "1"):
		    return "has both opening balance and trasaction"
		elif(str(hasOpeningBalance) == "1"):
		    return "has opening balance"
		elif(str(hasTransactions) == "1"):
		    return "has transaction"
		
		
		def xmlrpc_getAccountNameByAccountCode(self, queryParams, client_id):	
			'''
			i/p: accountcode
			Purpose   : Function for getting if an accountname with supplied 
					accountcode. 	
			Returns : accoutname if acountcode match else eturn false string
			Description : Querys the account table and sees if an acountcode
				similar to one provided as a parameter.
				if it exists then it will return accountname related accountcode
			'''
			connection = dbconnect.engines[client_id].connect()
			Session = dbconnect.session(bind=connection)
			result = Session.query(dbconnect.Account.accountname).\
				  	 	filter(dbconnect.Account.accountcode == queryParams[0]).\
				  		first()
			Session.commit()
			Session.close()
			connection.connection.close()
			print result
			if result == None:
				return []
			else:
				return result[0]
		
