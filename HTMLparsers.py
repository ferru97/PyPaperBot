# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 11:59:42 2020

@author: Vito
"""
from bs4 import BeautifulSoup
gErrors = ["This page appears when Google automatically detects requests coming from your computer network which appear to be in violation of the","Attiva JavaScript"]


def schoolarParser(html):
    result = []
    soup = BeautifulSoup(html, "html.parser")
    for element in soup.findAll("div", class_="gs_r gs_or gs_scl"):
        if isBook(element) == False:           
            for h3 in element.findAll("h3", class_="gs_rt"):
                found = False
                for a in h3.findAll("a"): 
                    if found == False:
                        result.append((a.text, a.get("href")))
                        found = True
    return result            
        


def isBook(tag):
    result = False
    for span in tag.findAll("span", class_="gs_ct2"):
        if span.text=="[B]":
            result = True
    return result



def getSchiHubPDF(html):
    result = None
    soup = BeautifulSoup(html, "html.parser")
    
    iframe = soup.find(id='pdf')
    plugin = soup.find(id='plugin')
    
    if iframe!=None:
        result = iframe.get("src")
        
    if plugin!=None and result==None:
        result = plugin.get("src")
        
    if result!=None and result[0]!="h":
        result = "https:"+result
    
    return result
