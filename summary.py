import sys
import os
import datetime
import subprocess
import numpy as np
import matplotlib as mp
import argparse

from stat import *

from fpdf import FPDF

ignoreFiles = [".DS_Store", "Icon\r"]
printReceipts = False

class Receipt:
		def __init__(self, name, account):

				self.name = name
				self.paidBy = None
				self.amount = 0
				self.paidDate = None
				self.description = None
				self.date = None
				self.account = account
				self.type = None


		def __str__(self):
			return "Account: %s - %s" % (self.account, self.name)

class Account:
	def __init__(self, name):
		self.receipts = []
		self.name = name
		self.accountName = self.name.split('/')[-1]

		self.hasSubAccount = False


		self.level = len(self.name.split('/'))

		return

	def getSum(self):
		return sum(r.amount for r in self.receipts)

	def getName(self): return self.name

	def setHasSubAccount(self, hasSubAccount):
		self.hasSubAccount = hasSubAccount

	def addReceipt(self, receipt):
		self.receipts.append(receipt)

	def printFormat(self):

		#return (F"{account_name}")
		
		return '{:<30s}'.format(self.level * 3 * " " + self.accountName) + '{:<2}'.format("$") + '{:>20.2f}'.format(float(self.getSum()))
			

		# if(printReceipts):
		#     for r in self.receipts:
		#         if(r.getName() != "ERROR"):
		#             print r.getName(),":",str(r.getAmount())

   
	def getPrint(self):
		account_name = self.name.split('/')[-1]
		return f'{account_name}: ${self.getSum()}'
		# return '{:<30s}'.format(self.level * 3 * " " + self.name.split("/")[-1]), '{:<2}'.format("$") + '{:>10.2f}'.format(float(self.getSum()))
	def __str__(self):
		return self.getPrint()

	def __lt__(self, other):

		if(self.name == "Grand Total"): 
			return False
		if(other.name == "Grand Total"): 
			return True
		return self.name < other.name



def visitfile(top, filename):
	# print(filename)
	pass

def walktree(top, callback, account):

		subAccounts = []
		x = Account(account)

		subAccounts.append(x)

		errorReceipts = []

		for f in os.listdir(top):
				pathname = os.path.join(top, f)
				mode = os.stat(pathname)[ST_MODE]
				if S_ISDIR(mode):
						# New Account Found
						#Summaries Account
						x.setHasSubAccount(True)

						nextAccount = f
						if(account != "Grand Total"):
							nextAccount = account + "/" + f

						totalAccount, returnedAccounts, errors = walktree(pathname, callback, nextAccount)

						for e in errors:
							errorReceipts.append(e)

						for a in returnedAccounts:
							subAccounts.append(a) 

						newReceipt = Receipt(f, x)
						if(newReceipt != -1):
							newReceipt.amount = totalAccount
							x.addReceipt(newReceipt)

				elif S_ISREG(mode):
						# It's a file, call the callback function
						# callback(top, f)
						newReceipt = processReceipt(f, x)
						if(newReceipt != -1):
							x.addReceipt(newReceipt)
						else: 
							if(f not in ignoreFiles):
								print(F"Error: {f}")
								errorReceipts.append(f)
				else:
						# Unknown file type, print a message    
						print(F"Skipping {pathname}")


		subAccounts.sort()
		#x.printAccount()
		return x.getSum(), subAccounts, errorReceipts


def processReceipt(receiptString, account):

	parts = receiptString.split("-")
	partsLen = len(parts)

	newReceipt = Receipt(receiptString, account)

	newReceipt.account = account

	if(partsLen == 4):
		#potentially unpaid receipt
		newReceipt.paidDate = None
	elif(partsLen == 5):
		#potential paid receipt
	   
		if "PAID" in parts[4]:
			if "UNPAID" not in parts[4]:
				newReceipt.paidDate = parts[4][parts[4].find("("):parts[4].find(")")]
				newReceipt.type = "PAID"
			else:
				newReceipt.type = "UNPAID"
		
		elif "SCANNED" in parts[4]:
			newReceipt.type = "SCANNED"

		elif "PENDING" in parts[4]:
			newReceipt.type = "PENDING"


		#attempt to extract paid date 
	else: 
		return -1


	newReceipt.paidBy = parts[0]
	newReceipt.date = parts[1]
	newReceipt.description = parts[2]

	try:
		newReceipt.amount = float(parts[3].strip()[1:])
	except Exception as e:
		return -1

	return newReceipt

