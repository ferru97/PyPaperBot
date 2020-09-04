# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 21:43:30 2020

@author: Vito
"""
import bibtexparser
import re
import string

class Paper:
    
    
    def __init__(self,title=None, scholar_link=None, scholar_page=None, cites=None, link_pdf=None):        
        self.title = title
        self.scholar_page = scholar_page
        self.scholar_link = scholar_link 
        self.pdf_link = link_pdf
        
        self.year = None
        self.jurnal = None
        self.cites_num = None
        self.bibtex = None
        self.DOI = None

        self.sc_authors = None
        self.pdf_name = None
             
        self.downloaded = False
        self.downloadedFrom = 0 #1-SciHub 2-scholar

    

    def getFileName(self):
        if self.pdf_name!=None:
            return self.pdf_name+".pdf"
        else:
            return str(self.title)+".pdf"


    def setAuthors(self,authors):
        self.sc_authors = []
        for a in authors:
            name = string.capwords(a["given"]) if "given" in a else  "None"
            surname = string.capwords(a["family"]) if "family" in a else  "None"
            self.sc_authors.append((name,surname))

    
    def setBibtex(self,bibtex):
        x=bibtexparser.loads(bibtex, parser=None)
        x=x.entries
        self.bibtex = x[0]
        try: 
            x[0]["author"] = x[0]["author"].replace("\\","").replace("{","").replace("}","")
            x[0]["author"] = string.capwords(x[0]["author"]).replace("And", "and")
            self.year=x[0]["year"] if "year" in x[0] else None
            self.jurnal=x[0]["journal"].replace("\\","") if "journal" in x[0] else None
            if self.jurnal==None:
                 self.jurnal=x[0]["publisher"].replace("\\","") if "publisher" in x[0] else None
            
            #take journal initials
            j_init=""
            if self.jurnal != None:
                ch_j=["and","&","of",",",'{','}']
                jurnal_temp = self.jurnal
                for c in ch_j:
                    jurnal_temp = jurnal_temp.replace(c,"")
                jurnal_temp = jurnal_temp.split()
                
                for i in range(0,len(jurnal_temp)):
                    j_init = j_init + jurnal_temp[i][0].upper() #iniziali journal
    
            
            authors_surnames = ""
            if len(self.sc_authors)>0:
                #characters to remove from author
                for author in self.sc_authors:
                    authors_surnames += author[1]+"_";
                
            
            self.pdf_name =  authors_surnames + str(self.year) + "_" + j_init+".pdf"
            
            (x[0])["ID"] = self.pdf_name[:-4].replace(" ","-")
        except Exception:
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
            
    
        content = "Name,Scholar Link,DOI,Bibtex,PDF Name,Year,Scholar page,Journal,Downloaded,Downloaded from"
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
                        strFix(p.jurnal)+","+strFix(p.downloaded)+","+strFix(dwn_from))
           
        f = open(path, "w", encoding='utf-8-sig')
        f.write(content)
        f.close()
                
        
    def generateBibtex(papers, path):
        content = ""
            
        for p in papers:
            if p.bibtex!=None:
                
                authors_bbx = ""
                if p.sc_authors!=None:
                    first = True
                    for a in p.sc_authors:
                        if first==False:
                            authors_bbx += " and "
                        else:
                            first=False      
                        authors_bbx += a[1]+", "+a[0]
                
                content += "\n\n@"+p.bibtex["ENTRYTYPE"]+"{"+p.bibtex["ID"]
                for key in p.bibtex.keys():
                    if key!="ENTRYTYPE" and key!="ID":
                        try:
                          val = p.bibtex[key].encode('Windows-1252').decode('latin-1').replace("{","").replace("}","")
                        except:
                          print("Encoding error")
                          val = p.bibtex[key].replace("{","").replace("}","")
                         
                        if key=="author":
                            val = authors_bbx
                        
                        content += ",\n\t"+key+" = "+"{"+val+"}"
                content += "\n}"
                
        
        relace_list = ["\ast","*","#"]
        for c in relace_list:
            content = content.replace(c,"")
        
        f = open(path, "w", encoding="latin-1", errors="ignore")
        f.write(str(content))
        f.close()
        
        return f
        
          
        
        
            