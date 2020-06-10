# -*- coding: utf-8 -*-
"""
Spyder Editor
This is a temporary script file.
"""

from urllib.request import Request, urlopen, quote
import urllib
from html.parser import HTMLParser
import requests
import time
import random
import json
import codecs
from unicodedata import normalize
from crossref_commons.iteration import iterate_publications_as_json
from difflib import SequenceMatcher
from scidownl.scihub import *
import HTMLparsers
from Paper import Paper

        

def main(query, number, dwn_dir):
    
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
    url = "https://scholar.google.com/scholar?q="+query+"&as_vis=1&as_sdt=1,5";
    
    papers_result = []    

    for i in range(0,int(number/10)):
        if i>0:
            url = url + "&start=" + str(10*i)
        html = requests.get(url, headers=HEADERS)
        html = html.text
        
        papers = HTMLparsers.schoolarParser(html)
        print("Papers found from Scholar at page "+str(i+1)+" : "+str(len(papers)))
        
        print("Searching on Crossref...")
        papersInfo = getPapersInfo(papers)
        info_valids = 0
        for x in papersInfo:
            if x.crs_DOI!=None:
                info_valids += 1
        print("Papers info from Crossref: "+str(info_valids))
     
        papers_result.append(papersInfo)
        SciHubDownload(papersInfo, dwn_dir)
        
        print("Next page-> ",i+1)
        
    Paper.generateReport(papers_result,dwn_dir+"result.csv")
    Paper.generateBibtex(papers_result,dwn_dir+"bibtex.bib")
        
        
def SciHubDownload(papers, dwnl_dir):
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
    SciHub_URL = "https://sci-hub.tw/"
    
    for p in papers:      
        if p.canBeDownloaded():        
            pdf_dir = dwnl_dir + p.getFileName()
            print("Downloading -> "+str(p.sc_title))
            
                        
            use_sc_link = False
            doi_used = False
            pdf_used = False
            errors = 0
            while p.downloaded==False and use_sc_link==False and errors!=2:        
                try:   
                    
                    if doi_used==False and p.crs_DOI!=None:
                        url = SciHub_URL + p.crs_DOI
                    else:
                        url = SciHub_URL + p.sc_link
                        use_sc_link = True
                        
                    doi_used = True
                
                    try:   
                        r = requests.get(url, headers=HEADERS)
                        pdf_link = HTMLparsers.getSchiHubPDF(r.text)
                        
                        time.sleep(random.randint(1,5))
                        
                        if(pdf_link != None):
                            r2 = requests.get(pdf_link, headers=HEADERS)
                            with open(pdf_dir, 'wb') as f:
                                f.write(r2.content)
                            p.downloaded = True
                    except:
                        pass
                            
                            
                    if p.downloaded==False and pdf_used==False and p.sc_link[-3:]=="pdf":
                        pdf_used = True
                        
                        r = requests.get(p.sc_link, headers=HEADERS)
                        with open(pdf_dir, 'wb') as f:
                                f.write(r.content)
                                p.downloaded = True        
                except:
                    errors +=1
                    
        
    
def similarStrings(a, b):
    return SequenceMatcher(None, a, b).ratio()


def getTimestamp(paper):
    timestamp = 0
    if "deposited" in paper:
        if "timestamp" in paper["deposited"]:
            timestamp = int(paper["deposited"]["timestamp"])
    return timestamp


def getPapersInfo(papers):
    papers_return = []
    for paper in papers:
        title = paper[0].lower()
        queries = {'query.bibliographic': title,'sort':'relevance',"select":"title,DOI,author"}

        found = False;
        found_timestamp = 0
        paper_found = Paper(title,paper[1])
        for el in iterate_publications_as_json(max_results=30, queries=queries):
           
            el_date = getTimestamp(el);
            
            if (found==False or el_date>found_timestamp) and ("title" in el) and similarStrings(title ,el["title"][0].strip().lower())>0.75:
                found_timestamp = el_date
                paper_found.reset()
                
                if "title" in el:
                    paper_found.crs_title = el["title"][0].strip().lower()
                if "DOI" in el:
                    paper_found.crs_DOI = el["DOI"].strip().lower()
                if "author" in el:
                    paper_found.setAuthors(el["author"])
               
                try: 
                    url_bibtex = "http://api.crossref.org/works/" + paper_found.crs_DOI + "/transform/application/x-bibtex"
                    x = requests.get(url_bibtex)
                    paper_found.setBibtex(str(x.text))
                except:
                    pass
 
                found = True
                paper_found.crossref_found = True 
        
            
        papers_return.append(paper_found)
                
        time.sleep(random.randint(1,5))
        
    return papers_return

    
if __name__ == "__main__":
    query = "OPEC agreements in 2019 and 2020"
    paper_num = 20
    dwn_dir = "E:/Users/Vito/Desktop/testPaperbot/"
    main(query, paper_num, dwn_dir)
    
    
    
    