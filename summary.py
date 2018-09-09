import sys
import os
import datetime
from stat import *

from fpdf import FPDF


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

        def setValuesFromName(self):
                values = self.name.split('-')
                if(len(values) != 5):
                        self.name = "ERROR"
                
                else:
                        self.paidBy = values[0]
                        self.date = values[1]
                        self.description = values[2]
                        self.amount = float(values[3].strip()[1:])
                        self.paidDate = values[4]

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
        return self.name < other.name



def visitfile(top, filename):
    # print(filename)
    pass

def walktree(top, callback, account):

        subAccounts = []
        x = Account(account)

        subAccounts.append(x)

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

                        totalAccount, returnedAccounts = walktree(pathname, callback, nextAccount)
           
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
                        # Unknown file type, print a message    
                        print(F"Skipping {pathname}")


        subAccounts.sort()
        #x.printAccount()
        return x.getSum(), subAccounts


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


def generatePDF(accounts):
    print("Generating PDF...")
    pdf = FPDF(orientation = 'P', unit = 'mm', format='A4')
    pdf.add_page()
    pdf.set_font('Courier', 'B', 16)
    pdf.ln(15)
    now = datetime.date.today()
    pdf.cell(130, 10, F"UQ Sailing Club Accounts    {now}",1, 1, 'C')
    pdf.ln(25)

    pdf.set_font('Courier', 'B', 14)
    pdf.cell(130, 10, F"Receipts",0, 1)
    pdf.set_font('Courier', '', 11)
    
    pdf.image("uqsail.png", 150, 10, 40, 40, "", "")
    for a in accounts:
        #text = a.printFormat()
        pdf.cell(0,7, F"{a.level * 3 * ' '}{a.accountName}".ljust(50) + "$" + F"{float(a.getSum()):.2f}".rjust(12), 0,1, 'C')

    pdf.output('report.pdf', 'F')

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


    totalamount, returnedAccounts = walktree(directory, visitfile, "Grand Total")
    
    print(F"Total Amount is {totalamount}")
    for a in returnedAccounts:
        print(a.printFormat())

    #walktreeiterative(directory)

    generatePDF(returnedAccounts)
                

if __name__ == '__main__':
    main()
