from multiprocessing.connection import Client

'''
import the database connector and functions for stored procedure.
'''
import dbconnect
import rpc_account
import rpc_transaction
import rpc_groups
import rpc_getaccountsbyrule
'''
import the twisted modules for executing rpc calls and 
also to implement the server
'''
from twisted.web import xmlrpc, server
'''
reactor from the twisted library starts the server with a 
published object and listens on a given port.'''
from twisted.internet import reactor
from datetime import datetime,time
from modules import blankspace
from sqlalchemy import or_ , func , and_

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
		
		
		transactions = transaction.xmlrpc_getTransactions([\
					queryParams[0],queryParams[2],queryParams[3],queryParams[4]],client_id)
		
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
		
		# get the groupname accourding to ac
		statement = "select groupname\
			     from group_subgroup_account\
			     where accountname = '"+queryParams[0]+"'"
		result = dbconnect.engines[client_id].execute(statement).fetchone()
		
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
		
		statement = "select sum(amount) as cr_amount\
				from view_voucherbook\
				where typeflag ='Cr'\
				and account_name = '"+queryParams[0]+"'\
				and reffdate >= '"+report_fromdate+"'\
				and reffdate <= '"+report_todate+"'\
				and flag = 1"
		result = dbconnect.engines[client_id].execute(statement).fetchone()
		total_CrBal = result[0]
		
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
			
			closingRow = self.xmlrpc_calculateBalance([account,queryParams[0],queryParams[1],queryParams[2]],client_id)
			
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
			
			if(('%.2f'%float(resultRow[0])!= "0.00" )or('%.2f'%float(resultRow[1])!="0.00")):
				statementRow = [srno,accountRow,accountGroup,'%.2f'%float(resultRow[0]),'%.2f'%float(resultRow[1])]
				totalDr = totalDr + resultRow[0]
				totalCr = totalCr + resultRow[1]
				srno = srno +1
				projectStatement.append(statementRow)
		projectStatement.append(["","","",'%.2f'%float(totalDr),'%.2f'%float(totalCr)])
		return projectStatement
	
	def xmlrpc_getProjectStatement(self,queryParams,client_id):
		'''
		Input parameters:[projectname,accountname,financial_fromdate,fromdate,todate]
		Output :[total_debit,total_credit]
		'''
		
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
		
		if (total_dirInc_balances > total_dirExp_balances):
			grossProfit = total_dirInc_balances - total_dirExp_balances
			
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
		
		return profitloss
		
	def xmlrpc_getReconLedger(self,queryParams,client_id):
		'''
		Purpose : returns a complete ledger for given bank account.
		Information taken from view_voucherbook	
					
		Parameters : For getting ledger it takes the result of rpc_getLedger.
		It expects a list of queryParams which contains
		Input parameters : 
		[accountname,financialStart,fromdate,todate,projectname]
		
		description: Returns a grid (2 dimentional list ) with columns as 
		Date, Particulars, Reference number, Dr amount, Cr amount, 
		narration, Clearance Date and Memo.
		
		Note that It will display the value of clearance date and memo 
		for only those transactions which are cleared.
		The last row will just contain the grand total which will 
		be equal at credit and debit side.
		2nd last row contains the closing balance.
		3rd last row contains just the total Dr and total Cr.
		If the closing balance (carried forward ) is debit 
		then it will be shown at credit side and 
		if it is credit will be shown at debit side.
		
		'''
		
		# create the instance of transaction 
		transaction = rpc_transaction.transaction()
		#first let's get the details of the given account regarding the 
		#Balance and its Dr/Cr side by calling getLedger function.
		#note that we use the getClearanceDate function which gives us 
		#the clearance date and memo for each account in the ledger.
		ledgerResult = self.xmlrpc_getLedger(queryParams,client_id)
		reconResult =[]
		#lets declare vouchercounter to zero
		voucherCounter = 0
		vouchercodeRecords= transaction.xmlrpc_getTransactions([\
					queryParams[0],queryParams[2],queryParams[3],\
					queryParams[4]],client_id)
		
		# following delete operations are done for avoiding clearance date 
		#and memo in opening balance, totaldr, totalcr and grand total rows.
		del ledgerResult[0] #opening balance row
		del ledgerResult[len(ledgerResult)-1] #grand total row
		del ledgerResult[len(ledgerResult)-1] #closing balance row
		del ledgerResult[len(ledgerResult)-1] #total Dr and Cr row
		del ledgerResult[len(ledgerResult)-1] # empty row
		voucherCodes = []
		for vc in vouchercodeRecords:
			voucherCodes.append(int(vc[0]))
		
		#lets append required rows in new list.
		for ledgerRow in ledgerResult:
			reconRow = []
			reconRow.append(ledgerRow[0]) #voucher date
			if (len(ledgerRow[1])==1):
				for acc in ledgerRow[1]:
					reconRow.append(acc) #particular
			reconRow.append(ledgerRow[2]) #ref no
			reconRow.append(voucherCodes[voucherCounter]) #voucher code
			reconRow.append(ledgerRow[3]) #Dr amount
			reconRow.append(ledgerRow[4]) #Cr amount
			reconRow.append(ledgerRow[5]) #narration
			
			clearanceDates =self.xmlrpc_getClearanceDate([\
						str(ledgerRow[1][0]),voucherCodes[voucherCounter]],client_id)
			if clearanceDates == None:
				reconRow.append("")
				reconRow.append("")
			else:
				for datesRow in clearanceDates:
					clrdate = str(datesRow.clearancedate).split(" ")
					clrDate = datetime.strptime(clrdate[0],"%Y-%m-%d").strftime("%d-%m-%Y")
					clrMemo = datesRow.memo
					reconRow.append(clrDate)
					reconRow.append(clrMemo)
				
			voucherCounter = voucherCounter + 1
			reconResult.append(reconRow)
		return reconResult
		
	def xmlrpc_setBankReconciliation(self,queryParams,client_id):
		'''
		Purpose : Sets the bankrecon table in database as saves 
		transaction details of those transactions which are
		cleared with clearance date and memo in table bankrecon
		
		Also sets the reconcode(reconciliation code) for the respective 
		transaction.
				 
		Parameters : It expects a list of queryParams which contains
		[vouchercode(datatype:integer),reffdate(datatype:timestamp),
		accountname(datatype:varchar),dramount(datatype:numeric),
		cramount(datatype:numeric),clearancedate(datatype:timestamp),
		memo(datatype:text)] 
		'''
		# lets create a list containing vouchercode,reffdate,accountname. 
		for clearRow in queryParams:
			sp_params = [clearRow[0],clearRow[1],clearRow[2]]
			
			#if dr_amount is blank, append 0 as dr_amount and respective cr_amount.
			if clearRow[3] == "":
				sp_params.append(0)
				sp_params.append(clearRow[4])
			#if cr_amount is blank, append 0 as cr_amount and respective dr_amount.
			if clearRow[4] == "":
				sp_params.append(clearRow[3])
				sp_params.append(0)
			#Now, lets append respective clearance date and memo				
			sp_params.append(clearRow[5])
			sp_params.append(clearRow[6])
			
			#Finally we are ready to set the bankrecon table.
			success = self.xmlrpc_setBankRecon(sp_params,client_id)
		return success	
		
	def xmlrpc_setBankRecon(self,queryParams,client_id):
		'''
		Input parameters: 
		[vouchercode,reffdate,accountname,dramount,cramount,clearencedate,memo]
		output : String success
		'''
		queryParams = blankspace.remove_whitespaces(queryParams)
		reffdate =  datetime.strptime(str(queryParams[1]),"%d-%m-%Y")
		clearencedate =  datetime.strptime(str(queryParams[5]),"%d-%m-%Y")
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		reconcode = Session.query(func.count(dbconnect.BankRecon.reconcode)).scalar()
		if reconcode == None:
			reconcode = 0
			reconcode = reconcode + 1
		else:
			reconcode = reconcode + 1
		
		result = Session.query(dbconnect.BankRecon).\
					filter(and_(dbconnect.BankRecon.accountname == queryParams[2],\
					dbconnect.BankRecon.vouchercode == queryParams[0])).\
					first()

		if result == None:
			if queryParams[3] == 0:
				# add all values in the bankrecon table
				Session.add(dbconnect.BankRecon(reconcode,queryParams[0],reffdate,queryParams[2],\
							0,queryParams[4],clearencedate,queryParams[6]))
				Session.commit()
			else:	
				# add all values in the bankrecon table
				Session.add(dbconnect.BankRecon(reconcode,queryParams[0],reffdate,queryParams[2],\
							queryParams[3],0,clearencedate,queryParams[6]))
				Session.commit()
		else:
			Session.query(dbconnect.BankRecon).\
			filter(and_(dbconnect.BankRecon.accountname == queryParams[2],\
					dbconnect.BankRecon.vouchercode == queryParams[1])).\
			delete()
			Session.commit()
			if queryParams[3] == 0:
				# add all values in the bankrecon table
				Session.add(dbconnect.BankRecon(reconcode,queryParams[0],reffdate,queryParams[2],\
							0,queryParams[4],clearencedate,queryParams[6]))
				Session.commit()
			else:
				# add all values in the bankrecon table
				Session.add(dbconnect.BankRecon(reconcode,queryParams[0],reffdate,queryParams[2],\
							queryParams[3],0,clearencedate,queryParams[6]))
				Session.commit()
			 
		Session.close()
		connection.connection.close()
		return "success"
		
	def xmlrpc_getClearanceDate(self,queryParams,client_id):
		
		'''
		input parameters :
		[accountname ,vouchercode]
		output :
		[clearance date , memo]	
		'''	
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		result = Session.query(dbconnect.BankRecon).\
				filter(and_(dbconnect.BankRecon.accountname==queryParams[0],\
					dbconnect.BankRecon.vouchercode==queryParams[1])).\
					all()
		
		return result
			
	def xmlrpc_deleteClearedRecon(self,queryParams,client_id):
		'''
		Purpose: To uncleared the cleared trasaction and
		delete cleared entry from bankrecon table 
		
		Input parametes:[accountname,vouchercode,todate]
		'''
		clearencedate =  str(datetime.strptime(str(queryParams[2]),"%d-%m-%Y"))
		connection = dbconnect.engines[client_id].connect()
		Session = dbconnect.session(bind=connection)
		result = Session.query(dbconnect.BankRecon).\
			filter(and_(dbconnect.BankRecon.accountname==queryParams[0],\
			dbconnect.BankRecon.vouchercode==queryParams[1],\
			dbconnect.BankRecon.clearancedate < clearencedate)).delete()
		
		Session.commit()
		Session.close()
		connection.connection.close()
		
		if result == True:
			return True
		else:
			return False
			
			
	
	def xmlrpc_updateBankRecon(self,queryParams,client_id):
		"""
		Purpose: Returns all uncleared transactions from the starting of 
		financial year to the end date of given period with 
		Bank Reconciliation Statement for the given period of time.
		 
		Input Parameters: 
		[account name, financial start, fromdate and todate,projectname]
		
		Description:This function returns a grid of 7 columns and number 
		of rows depending on number of uncleared transactions in the database. 
		After appending uncleared transactions in grid, 
		it appends Bank Reconciliation statement.
		
		A grid of 7 columns contains:
		transaction date, accountname, vouchercode, reference number, 
		dramount, cramount and narration.
		
		The function first makes a call to the previous function "getLedger" 
		and passes the account as a parameter along with the 
		financial start, Calculate_from and calculate_to.
		
		Note that balance is always calculated from the starting of the financial year.
		Then, on every iteration it calls following functions 
		1. getTransactions: to get trnsactions from starting date of 
			financial year to the end date of given period
		2. getParticulars: to get all particulars(account names) 
			for that period
		3. getOnlyClearedTransactions: to filter out all uncleared 
			transactions and their details.
		"""
		ReconGrid = []
		totalDbt = 0.00
		totalCdt = 0.00
		# create the instance of transaction 
		transaction = rpc_transaction.transaction()
		#now lets get  te transaction details for this account.
		transactions =transaction.xmlrpc_getTransactions([\
					queryParams[0],queryParams[2],queryParams[3],queryParams[4]],client_id)
		
					
		# [vouchercode , voucherflag , reff_date , voucher_reference,transaction_amount,show_narration]			
		# fill up the grid with the rows for transactions.
		for transactionRow in transactions:
			
			# if the transaction had the amount at Dr side then particulars
			# must have the names of accounts involved in Cr.
			if transactionRow[1] == "Dr":
				particulars = transaction.xmlrpc_getParticulars([transactionRow[0],"Cr"],client_id)
				# [voucher_code,type_flag]
				
				ledgerRow = []
				#may be more than one account was involved at the other side so loop through.
				for particularRow in particulars:
					
					cleared =transaction.xmlrpc_getOnlyClearedTransactions([\
							str(particularRow),int(transactionRow[0]),\
							queryParams[2],queryParams[3]],client_id)

					if cleared == False:
						ledgerRow.append(transactionRow[2])
						ledgerRow.append(particularRow)
						ledgerRow.append(transactionRow[3])
						ledgerRow.append(transactionRow[0])
						ledgerRow.append('%.2f'%(float(transactionRow[4])))
						totalDbt = totalDbt + float(transactionRow[4])
						ledgerRow.append("")
						ledgerRow.append(transactionRow[5])
						ReconGrid.append(ledgerRow)
					
			if transactionRow[1] == "Cr":
				particulars = transaction.xmlrpc_getParticulars([transactionRow[0],"Dr"],client_id)
				# [voucher_code,type_flag]
				ledgerRow = []
				#may be more than one account was involved a tthe other side so loop through.
				for particularRow in particulars:
					cleared =transaction.xmlrpc_getOnlyClearedTransactions(\
							[str(particularRow),int(transactionRow[0]),\
								queryParams[2],queryParams[3]],client_id)
					
					if cleared == False:
						ledgerRow.append(transactionRow[2])
						ledgerRow.append(particularRow)
						ledgerRow.append(transactionRow[3])
						ledgerRow.append(transactionRow[0])
						ledgerRow.append("")
						ledgerRow.append('%.2f'%(float(transactionRow[4])))
						ledgerRow.append(transactionRow[5])
						totalCdt = totalCdt + float(transactionRow[4])
						ReconGrid.append(ledgerRow)
					
		ReconGrid.append(["","","Total","",'%.2f'%(totalDbt),'%.2f'%(totalCdt)])
		#lets start making Reconcilition Statement,
		ReconGrid.append(["","RECONCILIATION STATEMENT","","","","AMOUNT"])
		#get the ledger Grid result,
		ledgerResult = self.xmlrpc_getLedger(queryParams,client_id)
		
		BankBal = 0.00
		closingBal = 0.00		
		midTotal = 0.00
		
		#lets get the closing row for closing balance
		closingBalRow = ledgerResult[len(ledgerResult)-2]
		#total of Dr and Cr
		TotalDrCrRow = ledgerResult[len(ledgerResult)-4]
		
		# if opening balance is debit then add opening balance to 
		# total debit amount else to total credit amount
		if ledgerResult[0][2] =="":
			openingBalRow = ledgerResult[0]
			if openingBalRow[3] != "":
				TotalDrCrRow[3] = float(TotalDrCrRow[3]) + float(openingBalRow[3])
			else:
				TotalDrCrRow[4] = float(TotalDrCrRow[4]) + float(openingBalRow[4])
		
		balancedate = str(queryParams[2])
		
		ClosingBalance = float(TotalDrCrRow[3]) - float(TotalDrCrRow[4])
		
		if closingBalRow[3] != "":
			ReconGrid.append([balancedate,"Balance as per our book (Credit) on "+balancedate,"","","",closingBalRow[3]])
			closingBal = float(closingBalRow[3])
			
		if closingBalRow[4] != "":
			ReconGrid.append([balancedate,"Balance as per our book (Debit) on "+balancedate,"","","",closingBalRow[4]])
			closingBal = float(closingBalRow[4])
			
		if ClosingBalance == 0:
			ReconGrid.append([balancedate,"Balance as per our book on "+balancedate,"","","",closingBalRow[3]])
			closingBal = float(closingBalRow[3])
		
		if  ClosingBalance >= 0:
			if totalCdt != 0:
				ReconGrid.append(["","Add: Cheques issued but not presented","","","","+ "+'%.2f'%(totalCdt)])
			else:
				ReconGrid.append(["","Add: Cheques issued but not presented","","","",'%.2f'%(totalCdt)])
			midTotal = closingBal + totalCdt
			ReconGrid.append(["","","","","",""+'%.2f'%(midTotal)])
			if totalDbt != 0:
				ReconGrid.append(["","Less: Cheques deposited but not cleared","","","","- "+'%.2f'%(totalDbt)])
			else:
				ReconGrid.append(["","Less: Cheques deposited but not cleared","","","",'%.2f'%(totalDbt)])
			BankBal = midTotal - totalDbt
			
			
		if  ClosingBalance < 0:
			if totalCdt != 0:
				ReconGrid.append(["","Add: Cheques issued but not presented","","","","+ "+'%.2f'%(totalCdt)])
			else:
				ReconGrid.append(["","Add: Cheques issued but not presented","","","",'%.2f'%(totalCdt)])
			midTotal = totalCdt - closingBal
			ReconGrid.append(["","","","","",""+'%.2f'%(abs(midTotal))])
			if totalDbt != 0:
				ReconGrid.append(["","Less: Cheques deposited but not cleared","","","","- "+'%.2f'%(totalDbt)])
			else:
				ReconGrid.append(["","Less: Cheques deposited but not cleared","","","",'%.2f'%(totalDbt)])
			BankBal = midTotal - totalDbt

		if BankBal < 0:
			ReconGrid.append(["","Balance as per Bank (Debit)","","","",'%.2f'%(abs(BankBal))])

		if BankBal > 0:
			ReconGrid.append(["","Balance as per Bank (Credit)","","","",'%.2f'%(abs(BankBal))])
			
		if BankBal == 0:
			ReconGrid.append(["","Balance as per Bank","","","",'%.2f'%(abs(BankBal))])
			
		return ReconGrid	
		
	def xmlrpc_getCashFlow(self,queryParams,client_id):
		""" Purpose: Returns the data for CashFlow in a grid format
		Input parameters : *financial_from ,startdate and end date
		description:This function takes one arguement queryParams 
		which is a list containing
		The function will return a grid with 4 columns.
		first 2 columns will have the account name and its sum of
		received amount, while next 2 columns will have the same 
		for amount paid.first we make a call to get CashFlowAccounts 
		for the list of accounts falling under Bank or Cash subgroups.
		Then a loop will run through the list and get the list of 
		payment and receipts as mentioned above.
		every row will contain a pair of 
		account:amount for payment and receipt each.
		"""
		#declare the cashFlowGrid, rlist, plist as a blank list.
		#we will fill up cashFlowGrid by appending rlist and plist.
		#rlist will contain the cashflow of received accounts.
		#plist will contain the cashflow of paid accounts.
		cashFlowGrid = []
		rlist = []
		plist = []
		account = rpc_account.account()
		getjournal = rpc_getaccountsbyrule.getaccountsbyrule()
		rlist.append(["Opening Balance","",""])
		#Let's start with 0 for totalreceivedamount and totalpaid amounts.
		totalreceivedamount = 0.00
		totalpaidamount = 0.00
		#first let's get the list of all accounts coming under cash or 
		#bank subgroup and their respective opening balance.
		cashBankAccounts=account.xmlrpc_getCashFlowOpening(client_id)
		#fill up the rlist with the rows for cashFlowAccounts.
		#also maintaining a list of cash and bank accounts will facilitate 
		#the loop for getting actual cash flow.
		cbAccounts = []
		for acc in cashBankAccounts:
			openingRow = []
			openingRow.append("ob")
			openingRow.append(acc[0])
			cbAccounts.append(acc[0])
			
			openinglist = closingRow = self.xmlrpc_calculateBalance(\
						[str(acc[0]),queryParams[0],queryParams[1],queryParams[2]],client_id)
			openingRow.append('%.2f'%float(openinglist[1]))
			totalreceivedamount = totalreceivedamount + float(openinglist[1])
			rlist.append(openingRow)
		
		
		cfAccountsRows = getjournal.xmlrpc_getJournalAccounts(client_id)
		#now we will run a nested loop for getting cash flow for all non-cash/bank accounts
		# the outer loop will run through the list of all the cfAccounts 
		#and check for any transactions on them involving bank or 
		#cash based accounts for which we have a list of cbAccounts
		#needless to say this process will happen once for recieved and one for paid transactions.
		for acc in cfAccountsRows:
			receivedAmount = 0.00
			for cb in cbAccounts:
				#print "checking with account " + str(account[0]) + " against " + cb
				
				receivedRow = account.xmlrpc_getCashFlowReceivedAccounts([\
					str(acc),str(cb),queryParams[1],queryParams[2]],client_id)
				#print"the amount for given combination is " + str(receivedRow["cfamount"]) 
				if receivedRow != None:
					receivedAmount = receivedAmount + float(str(receivedRow[0]))
			if receivedAmount != 0:
				rlist.append([acc,'%.2f'% receivedAmount,""])	
				totalreceivedamount = totalreceivedamount + float(receivedAmount)
				#print rlist	
		#print "received samapt hue"
		#print "finally the total of received with opening is " + str(totalreceivedamount)
		#print "now into the payed loop "
		for acc in cfAccountsRows:
			paidAmount = 0.00
			for cb in cbAccounts:
				#print "checking with account " + str(account[0]) + " against " + cb
				
				paidRow =account.xmlrpc_getCashFlowPaidAccounts([\
					str(acc),str(cb),queryParams[1],queryParams[2]],client_id)
				if paidRow!= None:
					paidAmount = paidAmount + float(str(paidRow[0]))  
			if paidAmount != 0:
				plist.append([acc,'%.2f'% paidAmount,""])
				
				totalpaidamount = totalpaidamount + float(paidAmount)
		plist.append(["Closing Balance","",""])
				#print plist
			#fill up the rlist with the rows for cashFlowAccounts only if receivedRow is not none.
				#now sum up the totalreceived amounts.
		for closingcb in cbAccounts:
			closingCbRow = []
			
			closinglist=self.xmlrpc_calculateBalance(\
						[str(closingcb),queryParams[0],queryParams[1],queryParams[2]],client_id)
			closingCbRow.append("cb")
			closingCbRow.append(closingcb)
			closingCbRow.append('%.2f'%float(closinglist[2]))
			print closingCbRow
			totalpaidamount = totalpaidamount + float(closinglist[2])
			plist.append(closingCbRow)
		# fill up the plist with the rows for cashFlowAccounts only if paidRow is not none.
		# now sum up the totalpaid amounts.
		# Now lets equate the row of rlist and plist.
		rlength = len(rlist)
		plength = len(plist)
		# if length of rlist is greater than plist then append the blank lists 
		# times of difference in rlist and plist into the plist or vice versa.
		if rlength > plength:
			diflength = rlength - plength
			for d in range(0,diflength):
				plist.append(["","",""])
		if rlength < plength:
			diflength = plength - rlength
			for d in range(0,diflength):
				rlist.append(["","",""])
		#now append the total receivedamount and total paidamount in respective lists i.e. rlist and plist
		rlist.append(["Total",'%.2f'% totalreceivedamount,""])
		plist.append(["Total",'%.2f'% totalpaidamount,""])
		
		#now append rlist and plist to cashFlowGrid
		cashFlowGrid.append(rlist)
		cashFlowGrid.append(plist)
		return cashFlowGrid
		'''
		rlength = len(cashFlowGrid[0])
		plength = len(cashFlowGrid[1])
		finalList =[]
		if rlength > plength:
			difflength = rlength
		else:
			difflength = plength
		for i in range (0, difflength):
			if cashFlowGrid[0][i][0] == "ob" :
				if cashFlowGrid[1][i][0] != "cb" :
			
					finalList.append([cashFlowGrid[0][i][1],\
							cashFlowGrid[0][i][2],\
							cashFlowGrid[1][i][0],\
							cashFlowGrid[1][i][1]])
				

			elif cashFlowGrid[0][i][0] == "ob" :
				if cashFlowGrid[1][i][0] == "cb" :
					finalList.append([cashFlowGrid[0][i][1],\
							cashFlowGrid[0][i][2],\
							cashFlowGrid[1][i][1],\
							cashFlowGrid[1][i][2]])
					
			
			elif cashFlowGrid[1][i][0] == "cb" :
				finalList.append([cashFlowGrid[0][i][0],\
						cashFlowGrid[0][i][1],\
						cashFlowGrid[1][i][1],\
						cashFlowGrid[1][i][2]])
			else:
				finalList.append([cashFlowGrid[0][i][0],\
						cashFlowGrid[0][i][1],\
						cashFlowGrid[1][i][0],\
						cashFlowGrid[1][i][1]])	
		
		return finalList
		'''
		
