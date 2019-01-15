from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from MusicData import *
import sys
import MusicData

def choose_directory():
   global dirname
   dirname = filedialog.askdirectory(parent=master,initialdir="/",title='Please select a directory')
   Label(master,text=dirname).grid(row = 1,column = 0)
master = Tk()
Label(master, text="      Please Select a Folder Containing MP3 Files    ").grid(row=0)

master.geometry("430x100")

current_Song = 0

Button(master, text='Start', command = lambda: Song_Metadata(dirname + "/", master)).grid(row=1, column=1, pady=4)
Button(master, text='Browse', command = choose_directory).grid(row=0, column=1, pady=4)

master.mainloop()