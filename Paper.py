# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 21:43:30 2020

@author: Vito
"""
import string



class Paper:
    
    def __init__(self,title, sc_link):
        self.sc_title = title
        self.sc_link = sc_link
        
        self.crs_title = None
        self.crs_DOI = None
        self.crs_authors = []
        self.crs_bibtex = None
        
        self.downloaded = False
        self.crossref_found = False
        self.bibtex_found = False
        
        
    
    def setAuthors(self,authors):
        for a in authors:
            name = string.capwords(a["given"]) if "given" in a else  "None"
            surname = string.capwords(a["family"]) if "family" in a else  "None"
            self.crs_authors.append((name,surname))
            
    def getFileName(self):
        fname = ""
        for author in self.crs_authors:
            fname += author[1]+" "
            
        if self.crs_bibtex!=None:
            char = self.crs_bibtex.find("year = ")
            year = self.crs_bibtex[char+7:char+11]
            fname += year
        
        return fname + ".pdf"
    
    def setBibtex(self,bibtex):
        if bibtex!=None and len(bibtex)>7 and bibtex[:8]=="@article" :      
            x_0 = bibtex.find("author = {")
            x_1 = bibtex.find("},", x_0)
            
            y = string.capwords(bibtex[(x_0 + 10):x_1])
            
            and_0 = y.find(" And ")
            
            if and_0 != -1:
                z = y[:(and_0 + 1)] + "a" + y[and_0 + 2:]
            else:
                z = y
            
            self.crs_bibtex = bibtex[:(x_0 + 10)] + z + bibtex[(x_1):] 
            self.bibtex_found = True
            
            
    def canBeDownloaded(self):
        if self.crs_DOI!=None or self.sc_link!=None:
            return True
        else:
            return False
            
    def reset(self):
        self.crs_title = None
        self.crs_DOI = None
        self.crs_authors = []
        self.crs_bibtex = None
        
        self.downloaded = False
        self.crossref_found = False
        self.bibtex_found = False
    
    def generateReport(papers, path):
        content = "SC Name;CRS Name;Downloaded;SC Link;CRS DOI;Bibtex;PDF Name"
        for list_p in papers:
            for p in list_p:  
                pdf_name = p.getFileName() if p.downloaded==True else ""
                content += ("\n"+str(p.sc_title)+";"+str(p.crs_title)+";"+str(p.downloaded)+
                ";"+str(p.sc_link)+";"+str(p.crs_DOI)+";"+str(p.bibtex_found))+";"+pdf_name
           
        f = open(path, "w")
        f.write(content)
        f.close()
        
        
    def generateBibtex(papers, path):
        content = ""
        for list_p in papers:
            for p in list_p:  
                if p.crossref_found:
                    note =  ",\n\tnote = {\doi{" + str(p.crs_DOI) + "}}\n}\n\n"
                    bibtex = p.crs_bibtex[:(len(p.crs_bibtex)-2)] + note
                    content += bibtex
           
        f = open(path, "w")
        f.write(content)
        f.close()
        
            