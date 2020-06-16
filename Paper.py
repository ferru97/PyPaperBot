# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 21:43:30 2020

@author: Vito
"""
import string


class Paper:
    
    def __init__(self,title, sc_link, sc_page, scholar_info):
        self.sc_title = title
        self.sc_link = sc_link
        self.sc_page = sc_page
        self.sc_authors = None
        self.sc_year = None
        self.sc_jurnal = None
        
        self.crs_title = None
        self.crs_DOI = None
        self.crs_authors = []
        self.crs_bibtex = None
        self.crs_year = None
        self.crs_jurnal = None
        
        self.downloaded = False
        self.downloadedFrom = 0 #1-SciHub 2-scholar
        self.crossref_found = False
        self.bibtex_found = False
        
        self.setScholarInfo(scholar_info)
        
        
    def setScholarInfo(self, s):
        m = s.find("-")     
            
        x = s[:m-1]
        x = x.replace(",", "")
        x = x.split()
        x = " ".join( [w for w in x if len(w) > 1 and w[1].islower()])
        if(x[-1:]=="…"):
            x = x[:-1] + " et al"
        self.sc_authors = x      
        
        n = s.rfind(" - ")
        year = s[(n-4):n].strip()
        self.sc_year = year
        
        
        jurnal = s[(m+2): (n-6)]
        
        if(jurnal[-1:]=="…"):
            jurnal = jurnal[:-1]
        self.sc_jurnal = jurnal
     

    def getJurnal(self):
        if self.crs_jurnal!=None:
            return self.crs_jurnal
        if self.sc_jurnal!=None:
            return self.sc_jurnal
        return None
        
    
    def setAuthors(self,authors):
        for a in authors:
            name = string.capwords(a["given"]) if "given" in a else  "None"
            surname = string.capwords(a["family"]) if "family" in a else  "None"
            self.crs_authors.append((name,surname))
            
    def getFileName(self, dwn_source):
        if dwn_source > 0:
            fname = ""
            
            if dwn_source == 1:
                for author in self.crs_authors:
                    fname += author[1]+" "
                    
                if self.crs_bibtex!=None:
                    fname += str(self.crs_year)
                    
            if dwn_source == 2 or fname=="":
                    fname += str(self.sc_authors)+" "+str(self.sc_year)                 
        
            return fname + ".pdf"

    
    def setBibtex(self,bibtex):
        if bibtex!=None and len(bibtex)>7 and bibtex[0]=="@" :      
            x_0 = bibtex.find("author = {")
            x_1 = bibtex.find("},", x_0)
            
            if(len(self.crs_authors)==0): 
                y = string.capwords(bibtex[(x_0 + 10):x_1])
                
                and_0 = y.find(" And ")
                
                if and_0 != -1:
                    z = y[:(and_0 + 1)] + "a" + y[and_0 + 2:]
                else:
                    z = y
                
    
                self.crs_bibtex = bibtex[:(x_0 + 10)] + z + bibtex[(x_1):] 
               
            else:
                authors_str = ""
                i = 0
                for (name,surname) in self.crs_authors:
                    authors_str += name +" "+ surname+" "
                    if i<len(self.crs_authors)-1:
                       authors_str += "and " 
                    i += 1
                    
                self.crs_bibtex = bibtex[:(x_0 + 10)] + authors_str + bibtex[(x_1):]
                
             
            char = self.crs_bibtex.find("year = ")
            self.crs_year  = int(self.crs_bibtex[char+7:char+11])    
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
        self.crs_year = None
        self.crs_jurnal = None
        
        self.downloaded = False
        self.crossref_found = False
        self.bibtex_found = False
    
    def generateReport(papers, path):
    
        content = "SC Name;CRS Name;SC Link;CRS DOI;Bibtex;PDF Name;Year;Scholar page;Jurnal;Downloaded;Downloaded from"
        for p in papers:
            pdf_name = p.getFileName(p.downloadedFrom) if p.downloaded==True else ""
            
            jurnal = str(p.sc_jurnal)
            dwn_from = ""
            if p.downloadedFrom == 1:
                jurnal = str(p.crs_jurnal)
                dwn_from = "SciHub"
            if p.downloadedFrom == 2:
                dwn_from = "Scholar"
                
            content += ("\n"+str(p.sc_title)+";"+str(p.crs_title)+
            ";"+str(p.sc_link)+";"+str(p.crs_DOI)+";"+str(p.bibtex_found)+";"+
            pdf_name+";"+str(p.crs_year)+";"+str(p.sc_page)+";"+jurnal+";"+str(p.downloaded)+";"+dwn_from)
           
        f = open(path, "w", encoding='utf-8-sig')
        f.write(content)
        f.close()
        
        
    def generateBibtex(papers, path):
        content = ""
        for p in papers:
            if p.crs_bibtex!=None:
                note =  ",\n\tnote = {\doi{" + str(p.crs_DOI) + "}}\n}\n\n"
                bibtex = p.crs_bibtex[:(len(p.crs_bibtex)-2)] + note
                content += bibtex
           
        f = open(path, "w")
        f.write(content.encode("iso-8859-1"))
        f.close()

            