def walktreeiterative(top):


	accounts = []

	accountStack = []


	#Add root to process first

	accountStack.append(".")

	while len(accountStack) > 0:

		directory = os.path.join(top, accountStack[0])
		account = Account(accountStack[0])

		for f in os.listdir(directory):
			pathname = os.path.join(directory, f)
			mode = os.stat(pathname)[ST_MODE]
			
			if S_ISDIR(mode):
				#if is file, create new account and add to stack

				accountStack.append(pathname)

			elif S_ISREG(mode):
				newReceipt = processReceipt(f, account)
				print(F"Found Receipt: {newReceipt}")
			else:
				print(F"Skipping {pathname}")

		dirStack.remove(parent)


def paidTo(accounts, filter): 

	paid = {}
	for a in accounts:
		for r in a.receipts:
			if r.type == filter:
				if r.paidBy != None:
					if paid.get(r.paidBy) == None:
						paid[r.paidBy] = r.amount
					else:
						paid[r.paidBy] += r.amount		
				else: 
					print(F"Couldn't assign : {r}")
	return paid

class PDF:
	def __init__(self):
		self.pdf = FPDF(orientation = 'P', unit = 'mm', format='A4')
		self.pdf.add_page()

	
	def add_title(self, title):
		self.pdf.ln(15)
		self.pdf.set_font('Courier', 'B', 16)
		self.pdf.cell(130, 10, title,1, 1, 'C')

	def add_subtitle(self, subtitle):
		self.pdf.set_font('Courier', 'B', 9)
		self.pdf.cell(130, 10, subtitle,0, 1)

	def add_heading1(self, heading): 
		self.pdf.set_font('Courier', 'B', 14)
		self.pdf.cell(130, 10, heading,0, 1)

	def add_centered_text(self, text):
		self.pdf.set_font('Courier', '', 11)
		self.pdf.cell(0 , 7, text, 0, 1, 'C')

def getRelativeDir(directory):
	foundRoot = False
	relativeDir = ""
	localDir = ""
	directoryLookBack = -1
	while(localDir == ""):
		localDir = directory.split("/")[directoryLookBack]
		directoryLookBack -= 1
		if(directoryLookBack > len(directory.split("/"))):
			localDir = directory
			break
	for d in directory.split("/"):
		if(d == "1.0 Financial"):
			foundRoot = True

		if foundRoot:
			relativeDir += d
			if(d != ""):
				relativeDir += "/"

	if(foundRoot == False):
		relativeDir = directory

	return relativeDir, localDir
		

def printResult(totalamount, accounts, errorReceipts, directory):
	print("Printing Results...")

	print(F"Total Amount is {totalamount}")

	relativeDir, localDir = getRelativeDir(directory)

	now = datetime.date.today()

	for a in accounts:
		print(F"{a.level * 3 * ' '}{a.accountName}".ljust(50) + "$" + F"{float(a.getSum()):.2f}".rjust(12))

	paid = paidTo(accounts, "PAID")

	print("\nPaid: ")
	if(len(paid) != 0):
		for person, amount in sorted(list(paid.items()), key=lambda x: x[1], reverse=True):
			print(F"{person}".ljust(50) +"$"+ F"{float(amount):.2f}".rjust(12))    
	else: 
		print("None") 


	pending = paidTo(accounts, "PENDING")

	print("\nPending: ")
	if(len(pending) != 0):
		for person, amount in sorted(list(pending.items()), key=lambda x: x[1], reverse=True):
			print(F"{person}".ljust(50) +"$"+ F"{float(amount):.2f}".rjust(12))
	else: 
		print("None") 

	unpaid = paidTo(accounts, "UNPAID")

	print("\nUnpaid: ")
	if(len(unpaid) != 0):
		for person, amount in sorted(list(unpaid.items()), key=lambda x: x[1], reverse=True):
			print(F"{person}".ljust(50) +"$"+ F"{float(amount):.2f}".rjust(12))
	else: 
		print("None") 

	
	print("\nUnable to process")

	if(len(errorReceipts) > 0):
		for e in errorReceipts:
			print(e)

	else: 
		print("None") 


