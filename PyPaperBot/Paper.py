# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 21:43:30 2020

@author: Vito
"""
import bibtexparser
import re

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
        return re.sub('[^\w\-_\. ]', '_', self.title)+".pdf"

    
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
        def strFix(s):
            if(len(str(s))==0):
                return "None"
            else:
                return str(s).replace(",", "").rstrip('\n')
            
    
        content = "Name,Scholar Link,DOI,Bibtex,PDF Name,Year,Scholar page,Journal,Downloaded,Downloaded from,Authors"
        for p in papers:
            pdf_name = p.getFileName() if p.downloaded==True else ""
            bibtex_found = True if p.bibtex!=None else False

            dwn_from = ""
            if p.downloadedFrom == 1:
                dwn_from = "SciHub"
            if p.downloadedFrom == 2:
                dwn_from = "Scholar"
                
            content += ("\n"+strFix(p.title)+","+strFix(p.scholar_link)+","+
                        strFix(p.DOI)+","+strFix(bibtex_found)+","+ strFix(pdf_name)+
                        ","+strFix(p.year)+","+strFix(p.scholar_page)+","+
                        strFix(p.jurnal)+","+strFix(p.downloaded)+","+strFix(dwn_from) +
                        ","+strFix(p.authors))
           
        f = open(path, "w", encoding='utf-8-sig')
        f.write(content)
        f.close()
                
        
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
        
          
        
        
            
