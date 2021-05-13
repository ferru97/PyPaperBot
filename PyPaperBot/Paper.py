# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 21:43:30 2020

@author: Vito
"""
import bibtexparser
import re
import csv
import os

class Paper:


    def __init__(self,title=None, scholar_link=None, scholar_page=None, cites=None, link_pdf=None, year=None, authors=None):        
        self.title = title
        self.scholar_page = scholar_page
        self.scholar_link = scholar_link
        self.pdf_link = link_pdf
        self.year = year
        self.authors = authors

        self.jurnal = None
        self.cites_num = None
        self.bibtex = None
        self.DOI = None

        self.downloaded = False
        self.downloadedFrom = 0 #1-SciHub 2-scholar



    def getFileName(self):
        try:
            return re.sub('[^\w\-_\. ]', '_', self.title)+".pdf"
        except:
            return "none.pdf"

    def setBibtex(self,bibtex):
        x=bibtexparser.loads(bibtex, parser=None)
        x=x.entries

        self.bibtex = bibtex

        try:
            if "year" in x[0]:
                self.year=x[0]["year"]
            if 'author' in x[0]:
                self.authors = x[0]["author"]
            self.jurnal=x[0]["journal"].replace("\\","") if "journal" in x[0] else None
            if self.jurnal==None:
                 self.jurnal=x[0]["publisher"].replace("\\","") if "publisher" in x[0] else None

        except:
            pass


    def canBeDownloaded(self):
        if self.DOI!=None or self.scholar_link!=None:
            return True
        return False


    def generateReport(papers, path):
        with open(path, mode="w", encoding='utf-8', newline='', buffering=1) as w_file:
            content = ["Name", "Scholar Link", "DOI", "Bibtex",
                       "PDF Name", "Year", "Scholar page", "Journal",
                       "Downloaded", "Downloaded from", "Authors"]
            file_writer = csv.DictWriter(w_file, delimiter = ",", lineterminator=os.linesep, fieldnames=content)
            file_writer.writeheader()

            for p in papers:
                pdf_name = p.getFileName() if p.downloaded==True else ""
                bibtex_found = True if p.bibtex!=None else False

                dwn_from = ""
                if p.downloadedFrom == 1:
                    dwn_from = "SciHub"
                if p.downloadedFrom == 2:
                    dwn_from = "Scholar"

                file_writer.writerow({
                        "Name" : p.title,
                        "Scholar Link" : p.scholar_link,
                        "DOI" : p.DOI,
                        "Bibtex" : bibtex_found,
                        "PDF Name" : pdf_name,
                        "Year" : p.year,
                        "Scholar page" : p.scholar_page,
                        "Journal" : p.jurnal,
                        "Downloaded" : p.downloaded,
                        "Downloaded from" : dwn_from,
                        "Authors" : p.authors})


    def generateBibtex(papers, path):
        content = ""
        for p in papers:
            if p.bibtex!=None:
                content += p.bibtex+"\n"


        relace_list = ["\ast","*","#"]
        for c in relace_list:
            content = content.replace(c,"")

        f = open(path, "w", encoding="latin-1", errors="ignore")
        f.write(str(content))
        f.close()
