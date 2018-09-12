import sys
import os
import datetime
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
       
        if "PAID" in parts[4] and "UNPAID" not in parts[4]:
            newReceipt.paidDate = parts[4][parts[4].find("("):parts[4].find(")")]
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
            if r.paidBy != None:
                if(filter == "PAID"):
                    if(r.paidDate == None):
                        break
                elif(filter == "UNPAID"):
                    if(r.paidDate != None):
                        break

                if paid.get(r.paidBy) == None:
                    paid[r.paidBy] = r.amount
                else:
                    paid[r.paidBy] += r.amount

    return paid

class PDF:
    def __init__():
        self.pdf = PDF(orientation = 'P', unit = 'mm', format='A4')
        self.pdf.add_page()

    
    def add_title(self, title):
        pdf.ln(15)
        pdf.set_font('Courier', 'B', 16)
        pdf.cell(130, 10, title,1, 1, 'C')

    def add_subtitle(self, subtitle):
        pdf.set_font('Courier', 'B', 9)
        pdf.cell(130, 10, subtitle,0, 1)

    def add_heading1(self, heading): 
        self.pdf.set_font('Courier', 'B', 14)
        self.pdf.cell(130, 10, heading,0, 1)

    def add_centered_text(self, text):
        pdf.set_font('Courier', '', 11)
        self.pdf.cell(130 , 7, text, 0, 1, 'C')

def generatePDF(directory):

    print("Generating PDF...")

    totalamount, accounts, errorReceipts = walktree(directory, visitfile, "Grand Total")

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

    report = PDF()
    report.pdf.add_page()
    now = datetime.date.today()

    report.add_title(F"UQ Sailing Club Accounts    {now}")
    report.add_subtitle(F"/{relativeDir}")
    report.pdf.ln(10)
    report.add_heading1(F"Receipts")
    
    pdf.image("uqsail.png", 150, 10, 40, 40, "", "")
    for a in accounts:
        report.add_centered_text(F"{a.level * 3 * ' '}{a.accountName}".ljust(50) + "$" + F"{float(a.getSum()):.2f}".rjust(12))    

    report.pdf.add_page()
    report.add_heading1(F"Reimbursements - Paid")

    paid = paidTo(accounts, "PAID")

    print("\nPaid: ")
    if(len(paid) != 0):

        for person, amount in sorted(list(paid.items()), key=lambda x: x[1], reverse=True):
            text = F"{person}".ljust(50) +"$"+ F"{float(amount):.2f}".rjust(12)
            report.add_centered_text(text)
            print(text)    
    else: 
        text = "None"
        report.add_centered_text(text)
        print(text) 
    
    report.add_heading1("Reimbursements - Yet to be paid")

    unpaid = paidTo(accounts, "UNPAID")

    print("\nUnpaid: ")
    if(len(unpaid) != 0):
        for person, amount in sorted(list(unpaid.items()), key=lambda x: x[1], reverse=True):
            text = F"{person}".ljust(50) +"$"+ F"{float(amount):.2f}".rjust(12)
            pdf.cell(0, 7, text,0, 1, 'C')
            print(text)
    else: 
        text = "None"
        pdf.cell(0, 7, text,0, 1, 'C')
        print(text) 

    
    pdf.set_font('Courier', 'B', 14)
    pdf.cell(130, 10, F"Unable to Process",0, 1)
    pdf.set_font('Courier', '', 11)

    print("\nUnable to process")
    if(len(errorReceipts) > 0):
        
        for e in errorReceipts:
            text = e
            pdf.cell(0, 7, text,0, 1, 'C')
            print(text)
    else: 
        text = "None"
        pdf.cell(0, 7, text,0, 1, 'C')
        print(text) 

    pdf.output(F'UQSail Receipts ({localDir}) - {datetime.date.today()}.pdf', 'F')
    #pdf.output(F"report-{now}.pdf", 'F')

def main():
    
    directory = "."
    numargs = len(sys.argv)

    watch = False
    if(numargs == 2):

        print(sys.argv[1])
        directory = sys.argv[1]

    elif(numargs == 3):
        if(sys.argv[2] == "-w"):
            #disable input, watch mode
            watch = True
    else:
        print(F"Usage: [TODO]")

    print("Files in " + directory + ":")


    files = os.listdir(directory)
    files.sort() 

    accounts = []
    receipts = []


    totalamount, returnedAccounts, errorReceipts = walktree(directory, visitfile, "Grand Total")
    
    print(F"Total Amount is {totalamount}")
    for a in returnedAccounts:
        print(a.printFormat())

    #walktreeiterative(directory)

    generatePDF(directory)
                

if __name__ == '__main__':
    main()
