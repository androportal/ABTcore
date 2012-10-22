from multiprocessing.connection import Client

'''
import the database connector and functions for stored procedure.
'''
import dbconnect
import rpc_account
import rpc_transaction
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


class reports(xmlrpc.XMLRPC):
	"""class name is aacount which having different store procedures"""
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
		[Date, Particulars, Reference number, Dr, Cr , vouchercode.]
		
		Description : Note that last 3 rows have the narration column blank.
		The 3rd last row contains just the total Dr and total Cr.
		the second last row contains the closing balance.
		If the closing balance (carried forward ) is Dr then it will be shown at Cr side.
		The C/F balance if Cr will be shown at Dr side.
		The last row will just contain the grand total which will be equal at credit and debit side.
		'''
		#first let's get the details of the given account regarding the
		#Balance and its Dr/Cr side.
		#note that we use the calculateBalance function which gives us
		#the B/f balance, C/F balance group type and type of the balance.
		#we will not use this if a project is specified, as there is no 
		#point in displaying opening balance.
		#if all transactions are to be searched then project 
		#(queryparams[4]) will be "No Project".
		
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
				ledgerGrid.append([openingdate,"Opening Balance b/f","",'%.2f'%(openingBalance),"","",""])
			if balanceRow[5] == "Cr":
				openingdate = datetime.strptime(str(queryParams[1]),"%d-%m-%Y").strftime("%d-%m-%Y")
				ledgerGrid.append([openingdate,"Opening Balance b/f","","",'%.2f'%(openingBalance),"",""])
				
		else:
			#its 0 so will be set to 0.
			totalDr= 0.00
			totalCr = 0.00
		# create the instance of transaction 
		transaction = rpc_transaction.transaction()
		# call getTransactions to get the transaction details for this account.
		transactions = transaction.xmlrpc_getTransactions([queryParams[0],queryParams[2],queryParams[3],queryParams[4]],client_id)

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
				ledgerRow.append(particular[0])
				ledgerRow.append(transactionRow[3])
				ledgerRow.append('%.2f'%(float(transactionRow[4])))
				totalDr = totalDr + float(transactionRow[4])
				ledgerRow.append("")
				ledgerRow.append(transactionRow[5])
				
			if transactionRow[1] == "Cr":
				particulars = transaction.xmlrpc_getParticulars([transactionRow[0],"Dr"],client_id)
				particular = []
				for particularRow in particulars:
					particular.append(particularRow)
				ledgerRow.append(particular[0])
				ledgerRow.append(transactionRow[3])
				ledgerRow.append("")
				ledgerRow.append('%.2f'%(float(transactionRow[4])))
				totalCr = totalCr + float(transactionRow[4])
				ledgerRow.append(transactionRow[5])
			ledgerRow.append(transactionRow[0])
			ledgerGrid.append(ledgerRow)
		#the transactions have been filled up duly.
		#now for the total dRs and Crs, we have added them up nicely during the grid loop.
		ledgerGrid.append(["","Total of Transactions","",'%.2f'%(totalDr),'%.2f'%(totalCr),"",""])
		if queryParams[4] == "No Project":
			ledgerGrid.append(["","","","","","",""])
			grandTotal = 0.00
			closingdate = datetime.strptime(str(queryParams[3]),"%d-%m-%Y").strftime("%d-%m-%Y")
			if balanceRow[6] == "Dr":
			#this is a Dr balance which will be shown at Cr side.
			#Difference will be also added to Cr for final balancing.
				ledgerGrid.append([closingdate,"Closing Balance c/f","","",'%.2f'%(balanceRow[2]),"",""])
				grandTotal =float(balanceRow[4])  + float(balanceRow[2])
			if balanceRow[6] == "Cr":
			#now exactly the opposit, see the explanation in the if condition preceding this one.

				ledgerGrid.append([closingdate,"Closing Balance c/f","",'%.2f'%(balanceRow[2]),"","",""])
				grandTotal =float(balanceRow[3])  + float(balanceRow[2])
			ledgerGrid.append(["","Grand Total","",'%.2f'%(grandTotal),'%.2f'%(grandTotal),"",""])
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
		statement = "select groupname\
			     from group_subgroup_account\
			     where accountname = '"+queryParams[0]+"'"
		result = dbconnect.engines[client_id].execute(statement).fetchone()
		#print "result"
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
		list containing list [serial no , accountname , groupname , debit bal , creadit bal ]
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
		total_balances = ['%.2f'%total_dr,'%.2f'%total_cr]
		trialBalance.append(total_balances)
	
		return trialBalance	
		
		
		
		
		
		
		
		
		