def generatePDF(totalamount, accounts, errorReceipts, directory):

	print("Generating PDF...")

	relativeDir, localDir = getRelativeDir(directory)

	report = PDF()
	now = datetime.date.today()

	report.add_title(F"UQ Sailing Club Accounts    {now}")
	report.add_subtitle(F"/{relativeDir}")
	report.pdf.ln(10)
	report.add_heading1(F"Receipts")
	
	report.pdf.image(F"{os.path.dirname(os.path.realpath(__file__))}/uqsail.png", 150, 10, 40, 40, "", "")
	for a in accounts:
		report.add_centered_text(F"{a.level * 3 * ' '}{a.accountName}".ljust(50) + "$" + F"{float(a.getSum()):.2f}".rjust(12))    

	report.pdf.add_page()
	report.add_heading1(F"Reimbursements - Paid")

	paid = paidTo(accounts, "PAID")
	total_paid = 0

	if(len(paid) != 0):

		for person, amount in sorted(list(paid.items()), key=lambda x: x[1], reverse=True):
			report.add_centered_text(F"{person}".ljust(50) +"$"+ F"{float(amount):.2f}".rjust(12))
			total_paid += amount
		report.add_centered_text(F"TOTAL PAID".ljust(50) +"$"+ F"{float(total_paid):.2f}".rjust(12))

	else: 
		report.add_centered_text("None")

	report.add_heading1(F"Reimbursements - Pending")

	pending = paidTo(accounts, "PENDING")
	total_pending = 0

	if(len(paid) != 0):

		for person, amount in sorted(list(pending.items()), key=lambda x: x[1], reverse=True):
			report.add_centered_text(F"{person}".ljust(50) +"$"+ F"{float(amount):.2f}".rjust(12))
			total_pending += amount
		report.add_centered_text(F"TOTAL PENDING".ljust(50) +"$"+ F"{float(total_pending):.2f}".rjust(12))

	else: 
		report.add_centered_text("None")
	
	report.add_heading1("Reimbursements - Unpaid")

	unpaid = paidTo(accounts, "UNPAID")
	total_unpaid = 0

	if(len(unpaid) != 0):
		for person, amount in sorted(list(unpaid.items()), key=lambda x: x[1], reverse=True):
			report.add_centered_text(F"{person}".ljust(50) +"$"+ F"{float(amount):.2f}".rjust(12))
			total_unpaid += amount

		report.add_centered_text(F"TOTAL UNPAID".ljust(50) +"$"+ F"{float(total_unpaid):.2f}".rjust(12))	

	else: 

		report.add_centered_text("None")

	report.add_subtitle("Unable to Process")

	if(len(errorReceipts) > 0):
		for e in errorReceipts:
			report.add_centered_text(e)
	else: 
		report.add_centered_text("None")


	pdfFileName = F'UQSail Receipts ({localDir}) - {datetime.date.today()}.pdf' 

	report.pdf.output(pdfFileName, 'F')   

	subprocess.call(['open', pdfFileName])
	#pdf.output(F"report-{now}.pdf", 'F')

def checkDirectory(directory):
	if directory == None:
		print("Directory must be set.")
		return False

	return True

def interactive(directory):

	while(True):
		command = input("Enter command> ")
		#print(command)

		if command == "directory" or command == "d":
			print(F"Current directory is: {directory}")
			option = input("Change directory? (y/n)> ")
			if option == "y" or option == "yes":
				directory = input("Enter new directory> ")


		if command == "search" or command == "s":
			print(F"- Enter search parameters - " )
			startDate = input("Start date (dd/mm/yy): ")
			print(F"Start date selected: {startDate}")
			endDate = input("End date (dd/mm/yy): ")
			print(F"Start date selected: {endDate}")

		if command == "summary":
			if not checkDirectory(directory):
				pass
			else: 
				totalamount, accounts, errorReceipts = walktree(directory, visitfile, "Grand Total")
				printResult(totalamount, accounts, errorReceipts, directory)

		if command == "pdf":
			if not checkDirectory(directory):
				pass
			else: 
				totalamount, accounts, errorReceipts = walktree(directory, visitfile, "Grand Total")
				generatePDF(totalamount, accounts, errorReceipts, directory)



def main():
	
	parser = argparse.ArgumentParser(description='Process some integers.')

	
	parser.add_argument('-c', help='print to command-line ', action='store_true')
	parser.add_argument('-p', help='generate PDF', action='store_true')
	parser.add_argument('--directory', '--dir', '-d', help='directory')#, required='False')
	parser.add_argument('--interactive', '-i', help='interactive mode', action='store_true')
	args = parser.parse_args()

	if not args.interactive and args.directory is None: 
		parser.error("Non-Interactive mode requires --directory")

	

	#walktreeiterative(directory)
	
	directory = args.directory

	if not args.interactive:
		
		totalamount, accounts, errorReceipts = walktree(directory, visitfile, "Grand Total")
		if args.c:
			printResult(totalamount, accounts, errorReceipts, directory)
		if args.p:
			generatePDF(totalamount, accounts, errorReceipts, directory)
	else: 
		#interactive mode
		interactive(directory)

				

if __name__ == '__main__':
	main()
