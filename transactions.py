import csv
from os import walk

from datetime import *
from dateutil import parser



def clean(string1): 
	parseString = string1

	for i in range(0,3):
		for chars in ['(', ')', ' ', '.', '-', '$', "jpg", "pdf"]: 
			parseString = parseString.strip(chars)

	return parseString

class receipt():
	def __init__(self, name, date, description, amount, status, path, filename):
		self.name = name

		self.date = parser.parse(date.strip(), dayfirst=True)

		self.description = description

		amountString = amount.strip().strip("$")
		self.amount = -float(amountString) 

		self.status = status
		self.path = path
		self.filename = filename

		self.paidDate = None

		parseString = ""


		try:
			parseString = self.status.strip()
			parseString = parseString.rsplit(".",1)[0]
			parseString = parseString.split(" ")[1]
			parseString = parseString.strip("(").strip(")")
			self.paidDate = parser.parse(parseString, dayfirst=True)
			#print(self.paidDate)
		except:
			print(F"ERROR - {self}: {parseString}")
			self.paidDate = None

		#print(self.amount, self.paidDate)
	def __str__(self):
		return F"{self.filename}"

	
class transaction():
	def __init__(self, date, amount, description, balance):

		self.date = parser.parse(date, dayfirst=True)
		self.amount = float(amount)
		self.description = description
		self.balance = balance

		self.type = None

		if(self.amount < 0):
			self.type = "debit"
		else:
			self.type = "credit"




	def __str__(self):

		#datetext = F"{self.date.day}-{self.date.month}-{self.date.year}"
		return F"{self.date}, {self.amount}, {self.description}"

def readTransactions(fileName):
	with open(fileName, 'r') as readFile:
		reader = csv.reader(readFile)
		lines = list(reader)

	transactions = []

	for line in lines:
		#print(line)
		newTransaction = transaction(line[0], line[1], line[2], line[3])
		transactions.append(newTransaction)

	return transactions



def readReceipts(directory):

	f =  []

	receipts = []

	for dirpath,dirnames,filenames in walk(directory, followlinks=True):
		#print(dirpath, filenames)
		#f.extend(filenames)

		for filename in filenames:
			if(filename == "Icon\r" or filename == ".DS_Store"):
				continue
			items = filename.split("-")
			if len(items) == 5:
				receipts.append(receipt(items[0], items[1], items[2], items[3], items[4], dirpath, filename))
			else: 
				print(F"FILENAME ERROR: {filename}")
	return receipts

def main():
	print("Hello, World")

	#testTransaction = transaction("30/10/18", "-50", "Transfer to other NetBank Moreton Refund", "2752.65")

	transactions = readTransactions("2018transactions_copy.csv")
	receipts = readReceipts("/Users/jaricthorning/Google Drive (uqsail@gmail.com)/1.0 Financial/2018")


	print("Matching: ")
	notmatching = []

	count = 0

	variableOffset = 0
	skipped = 0

	foundDate = False
	foundAmount = False

	
	for t in transactions:
		
		if not t.type == "debit":
			continue

		if "STRIPE" in t.description:
			continue

		#if "MYOB" in t.description:
		#	continue
		#print(t)

		foundMatch = False
		

		foundDate = False
		foundAmount = False


		
		foundReceipt = None
		for r in receipts: 

			if(r.paidDate == None):
				#print(F"ERROR - {r}")
				continue

			if r.paidDate == t.date:
				foundDate = r.paidDate
				if t.amount == r.amount:
					foundReceipt = r
					foundAmount = True
					count += 1
					#print(F"{count}) {r.name} - {t.date} - {r.amount} - {r.path}")
					foundMatch = True
					break

				else: 
					#print(F"{r.name} {t.date} DATEMATCH BUT: {t.amount} != {r.amount}")
					pass
			#print(t.date, r.paidDate)
			#print(t.amount, r.amount)

		if(foundReceipt != None):
			receipts.remove(foundReceipt)

		if not foundMatch:
			#t.description += F" foundDate: {foundDate}"
			notmatching.append(t)



	
	count = 0
	print("Unused Receipts: ")
	for r in receipts:
		count += 1
		#print(F"{count}) {t}")
		print(F"{count}, {r}")



	count = 0
	print("Not matching: ")
	for t in notmatching:
		count += 1
		#print(F"{count}) {t}")
		print(F"{count}, {t}")
		pass


	print(f"WARNING SKIPPED: {skipped}")

	#walkDir(".")

if __name__ == "__main__":
	main()