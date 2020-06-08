# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 21:43:30 2020

@author: Vito
"""


class Paper:
    
    def __init__(self,title):
        self.crs_title = title
        
        self.crs_title = None
        self.crs_DOI = None
        self.crs_authors = []
        self.crs_bibtex = None
        
        self.sc_title = None
        self.sc_link = None
        
        self.downloaded = False
        self.crossref_found = False
        
        
    
    def setAuthors(self,authors):
        for a in authors:
            self.crs_authors.append((a["given"],a["family"]))
            
    def getFileName(self):
        fname = ""
        for author in self.crs_authors:
            fname += author[1]+" "
            
        if self.crs_bibtex!=None:
            char = self.crs_bibtex.find("year = ")
            year = self.crs_bibtex[char+7:char+11]
            fname += year
        
        return fname + ".pdf"