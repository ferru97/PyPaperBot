from guizero import App, Box, Text, TextBox, Combo, ButtonGroup, PushButton, CheckBox, Picture
from tkinter.filedialog import askdirectory, askopenfilename
from tkinter import Tk
from PIL import ImageTk,Image  
import pathlib
import os



#☼info_icon = PhotoImage(file="info_icon.pgm")
app = App(title="PyPaperBot", height=400,)
curr_path = pathlib.Path(__file__).parent.absolute()
help_icon = os.path.join(curr_path, "img\info_icon.pgm")
image_logo = os.path.join(curr_path, "img\logo.png")


def popUpInfo(info):
    global app
    if info == 1:
        msg = "Scholar pages: integer representing the number of Google Scholar pages to inspect. Each page has a maximum of 10 papers"
    if info == 2:
        msg = "Min year: integer representing the minimal publication year of the paper to download"
    if info == 3:
        msg = "Journal filter: path of a CSV file containing the list of accepted journals (More info on github)"
    if info == 4:
        msg = "Limit download number: integer representing the maximum number of papers to download sorted by:\n -Year of publication or \n-Citations number"
    app.info("info",msg)

def setDwnLimit():
    global dwn_limit
    global limit_type
    if len(dwn_limit.value.strip())>0:
        limit_type.show()
    else:
        limit_type.hide()

def setDwnDir():
    folder = askdirectory()
    print(folder)

def setCSVfilter():
    Tk().withdraw() 
    filename = askopenfilename(title = "Select CSV",filetypes = (("CSV Files","*.csv"),))
    print(filename)

def start():
    print("start!")


title_box = Box(app, width="fill", align="top", border=True)
Picture(app, image=image_logo)

buttons_box = Box(app, width="fill", align="bottom")
PushButton(buttons_box, text="DOWNLOAD", command=start).bg = "#ED4723"
Text(buttons_box, text="Developed by ferru97", align="left", size=8)


options_box = Box(app, height="fill", align="right", border=True)
Text(options_box, text="Options")
choice = ButtonGroup(options_box, options=["Search by DOI", "Search by DOI's file", "Search by keywords"], selected="Search by DOI")

content_box = Box(app, align="top", width="fill")

form_box = Box(content_box, layout="grid", width="fill", align="left", grid=[0,1])
Text(form_box, grid=[0,0], text="DOI", align="left", height=2)
TextBox(form_box, grid=[1,0], text="Insert DOI..", width="fill", align="left")

Text(form_box, grid=[0,1], text="Download directory", align="left", height=2)
PushButton(form_box, grid=[1,1], text="Select dir", command=setDwnDir, align="left", padx=5, pady=0)

Text(form_box, grid=[0,2], text="       Scholar pages", align="left", height=2)
TextBox(form_box, grid=[1,2], text="2", width="fill", align="left")
PushButton(form_box, grid=[0,2], image=help_icon, command=lambda :popUpInfo(1), align="left")

Text(form_box, grid=[0,3], text="       Min year", align="left", height=2)
TextBox(form_box, grid=[1,3], text="", width="fill", align="left")
PushButton(form_box, grid=[0,3], image=help_icon, command=lambda :popUpInfo(2), align="left")

Text(form_box, grid=[0,4], text="       Journal filter", align="left", height=2)
PushButton(form_box, grid=[1,4], text="Select csv", command=setCSVfilter, align="left", padx=5, pady=0)
PushButton(form_box, grid=[0,4], image=help_icon, command=lambda :popUpInfo(3), align="left")

Text(form_box, grid=[0,5], text="       Max downloads", align="left", height=2)
PushButton(form_box, grid=[0,5], image=help_icon, command=lambda :popUpInfo(4), align="left")
dwn_limit = TextBox(form_box, grid=[1,5], text="", width="fill", align="left", command=setDwnLimit)
limit_type = ButtonGroup(form_box, options=["Limit by year", "Limit by citation"], selected="Limit by year", grid=[0,6])
limit_type.hide()


app.display()