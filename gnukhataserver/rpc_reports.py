from multiprocessing.connection import Client

'''
import the database connector and functions for stored procedure.
'''
import dbconnect
import rpc_account
import rpc_transaction
import rpc_groups
'''
import the twisted modules for executing rpc calls and 
also to implement the server
'''
from twisted.web import xmlrpc, server
'''
reactor from the twisted library starts the server with a 
published object and listens on a given port.'''
from twisted.internet import reactor
from datetime import datetime
from time import strftime
from modules import blankspace

class reports(xmlrpc.XMLRPC):
	
	def __init__(self):
		xmlrpc.XMLRPC.__init__(self)
	
	def xmlrpc_getLedger(self,queryParams,client_id):
		'''
		Purpose : returns a complete ledger for given account.  
		Information taken from view_voucherbook	
		
		Input parameters : 
		[accountname,financialStart,fromdate,todate,projectname]
		
		Output parameters : 
		Returns a grid (2 dimentional list ) with columns as 
		[Date, Particulars, Reference number, Dr, Cr , vouchercode]
		
		Description : Note that last 3 rows have the narration 
		column blank.
		The 3rd last row contains just the total Dr and total Cr.
		the second last row contains the closing balance.
		If the closing balance (carried forward ) is Dr then it 
		will be shown at Cr side.
		The C/F balance if Cr will be shown at Dr side.
		The last row will just contain the grand total which will
		be equal at credit and debit side.
		'''
		#first let's get the details of the given account regarding the
		#Balance and its Dr/Cr side.
		#note that we use the calculateBalance function which gives us
		#the B/f balance, C/F balance group type and type of the balance.
		#we will not use this if a project is specified, as there is no 
		#point in displaying opening balance.
		#if all transactions are to be searched then project 
		#(queryparams[4]) will be "No Project".
		queryParams = blankspace.remove_whitespaces(queryParams)
		balanceRow = self.xmlrpc_calculateBalance([queryParams[0],queryParams[1],queryParams[2],queryParams[3]],client_id)
		
		if queryParams[4] == "No Project":
			# calculateBalance will return opening balance 
			openingBalance = balanceRow[1]
		else:
			# if ledger of account which is not under any project 
			# will have opening balance 0.00
			openingBalance = 0.00
		#declare the ledgerGrid as a blank list.
		#we will fill it up through a for loop where every iteration will append a row with 5 columns.
		ledgerGrid = []
		#Let's start with 0 for Total Dr and total Cr amounts.
		totalDr = 0.00
		totalCr = 0.00
		if openingBalance != 0:
			#since we know that balance is not 0, we must decide if it is Cr or Dr balance.
			#This can be found out depending on the opening_baltype from the stored procedure calculateBalance.
			if balanceRow[5] == "Dr":
				#this makes the first row of the grid.
				#note that the total Dr is also set.  Same will happen in the next condition for Cr.
				openingdate = datetime.strptime(str(queryParams[1]),"%d-%m-%Y").strftime("%d-%m-%Y")
				ledgerGrid.append([openingdate,["Opening Balance b/f"],"",'%.2f'%(openingBalance),"","",""])
			if balanceRow[5] == "Cr":
				openingdate = datetime.strptime(str(queryParams[1]),"%d-%m-%Y").strftime("%d-%m-%Y")
				ledgerGrid.append([openingdate,["Opening Balance b/f"],"","",'%.2f'%(openingBalance),"",""])
				
		else:
			#its 0 so will be set to 0.
			totalDr= 0.00
			totalCr = 0.00
		# create the instance of transaction 
		transaction = rpc_transaction.transaction()
		# call getTransactions to get the transaction details for this account.
		
		
		transactions = transaction.xmlrpc_getTransactions([queryParams[0],queryParams[2],queryParams[3],queryParams[4]],client_id)
		print "get Transactions"
		print transactions
		# fill up the grid with the rows for transactions.
		for transactionRow in transactions:
			ledgerRow = []
			date = str(transactionRow[2]).split(" ")
			#print type(str(transactionRow[2]).split(""))
			transactionDate = datetime.strptime(date[0],"%Y-%m-%d").strftime("%d-%m-%Y")
			ledgerRow.append(transactionDate)
			# if the transaction had the amount at Dr side then particulars must have the names of accounts involved in Cr.
			if transactionRow[1] == "Dr":
				particulars = transaction.xmlrpc_getParticulars([transactionRow[0],"Cr"],client_id)
				print "particulars"
				print particulars
				#may be more than one account was involved a tthe other side so loop through.
				particular = []
				for particularRow in particulars:
					particular.append(particularRow)
				ledgerRow.append(particular)
				ledgerRow.append(transactionRow[3])
				ledgerRow.append('%.2f'%(float(transactionRow[4])))
				totalDr = totalDr + float(transactionRow[4])
				ledgerRow.append("")
				ledgerRow.append(transactionRow[5])
				
			if transactionRow[1] == "Cr":
				particulars = transaction.xmlrpc_getParticulars([transactionRow[0],"Dr"],client_id)
				print "particulars"
				print particulars
				particular = []
				for particularRow in particulars:
					particular.append(particularRow)
				ledgerRow.append(particular)
				ledgerRow.append(transactionRow[3])
				ledgerRow.append("")
				ledgerRow.append('%.2f'%(float(transactionRow[4])))
				totalCr = totalCr + float(transactionRow[4])
				ledgerRow.append(transactionRow[5])
			ledgerRow.append(transactionRow[0])
			ledgerGrid.append(ledgerRow)
		#the transactions have been filled up duly.
		#now for the total dRs and Crs, we have added them up nicely during the grid loop.
		ledgerGrid.append(["",["Total of Transactions"],"",'%.2f'%(totalDr),'%.2f'%(totalCr),"",""])
		if queryParams[4] == "No Project":
			ledgerGrid.append(["",[""],"","","","",""])
			grandTotal = 0.00
			closingdate = datetime.strptime(str(queryParams[3]),"%d-%m-%Y").strftime("%d-%m-%Y")
			if balanceRow[6] == "Dr":
			#this is a Dr balance which will be shown at Cr side.
			#Difference will be also added to Cr for final balancing.
				ledgerGrid.append([closingdate,["Closing Balance c/f"],"","",'%.2f'%(balanceRow[2]),"",""])
				grandTotal =float(balanceRow[4])  + float(balanceRow[2])
			if balanceRow[6] == "Cr":
			#now exactly the opposit, see the explanation in the if condition preceding this one.

				ledgerGrid.append([closingdate,["Closing Balance c/f"],"",'%.2f'%(balanceRow[2]),"","",""])
				grandTotal =float(balanceRow[3])  + float(balanceRow[2])
			ledgerGrid.append(["",["Grand Total"],"",'%.2f'%(grandTotal),'%.2f'%(grandTotal),"",""])
		#we are ready with the complete ledger, so lets send it out!
		return ledgerGrid
			
	def xmlrpc_calculateBalance(self,queryParams,client_id):
		"""
		Purpose: calculate closing balance of given accounts 
		Returns a grid of 4 columns and number of 
		rows depending on number of accounts.
		
		Input parameters:
		[accountname,org_financial_from,report_from_date,report_to_date]
		
		Returns list:
		[group_name,bal_brought,curbal,total_DrBal,total_CrBal,opening_baltype,baltype]
		
		"""
		print "cal bal list "
		print queryParams
		# get the groupname accourding to ac
		statement = "select groupname\
			     from group_subgroup_account\
			     where accountname = '"+queryParams[0]+"'"
		result = dbconnect.engines[client_id].execute(statement).fetchone()
		print "result"
		print result
		print result[0]
		group_name = result[0]
		#print "groupname"
		#print group_name
		statement = "select openingbalance\
			      from group_subgroup_account\
			      where accountname = '"+queryParams[0]+"'"
		result = dbconnect.engines[client_id].execute(statement).fetchone()
		opening_balance = result[0]
		#print "opening_balance"
		#print opening_balance
		financial_fromdate = str(datetime.strptime(str(queryParams[1]),"%d-%m-%Y"))
		report_fromdate =  str(datetime.strptime(str(queryParams[2]),"%d-%m-%Y"))
		report_todate =  str(datetime.strptime(str(queryParams[3]),"%d-%m-%Y"))
		
		if financial_fromdate == report_fromdate:
			if opening_balance == 0:
        	 		bal_brought = opening_balance 
     				opening_baltype = 0
		 		baltype = 0
	     		if (opening_balance < 0) and (group_name == 'Current Asset' \
	     							or group_name == 'Fixed Assets'\
	     							or group_name == 'Investment' \
	     							or group_name == 'Loans(Asset)' \
	     							or group_name == 'Miscellaneous Expenses(Asset)'): 
				bal_brought = abs(opening_balance) 
		 		opening_baltype = 'Cr' 
		 		baltype = 'Cr'
		 		
			if (opening_balance > 0) and (group_name == 'Current Asset' \
								or group_name =='Fixed Assets'\
								or group_name == 'Investment' \
								or group_name == 'Loans(Asset)' \
								or group_name == 'Miscellaneous Expenses(Asset)'): 
				bal_brought = opening_balance
				opening_baltype = 'Dr'
				baltype = 'Dr'
				
			if (opening_balance < 0 ) and (group_name == 'Corpus' \
								or group_name == 'Capital' \
								or group_name == 'Current Liability' \
								or group_name == 'Loans(Liability)' \
								or group_name == 'Reserves'):
				bal_brought = abs(opening_balance)
				opening_baltype = 'Dr'
				baltype = 'Dr'
	
			if (opening_balance > 0) and (group_name == 'Corpus' \
								or group_name == 'Capital' \
								or group_name == 'Current Liability'\
								or group_name == 'Loans(Liability)'\
								or group_name == 'Reserves'):
				bal_brought = opening_balance
				opening_baltype = 'Cr'
				baltype = 'Cr'
			#print baltype	
		
		else:
			statement = "select sum(amount) as dr_amount\
				from view_voucherbook \
				where account_name = '"+queryParams[0]+"'\
				and typeflag = 'Dr' \
				and reffdate >= '"+financial_fromdate+"' \
				and reffdate < '"+report_fromdate+"'\
				and flag = 1"
	
			result = dbconnect.engines[client_id].execute(statement).fetchone()
			total_dr_upto_from = result[0]
			
			statement = "select sum(amount) as cr_amount \
				from view_voucherbook \
				where account_name ='"+queryParams[0]+"'\
				and typeflag = 'Cr' \
				and reffdate >= '"+financial_fromdate+"' \
				and reffdate < '"+report_fromdate+"' \
				and flag = 1"
				
			result = dbconnect.engines[client_id].execute(statement).fetchone()
			total_cr_upto_from = result[0]
			#print total_dr_upto_from
			#print total_cr_upto_from
			
			if total_dr_upto_from == None: 
				total_dr_upto_from = 0
	
			if total_cr_upto_from == None:
				total_cr_upto_from = 0
	
			if opening_balance == 0:
				bal_brought = opening_balance

			if (opening_balance < 0) and (group_name == 'Current Asset'\
								or group_name == 'Fixed Assets'\
								or group_name == 'Investment' \
								or group_name == 'Loans(Asset)' \
								or group_name == 'Miscellaneous Expenses(Asset)'):
								
				total_cr_upto_from = total_cr_upto_from + abs(opening_balance)
	
			if (opening_balance > 0) and (group_name == 'Current Asset'\
								or group_name == 'Fixed Assets'\
								or group_name == 'Investment'\
								or group_name == 'Loans(Asset)'\
								or group_name == 'Miscellaneous Expenses(Asset)'):
								 
				total_dr_upto_from = total_dr_upto_from + opening_balance
	
			if (opening_balance < 0) and (group_name == 'Corpus'\
								or group_name == 'Capital'\
								or group_name == 'Current Liability'\
								or group_name == 'Loans(Liability)'\
								or group_name == 'Reserves'):
								 
				total_dr_upto_from = total_dr_upto_from + abs(opening_balance)
	
			if (opening_balance > 0) and (group_name == 'Corpus'\
								or group_name == 'Capital'\
								or group_name == 'Current Liability'\
								or group_name == 'Loans(Liability)'\
								or group_name == 'Reserves'):
								 
				total_cr_upto_from = total_cr_upto_from + opening_balance 
				
			if total_dr_upto_from > total_cr_upto_from: 
				bal_brought = total_dr_upto_from - total_cr_upto_from
				baltype = 'Dr'
				opening_baltype = 'Dr'
	
			if total_dr_upto_from < total_cr_upto_from:
				bal_brought = total_cr_upto_from - total_dr_upto_from 
		                baltype = 'Cr'
				opening_baltype = 'Cr'
				
		
		statement = "select sum(amount) as dr_amount\
				from view_voucherbook\
				where typeflag = 'Dr'\
				and account_name = '"+queryParams[0]+"'\
				and reffdate >= '"+report_fromdate+"'\
				and reffdate <= '"+report_todate+"' \
				and flag = 1"
		result = dbconnect.engines[client_id].execute(statement).fetchone()
		total_DrBal = result[0]
		print "total_DrBal"
		print total_DrBal
		statement = "select sum(amount) as cr_amount\
				from view_voucherbook\
				where typeflag ='Cr'\
				and account_name = '"+queryParams[0]+"'\
				and reffdate >= '"+report_fromdate+"'\
				and reffdate <= '"+report_todate+"'\
				and flag = 1"
		result = dbconnect.engines[client_id].execute(statement).fetchone()
		total_CrBal = result[0]
		print "total_CrBal"
		print total_CrBal
		
		if total_CrBal == None: 
			total_CrBal = 0 
		if total_DrBal == None: 
			total_DrBal = 0 

		if baltype == 'Dr': 
			total_DrBal = total_DrBal + bal_brought 
		if baltype == 'Cr':
			total_CrBal = total_CrBal + bal_brought 

		if total_DrBal > total_CrBal: 
			curbal = total_DrBal - total_CrBal
			baltype = 'Dr'
		else:
			curbal = total_CrBal - total_DrBal
			baltype = 'Cr'

		calculate_balancelist = [group_name,bal_brought,curbal,total_DrBal,total_CrBal,opening_baltype,baltype]
		print "calculate_balancelist"
		print calculate_balancelist
		return calculate_balancelist
		
		
	def xmlrpc_getTrialBalance(self,queryParams,client_id):
		
		"""
		Purpose: 
		gets trial balance as on the given date. 
		Returns a grid of 4 columns and number of 
		rows depending on number of accounts.
			
		Input parameters contains: 
		[org_financial_from,from_date,to_date]
		
		Output : 
		list containing list 
		[serial no , accountname , groupname , debit bal , creadit bal ]
		 	and [total debit , total credit]
			
		description:
		
		This function returns a grid of 4 columns contaning 
		trial balance.
		Number of rows in this grid will depend on the number 
		of accounts in the database.
		The function first makes a call to the getAllAccounts 
		from rpc_account to get accountlist
		then a loop runs through the list of accounts.
		on every iteration it calls the calculateBalance and 
		passes the account as a parameter along with the financial start
		from_date and to_date
		
		Note that trial balance is always calculated from the starting 
		of the financial year.
		Also in the for loop we see if the typeflag for the balance 
		for given account is Dr or Cr.
		if the balance is Dr then we put the amount in the 4th column, 
		with the 5th column blank.
		If the typeflag is credit then we put the amount in the 5th row, 
		leaving the 4th as blank.
		   
		"""
		queryParams = blankspace.remove_whitespaces(queryParams)
		account = rpc_account.account()
		accounts = account.xmlrpc_getAllAccountNames(client_id)
		trialBalance = []
		srno =1
		total_dr = 0.00
		total_cr = 0.00
		
		for account in accounts:
			print account
			closingRow = self.xmlrpc_calculateBalance([account,queryParams[0],queryParams[1],queryParams[2]],client_id)
			print closingRow[2]
			if float(closingRow[2])!= 0:
				trialRow = []
				trialRow.append(srno)
				trialRow.append(account)
				trialRow.append(closingRow[0])
				if closingRow[6] == "Cr":
					total_cr = total_cr + float(closingRow[2])
					trialRow.append("")
					trialRow.append('%.2f'%float(closingRow[2]))
				if closingRow[6] == "Dr":
					total_dr = total_dr + float(closingRow[2])
					trialRow.append('%.2f'%float(closingRow[2]))
					trialRow.append("")
				srno = srno +1
				trialBalance.append(trialRow)
		total_balances = ["","","",'%.2f'%total_dr,'%.2f'%total_cr]
		trialBalance.append(total_balances)
	
		return trialBalance
		
	def xmlrpc_getGrossTrialBalance(self,queryParams,client_id):
		'''
		purpose:just like the getTrialBalance, this function too returns
		list of balances of all accounts.
		However it has a difference in that it provides the total Dr 
		and total Cr for all accounts, instead of the difference.
		
		
		description: Similar to the getTrial balance function this one 
		returns a grid, but instead of current balance, it returns total 
		Dr and total Cr in the grid.
		[serial no , accountname , groupname , debit bal , creadit bal ]
		 	and [total debit , total credit]
		
		'''
		account = rpc_account.account()
		accounts = account.xmlrpc_getAllAccountNames(client_id)
		trialBalance = []
		srno =1
		total_dr = 0.00
		total_cr = 0.00
		for acc in accounts:
			
			closingRow = self.xmlrpc_calculateBalance(\
						[acc,queryParams[0],queryParams[1],queryParams[2]],client_id)
			print closingRow
			if float(closingRow[3]) != 0 or float(closingRow[4]) != 0:
				trialRow = []
				trialRow.append(srno)
				trialRow.append(acc)
				trialRow.append(closingRow[0])
				trialRow.append('%.2f'%float(closingRow[3]))
				trialRow.append('%.2f'%float(closingRow[4]))
				total_dr = total_dr + float(closingRow[3])
				total_cr = total_cr + float(closingRow[4])
				srno = srno +1
				trialBalance.append(trialRow)
		total_balances = ['','','','%.2f'%total_dr,'%.2f'%total_cr]
		trialBalance.append(total_balances)
		return trialBalance	
	
	def xmlrpc_getExtendedTrialBalance(self,queryParams,client_id):
		"""
		Purpose: gets trial balance as on the given date. 
		Returns a grid of 7 columns and number of rows 
		depending on number of accounts.
		
		description:This function returns a grid of 7 columns 
		contaning trial balance.
		Number of rows in this grid will depend on the number 
		of accounts in the database.
		The function first makes a call to the getAllAccountnames 
		and stors the list.
		then a loop runs through the list of accounts.
		on every iteration it calls the calculateBalance and 
		passes the account as a parameter along with the 
		[financial start, Calculate_from and calculate_to]
		
		Note: trial balance is always calculated from the starting 
		of the financial year.
		Also in the for loop we see if the typeflag for the balance 
		for given account is Dr or Cr.
		if the balance is Dr then we put the amount in the 
		4th column, with the 5th column blank.
		If the typeflag is credit then we put the amount in the 5th row,
		leaving the 4th as blank.
		
		"""
		queryParams = blankspace.remove_whitespaces(queryParams)
		account = rpc_account.account()
		accounts = account.xmlrpc_getAllAccountNames(client_id)
		trialBalance = []
		srno =1
		total_dr = 0.00
		total_cr = 0.00
		total_ExtendedCr = 0.00
		total_ExtendedDr = 0.00
		for acc in accounts:
			
			closingRow = self.xmlrpc_calculateBalance(\
						[acc,queryParams[0],queryParams[1],queryParams[2]],client_id)
			print closingRow
			if float(closingRow[1]) != 0 or float(closingRow[3]) != 0 or float(closingRow[4]) != 0:
				trialRow = []
				trialRow.append(srno)
				trialRow.append(acc)
				trialRow.append(closingRow[0])
				if float(closingRow[1]) != 0 and closingRow[5] == "Dr":
					trialRow.append('%.2f'%float(closingRow[1])+"(Dr)")
					trialRow.append('%.2f'%(float(closingRow[3])- float(closingRow[1])))
					total_dr = total_dr + (float(closingRow[3]) - float(closingRow[1]))
					trialRow.append('%.2f'%float(closingRow[4]))
					total_cr = total_cr +float(closingRow[4])
				if float(closingRow[1]) != 0 and closingRow[5] == "Cr":
					trialRow.append('%.2f'%float(closingRow[1])+"(Cr)")
					trialRow.append('%.2f'%float(closingRow[3]))
					total_dr = total_dr + float(closingRow[3])
					trialRow.append('%.2f'%(float(closingRow[4])- float(closingRow[1])))
					total_cr = total_cr + (float(closingRow[4]) - float(closingRow[1]))
				if float(closingRow[1]) == 0:
					trialRow.append("")
					trialRow.append('%.2f'%float(closingRow[3]))
					total_dr = total_dr + float(closingRow[3])
					trialRow.append('%.2f'%float(closingRow[4]))
					total_cr = total_cr + float(closingRow[4])
				if closingRow[6] == "Dr":
					trialRow.append('%.2f'%float(closingRow[2]))
					trialRow.append("")
					total_ExtendedDr = total_ExtendedDr + float(closingRow[2])
				if closingRow[6] == "Cr":
					trialRow.append("")
					trialRow.append('%.2f'%float(closingRow[2]))
					total_ExtendedCr = total_ExtendedCr + float(closingRow[2]) 
				srno = srno +1
				trialBalance.append(trialRow)
		total_balances = ['','','','','%.2f'%total_dr,'%.2f'%total_cr,'%.2f'%total_ExtendedDr,'%.2f'%total_ExtendedCr]
		trialBalance.append(total_balances)
		return trialBalance
		
	def xmlrpc_getProjectStatementReport(self,queryParams,client_id):
		'''
		Input parameters:[projectname,accountname,financial_fromdate,fromdate,todate]
		Output:list of list [serialno,accountname,groupname,totalDr,totalCr]
		'''
		account = rpc_account.account()
		group = rpc_groups.groups()
		projectAccounts =account.xmlrpc_getAccountNamesByProjectName([str(queryParams[0])],client_id)
		totalDr = 0.00
		totalCr = 0.00
		srno = 1
		projectStatement = []
		for accountRow in projectAccounts:
			
			groupRow = group.xmlrpc_getGroupNameByAccountName([accountRow],client_id)
			accountGroup = groupRow[0]
			resultRow = self.xmlrpc_getProjectStatement(\
			[queryParams[0],accountRow,queryParams[1],queryParams[2],queryParams[3]],client_id)
			print '%.2f'%float(resultRow[0])
			print '%.2f'%float(resultRow[1])
			if(('%.2f'%float(resultRow[0])!= "0.00" )or('%.2f'%float(resultRow[1])!="0.00")):
				statementRow = [srno,accountRow,accountGroup,'%.2f'%float(resultRow[0]),'%.2f'%float(resultRow[1])]
				totalDr = totalDr + resultRow[0]
				totalCr = totalCr + resultRow[1]
				srno = srno +1
				projectStatement.append(statementRow)
		projectStatement.append(["","","",'%.2f'%float(totalDr),'%.2f'%float(totalCr)])
		print "getProjectStatementReport"
		print projectStatement
		return projectStatement
	
	def xmlrpc_getProjectStatement(self,queryParams,client_id):
		'''
		Input parameters:[projectname,accountname,financial_fromdate,fromdate,todate]
		Output :[total_debit,total_credit]
		'''
		print "getProjectStatement"
		financial_fromdate = str(datetime.strptime(str(queryParams[2]),"%d-%m-%Y"))
		report_fromdate =  str(datetime.strptime(str(queryParams[3]),"%d-%m-%Y"))
		report_todate =  str(datetime.strptime(str(queryParams[4]),"%d-%m-%Y"))
		transaction = rpc_transaction.transaction()
		projectcode = transaction.xmlrpc_getProjectcodeByProjectName([queryParams[0]],client_id)
		statement = "select sum(amount)\
			     		from view_voucherbook\
			     		where projectcode = '"+str(projectcode)+"'\
			     		and account_name = '"+str(queryParams[1])+"'\
			     		and reffdate >= '"+report_fromdate+"'\
					and reffdate <= '"+report_todate+"' \
			     		and typeflag = 'Dr'\
					and flag = 1"  	
		totalDr = dbconnect.engines[client_id].execute(statement).fetchone()
		total_dr = totalDr[0]
		statement = "select sum(amount)\
			     		from view_voucherbook\
			     		where projectcode = '"+str(projectcode)+"'\
			     		and account_name = '"+str(queryParams[1])+"'\
			     		and reffdate >= '"+report_fromdate+"'\
					and reffdate <= '"+report_todate+"' \
			     		and typeflag = 'Cr'\
					and flag = 1"  	
		totalCr = dbconnect.engines[client_id].execute(statement).fetchone()
		total_cr = totalCr[0]
		print [total_dr,total_dr]
		if total_dr == None:
			total_dr = 0.00
		
		if total_cr == None:
			total_cr = 0.00	
				
		return [total_dr,total_cr]
	
	def xmlrpc_getBalancesheet(self,queryParams,client_id):
		"""
		Purpose: gets trial balance as on the given date.
		Returns a grid of 4 columns and number of rows depending 
		on number of accounts.
		
		description: This function returns a grid of 4 columns 
		contaning balancesheet.
		Number of rows in this grid will depend on the number 
		of accounts in the database.
		
		Input parameters contains: 
		[org_financial_from,from_date,to_date]
		
		"""
		assetGrpCodes = [6,2,10,9,13]
		liabilitiesGrpCodes = [1,3,11,12]
		balancesheet = []
		assetSrno = 1; liabilitiesSrno = 1
		total_asset_balances = 0.00; 
		total_liabilities_balances = 0.00
		tot_capital = 0.00 
		tot_currliabilities = 0.00 
		tot_loansliabilities = 0.00
		tot_reserves = 0.00
		tot_fixedasset = 0.00
		tot_currentasset = 0.00
		tot_loansasset = 0.00
		tot_investment = 0.00
		tot_miscExpense = 0.00
		account = rpc_account.account()
		for grpCode in liabilitiesGrpCodes:
			print grpCode
			
			accounts = account.xmlrpc_getAccountNamesByGroupCode([grpCode],client_id)
			if accounts != []:
			
				for acc in accounts:
					assetrow = []; liabilitiesrow = []
					closingRow = self.xmlrpc_calculateBalance(\
						[acc,queryParams[0],queryParams[1],queryParams[2]],client_id)
				
					if closingRow[6] == "Cr":
						closingBalanceAmount = float(closingRow[2]) 
					else:
						closingBalanceAmount = - float(closingRow[2])
					if closingBalanceAmount != 0:
						liabilitiesrow.append(liabilitiesSrno)
						liabilitiesrow.append(grpCode)
						liabilitiesrow.append(acc)
						liabilitiesrow.append('%.2f'%(closingBalanceAmount))
						if (grpCode == 1):
							tot_capital += closingBalanceAmount
						if (grpCode == 3):
							tot_currliabilities += closingBalanceAmount
						if (grpCode == 11):
							tot_loansliabilities += closingBalanceAmount
						if (grpCode == 12):
							tot_reserves += closingBalanceAmount
						total_liabilities_balances += closingBalanceAmount
						balancesheet.append(liabilitiesrow)
						liabilitiesSrno += 1
		for grpCode in assetGrpCodes:
			accounts = account.xmlrpc_getAccountNamesByGroupCode([grpCode],client_id)
			if accounts != []:
				for acc in accounts:
					assetrow = []; liabilitiesrow = []
					closingRow = self.xmlrpc_calculateBalance(\
						[acc,queryParams[0],queryParams[1],queryParams[2]],client_id)
				
					if closingRow[6] == "Dr":
						closingBalanceAmount = float(closingRow[2]) 
					else:
						closingBalanceAmount = - float(closingRow[2]) 
					if closingBalanceAmount != 0:
						assetrow.append(assetSrno)
						assetrow.append(grpCode)
						assetrow.append(acc)
						assetrow.append('%.2f'%(closingBalanceAmount))
						if (grpCode == 6):
							tot_fixedasset += closingBalanceAmount
						if (grpCode == 2):
							tot_currentasset += closingBalanceAmount
						if (grpCode == 10):
							tot_loansasset += closingBalanceAmount
						if (grpCode == 9):
							tot_investment += closingBalanceAmount
						if (grpCode == 13):
							tot_miscExpense += closingBalanceAmount
						total_asset_balances += closingBalanceAmount
						balancesheet.append(assetrow)
						assetSrno += 1
		balancesheet.append(assetSrno - int(1))
		balancesheet.append(liabilitiesSrno - int(2))
	
		balancesheet.append('%.2f'%(float(tot_investment)))
		balancesheet.append('%.2f'%(float(tot_loansasset)))
		balancesheet.append('%.2f'%(float(tot_currentasset)))
		balancesheet.append('%.2f'%(float(tot_fixedasset)))
		balancesheet.append('%.2f'%(float(tot_miscExpense)))
		balancesheet.append('%.2f'%(float(tot_currliabilities)))
		balancesheet.append('%.2f'%(float(tot_loansliabilities)))
		balancesheet.append('%.2f'%(float(tot_capital)))
		balancesheet.append('%.2f'%(float(tot_reserves)))
		balancesheet.append('%.2f'%(float(total_liabilities_balances)))
		balancesheet.append('%.2f'%(float(total_asset_balances)))
		print balancesheet
		return balancesheet
		
		
	def xmlrpc_getProfitLoss(self,queryParams,client_id):
		"""
		Purpose: gets trial balance as on the given date.
		Returns a grid of 4 columns and number of rows 
		depending on number of accounts.
		
		description: This function returns a grid of 4 columns 
		contaning profit and loss details.
		
		Number of rows in this grid will depend on the number 
		of accounts in the database.
		
		For profit and loss the accounts from group direct 
		and indirect income and expence are invoke.
		The function first makes a call to the
		getAccountsByGroupCode and stores the list.
		then a loop runs through the list of accounts.
		on every iteration it calls the calculateBalance 
		and passes the account as a parameter along with the 
		financial start, Calculate_from and calculate_to.
		
		Note: profit and loss is always calculated from 
		the starting of the financial year.
		the total of each group of accounts is calculated 
		separately for calculation purpose.
		
		Input parameters contains: 
		[org_financial_from,from_date,to_date]
		
		Otput parameters :List of list
		[serial no,groupcode,accountname,amount,balancetype]
		"""
		grpCodes = [4,5,7,8]
		profitloss = []
		srno = 1
		total_dirInc_balances = 0.00; total_dirExp_balances =0.00
		total_indirInc_balances =0.00; total_indirExp_balances = 0.00
		grossProfit = 0.00 ; grossLoss = 0.00
		netProfit = 0.00 ; netLoss = 0.00
		account = rpc_account.account()
		for grpCode in grpCodes:
			accounts = account.xmlrpc_getAccountNamesByGroupCode([grpCode],client_id)
			if accounts != []:
				for acc in accounts:
					profitlossrow = []
					closingRow = self.xmlrpc_calculateBalance(\
						[acc,queryParams[0],queryParams[1],queryParams[2]],client_id)
					
					print closingRow
					profitlossrow.append(srno)
					profitlossrow.append(grpCode)
					profitlossrow.append(acc)
					profitlossrow.append('%.2f'%(float(closingRow[2])))
					profitlossrow.append(str(closingRow[6]))
					srno = srno + 1
					profitloss.append(profitlossrow)
				
					if grpCode == 5:
						if str(closingRow[6]) == "Dr":
							total_dirExp_balances = total_dirExp_balances + float(closingRow[2])
						else:
							total_dirInc_balances = total_dirInc_balances + float(closingRow[2])
						
					if grpCode == 8:
						if str(closingRow[6]) == "Dr":
							total_indirExp_balances = total_indirExp_balances + float(closingRow[2])
						else:
							total_indirInc_balances = total_indirInc_balances + float(closingRow[2])
					
					if grpCode == 4:
						if str(closingRow[6]) == "Cr":
							total_dirInc_balances = total_dirInc_balances + float(closingRow[2])
						else:
							total_dirExp_balances = total_dirExp_balances + float(closingRow[2])
				
					if grpCode == 7:
						if str(closingRow[6]) == "Cr":
							total_indirInc_balances = total_indirInc_balances + float(closingRow[2])
						else:
							total_indirExp_balances = total_indirExp_balances + float(closingRow[2])
				
				
		profitloss.append('%.2f'%(float(total_dirInc_balances)))
		profitloss.append('%.2f'%(float(total_dirExp_balances)))
		profitloss.append('%.2f'%(float(total_indirInc_balances)))
		profitloss.append('%.2f'%(float(total_indirExp_balances)))
		print "we are in profit and loss"
		print total_dirInc_balances
		print total_dirExp_balances
		print total_indirInc_balances 
		print total_indirExp_balances
		if (total_dirInc_balances > total_dirExp_balances):
			grossProfit = total_dirInc_balances - total_dirExp_balances
			print "gross proftt"
			print grossProfit
			profitloss.append("grossProfit")
			profitloss.append('%.2f'%(float(grossProfit)))
			totalnetprofit = total_indirInc_balances + grossProfit
			if(totalnetprofit > total_indirExp_balances):
				netProfit = totalnetprofit - total_indirExp_balances
				grandTotal = netProfit+total_indirExp_balances
				profitloss.append("netProfit")
				profitloss.append('%.2f'%(float(netProfit)))
				profitloss.append('%.2f'%(float(totalnetprofit)))
				profitloss.append('%.2f'%(float(grandTotal)))
			else:
				netLoss = total_indirExp_balances - totalnetprofit
				grandTotal = netLoss+totalnetprofit
				profitloss.append("netLoss")
				profitloss.append('%.2f'%(float(netLoss)))
				profitloss.append('%.2f'%(float(totalnetprofit)))
				profitloss.append('%.2f'%(float(grandTotal)))
		else:
			grossLoss = total_dirExp_balances - total_dirInc_balances
			profitloss.append("grossLoss")
			profitloss.append('%.2f'%(float(grossLoss)))
			totalnetloss = total_indirExp_balances + grossLoss
			print "totalnetloss"
			print totalnetloss
			if(totalnetloss > total_indirInc_balances):
				netLoss = totalnetloss - total_indirInc_balances
				grandTotal = netLoss+totalnetloss 
				profitloss.append("netLoss")
				profitloss.append('%.2f'%(float(netLoss)))
				profitloss.append('%.2f'%(float(totalnetloss)))
				profitloss.append('%.2f'%(float(grandTotal)))
			else:
				netProfit = total_indirInc_balances - totalnetloss
				grandTotal = netProfit+total_indirInc_balances
				profitloss.append("netProfit")
				profitloss.append('%.2f'%(float(netProfit)))
				profitloss.append('%.2f'%(float(totalnetloss)))
				profitloss.append('%.2f'%(float(grandTotal)))
		print "profit and loss"
			
		print profitloss
		return profitloss	
		
		
		
		
		
		
