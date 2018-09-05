import sys
import os
from stat import *

printReceipts = False

class Receipt:
        def __init__(self, name, account):

                self.name = name
                self.paidBy = "none"
                self.amount = 0
                self.paidDate = "none"
                self.description = "none"
                self.date = "none"
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


class Account:
    def __init__(self, name):
        self.receipts = []
        self.name = name

        self.hasSubAccount = False

        return

    def getSum(self):
        return sum(r.amount for r in self.receipts)

    def getName(self): return self.name

    def setHasSubAccount(self, hasSubAccount):
        self.hasSubAccount = hasSubAccount

    def addReceipt(self, receipt):
        self.receipts.append(receipt)

    def printAccount(self):
        if(self.hasSubAccount):
            print "         ", '{:<30s}'.format(self.name), "Total:", "$" + '{:>12.2f}'.format(float(self.getSum()))
        else:
            print "Account: ", '{:<30s}'.format(self.name), "Total:", "$" + '{:>12.2f}'.format(float(self.getSum()))
        if(printReceipts):
            for r in self.receipts:
                if(r.getName() != "ERROR"):
                    print r.getName(),":",str(r.getAmount())



def visitfile(top, filename):
    print filename

def walktree(top, callback, account):
        x = Account(account)

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

                        totalAccount = walktree(pathname, callback, nextAccount)
           
                        newReceipt = Receipt(f, x)
                        newReceipt.amount = totalAccount
                        x.addReceipt(newReceipt)

                elif S_ISREG(mode):
                        # It's a file, call the callback function
                        # callback(top, f)
                        newReceipt = Receipt(f, x)
                        newReceipt.setValuesFromName()
                        x.addReceipt(newReceipt)
                else:
                        # Unknown file type, print a message    
                        print 'Skipping %s' % pathname


        
        x.printAccount()
        return x.getSum()


def recurse():
    return [something_else] + recurse()


def main():
    
    directory = "."
    numargs = len(sys.argv)
    if(numargs == 2):

        print(sys.argv[1])
        directory = sys.argv[1]

    print("Files in " + directory + ":")


    files = os.listdir(directory)
    files.sort() 

    accounts = []
    receipts = []


    walktree(directory, visitfile, "Grand Total")


if __name__ == '__main__':
    main()
