from tkinter import *
from tkinter import filedialog
from PIL import ImageTk,Image 

class Application:
    def __init__(self, master):
        self.master = master

        self.frame = Frame(height = 500, width = 500)
        self.frame.pack()

        master.title("A simple GUI")

        #self.label = Label(master, text="This is our first GUI!")
        #self.label.pack()

        self.addLogo()
        self.getDir = Button(master, text="Select Directory", command=self.openDir)

        self.getDir.pack()

        self.close_button = Button(master, text="Close", command=master.quit)
        self.close_button.pack()


    
    def addLogo(self):
        
        image = Image.open("uqsail.jpg")
        photo = ImageTk.PhotoImage(image)

        canvas.create_image(20,20, anchor=NW, image=photo)

        panel = Label(self.frame, image = photo)
        panel.pack(side = "bottom", fill = "both", expand = "yes")


    def openDir(self):
        filedir = filedialog.askdirectory()

    def greet(self):
        print("Greetings!")



if __name__ == '__main__':
    root = Tk()
    my_gui = Application(root)
    root.mainloop()