from guizero import App, Box, Text, TextBox, Combo, ButtonGroup, PushButton, CheckBox, Picture, MenuBar
from tkinter.filedialog import askdirectory, askopenfilename
from tkinter import Tk
from PIL import ImageTk,Image  
import pathlib
import os
import webbrowser

class UI:

    def __init__(self, help_icon, image_logo, donate_img):
        self.help_icon = help_icon
        self.image_logo = image_logo
        self.donate_img = donate_img
        self.search_mode = "Search by DOI"

        self.app = App(title="PyPaperBot v0.9.6", height=450)
        MenuBar(self.app, toplevel=["About", "Donate :)"],
            options=[
                [["GitHub page", lambda : webbrowser.open('https://github.com/ferru97/PyPaperBot')]],
                [["Donate with PayPal", lambda : webbrowser.open('https://www.paypal.com/paypalme/ferru97')]]
            ])

        Box(self.app, width="fill", align="top", border=True)
        Picture(self.app, image=image_logo)

        bottom_box = Box(self.app, width="fill", align="bottom")
        PushButton(bottom_box, text="DOWNLOAD", command=lambda: self.start()).bg = "#ED4723"
        Text(bottom_box, text="Developed by ferru97", align="left", size=8)
        PushButton(bottom_box, image=donate_img, command=lambda: webbrowser.open('https://www.paypal.com/paypalme/ferru97'), align="right")

        
        options_box = Box(self.app, height="fill", align="right", border=True)
        Text(options_box, text="Search type")
        self.search_mode = ButtonGroup(options_box, options=["Search by DOI", "Search by DOI's file", "Search by keywords"], command=lambda: self.changeMode(), selected="Search by DOI")
        Text(options_box, text="\nDownload mode")
        self.dwn_type = ButtonGroup(options_box, options=["Papers & bibtex", "Only papers", "Only bibtex"], command=lambda: self.changeMode(), selected="Papers & bibtex", width="fill")

        content_box = Box(self.app, align="top", width="fill")

        form_box = Box(content_box, layout="grid", width="fill", align="left")
        self.search_text = Text(form_box, grid=[0,0], text="DOI", align="left", height=2)
        self.doi = TextBox(form_box, grid=[1,0], text="Insert DOI..", width="fill", align="left")
        self.keywords = TextBox(form_box, grid=[1,0], text="Insert keywords", width="fill", align="left")
        self.doi_file_btn = PushButton(form_box, grid=[1,0], text="Select Dois file", command=lambda: self.setFile(0), align="left", padx=5, pady=0)


        Text(form_box, grid=[0,1], text="Download directory", align="left", height=2)
        PushButton(form_box, grid=[1,1], text="Select dir", command=lambda: self.setDwnDir(), align="left", padx=5, pady=0)

        self.scholar_text = Text(form_box, grid=[0,2], text="       Scholar pages", align="left", height=2)
        self.scholar_pages = TextBox(form_box, grid=[1,2], text="2", width="fill", align="left")
        self.scholar_info = PushButton(form_box, grid=[0,2], image=help_icon, command=lambda :self.popUpInfo(1), align="left")

        self.min_year_text = Text(form_box, grid=[0,3], text="       Min year", align="left", height=2)
        self.min_year = TextBox(form_box, grid=[1,3], text="", width="fill", align="left")
        self.min_year_info = PushButton(form_box, grid=[0,3], image=help_icon, command=lambda :self.popUpInfo(2), align="left")

        self.jur_text = Text(form_box, grid=[0,4], text="       Journal filter", align="left", height=2)
        self.jur_btn1 = PushButton(form_box, grid=[1,4], text="Select csv", command=lambda: self.setFile(1), align="left", padx=5, pady=0)
        self.jur_btn2 = PushButton(form_box, grid=[0,4], image=help_icon, command=lambda :self.popUpInfo(3), align="left")

        self.maxDwn_text = Text(form_box, grid=[0,5], text="       Max downloads", align="left", height=2)
        self.maxDwn_info = PushButton(form_box, grid=[0,5], image=help_icon, command=lambda :self.popUpInfo(4), align="left")
        self.dwn_limit = TextBox(form_box, grid=[1,5], text="", width="fill", align="left", command=lambda: self.setDwnLimit())
        self.limit_type = ButtonGroup(form_box, options=["Limit by year", "Limit by citation"], selected="Limit by year", grid=[0,6])
        self.limit_type.hide()

        self.changeMode()

    
    def changeMode(self):
        self.keywords.hide()
        self.doi_file_btn.hide()
        self.doi.hide()
        self.limit_type.hide()
        self.dwn_limit.value = ""
        self.setScholarVisibility(False)
        self.setMinYearVisibility(False)
        self.setJournalVisibility(False)
        self.setMaxDwnVisibility(False)

        if self.search_mode.value == "Search by DOI":
            self.search_text.value = "DOI"
            self.doi.show()
        if self.search_mode.value == "Search by DOI's file":
            self.search_text.value = "DOIs file"
            self.doi_file_btn.show()
        if self.search_mode.value == "Search by keywords":
            self.search_text.value = "Keywords"
            self.keywords.show()
            self.setScholarVisibility(True)

        if self.dwn_type.value != "Only papers":
            self.setJournalVisibility(True)
            self.setMinYearVisibility(True)
        
        if self.search_mode.value == "Search by keywords":
            self.setMaxDwnVisibility(True)
    


    def setDwnDir(self):
        self.dwn_dir = askdirectory()


    def setFile(self,type):
        Tk().withdraw() 
        if(type == 1):
            self.csv = askopenfilename(title = "Select CSV",filetypes = (("CSV Files","*.csv"),))
        if(type == 0):
            self.doi_file = askopenfilename(title = "Select DOIs file",filetypes = (("DOIs txt","*.txt"),))


    def setDwnLimit(self):
        if len(self.dwn_limit.value.strip())>0 and self.dwn_type.value=="Papers & bibtex" and self.search_mode.value=="Search by keywords":
            self.limit_type.show()
        else:
            self.limit_type.hide()
    

    def start(self):
        print("start!")


    def setScholarVisibility(self,visibility):
        self.scholar_text.visible = self.scholar_pages.visible = self.scholar_info.visible = visibility
    
    def setMinYearVisibility(self,visibility):
        self.min_year_text.visible = self.min_year.visible = self.min_year_info.visible = visibility
    
    def setJournalVisibility(self,visibility):
        self.jur_text.visible = self.jur_btn1.visible = self.jur_btn2.visible = visibility
    
    def setMaxDwnVisibility(self,visibility):
        self.maxDwn_text.visible = self.maxDwn_info.visible = self.dwn_limit.visible = visibility


    def popUpInfo(self, info):
        if info == 1:
            msg = "Scholar pages: integer representing the number of Google Scholar pages to inspect. Each page has a maximum of 10 papers"
        if info == 2:
            msg = "Min year: integer representing the minimal publication year of the paper to download"
        if info == 3:
            msg = "Journal filter: path of a CSV file containing the list of accepted journals (More info on github)"
        if info == 4:
            msg = "Max downloads: integer representing the maximum number of papers to download sorted by:\n - Year of publication or \n- Citations number"
        self.app.info("info",msg)



curr_path = pathlib.Path(__file__).parent.absolute()
help_icon = os.path.join(curr_path, "img/info_icon.pgm")
image_logo = os.path.join(curr_path, "img/logo.png")
donate_img = os.path.join(curr_path, "img/donate.gif")

appUI = UI(help_icon, image_logo, donate_img)  
appUI.app.display()