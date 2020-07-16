# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 21:43:30 2020

@author: Vito
"""
import string
import bibtexparser
import unidecode


class Paper:
    
    def __init__(self,title, sc_link, sc_page, cites, link_pdf):
        self.sc_title = title
        self.sc_page = sc_page
        self.sc_link = sc_link 
        self.sc_pdf_link = link_pdf
        self.sc_authors = []
        self.sc_year = None
        self.sc_jurnal = None
        self.sc_cites = cites
        self.sc_bibtex = None
        self.pdf_name = None
        self.sc_DOI = None
             
        self.downloaded = False
        self.downloadedFrom = 0 #1-SciHub 2-scholar
        self.bibtex_found = False
                

    def getJurnal(self):
        return self.sc_jurnal
        
    

    def getFileName(self):
        return self.pdf_name
    

    def setAuthors(self,authors):
        self.sc_authors = []
        for a in authors:
            name = string.capwords(a["given"]) if "given" in a else  "None"
            surname = string.capwords(a["family"]) if "family" in a else  "None"
            self.sc_authors.append((name,surname))

    
    def setBibtex(self,bibtex):
        try:
            x=bibtexparser.loads(bibtex, parser=None)
            x=x.entries
            
           
            x[0]["author"] = x[0]["author"].replace("\\","").replace("{","").replace("}","")
            x[0]["author"] = string.capwords(x[0]["author"]).replace("And", "and")
            self.sc_year=x[0]["year"] if "year" in x[0] else None
            self.sc_jurnal=x[0]["journal"].replace("\\","") if "journal" in x[0] else None
            if self.sc_jurnal==None:
                 self.sc_jurnal=x[0]["publisher"].replace("\\","") if "publisher" in x[0] else None
            
            #take journal initials
            j_init=""
            if self.sc_jurnal != None:
                ch_j=["and","&","of",",",'{','}']
                jurnal_temp = self.sc_jurnal
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
                
            
            self.pdf_name =  authors_surnames + str(self.sc_year) + "_" + j_init+".pdf"
            
            (x[0])["ID"] = self.pdf_name[:-4].replace(" ","-")
            self.sc_bibtex = x[0]
            
            self.bibtex_found = True
            
        except Exception as e:
                print(e)
                    
            
    def canBeDownloaded(self):
        if self.sc_DOI!=None or self.sc_link!=None:
            return True
        else:
            return False
            
    
    def generateReport(papers, path):
        def strFix(s):
            if(len(str(s))==0):
                return "None"
            else:
                return str(s).replace(",", "").rstrip('\n')
            
    
        content = "SC Name,SC Link,CRS DOI,Bibtex,PDF Name,Year,Scholar page,Journal,Downloaded,Downloaded from"
        for p in papers:
            pdf_name = p.getFileName() if p.downloaded==True else ""

            dwn_from = ""
            if p.downloadedFrom == 1:
                dwn_from = "SciHub"
            if p.downloadedFrom == 2:
                dwn_from = "Scholar"
                
            content += ("\n"+strFix(p.sc_title)+","+strFix(p.sc_link)+","+
                        strFix(p.sc_DOI)+","+strFix(p.bibtex_found)+","+ strFix(pdf_name)+
                        ","+strFix(p.sc_year)+","+strFix(p.sc_page)+","+
                        strFix(p.sc_jurnal)+","+strFix(p.downloaded)+","+strFix(dwn_from))
           
        f = open(path, "w", encoding='utf-8-sig')
        f.write(content)
        f.close()
        
        
    def generateBibtex(papers, path):
        content = ""
            
        for p in papers:
            if p.sc_bibtex!=None:
                
                authors_bbx = ""
                first = True
                for a in p.sc_authors:
                    if first==False:
                        authors_bbx += " and "
                    else:
                        first=False
                        
                    authors_bbx += a[0]+", "+a[1]
                
                content += "\n\n@"+p.sc_bibtex["ENTRYTYPE"]+"{"+p.sc_bibtex["ID"]
                for key in p.sc_bibtex.keys():
                    if key!="ENTRYTYPE" and key!="ID":
                        try:
                          val = p.sc_bibtex[key].encode('Windows-1252').decode('latin-1').replace("{","").replace("}","")
                        except:
                          print("Encoding error")
                          val = p.sc_bibtex[key].replace("{","").replace("}","")
                         
                        if key=="author":
                            val = authors_bbx
                        
                        content += ",\n\t"+key+" = "+"{"+val+"}"
                content += "\n}"
                
        
        relace_list = ["\ast","*","#"]
        for c in relace_list:
            content = content.replace("'","").replace("\ast","")
        
        f = open(path, "w")
        f.write(str(content))
        f.close()

          
        
        
            