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
import re
from Paper import Paper


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = str(re.sub('[^\w\s-]', '', value).strip().lower())
    value = str(re.sub('[-\s]+', '-', value))
    # ...
    return value
        

def main(query, number, dwn_dir, proxies):
    
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
    url = "https://scholar.google.com/scholar?q="+query+"&as_vis=1&as_sdt=1,5";
    

    for i in range(0,int(number/10)):
        if i>0:
            url = url + "&start=" + str(10*i)
        html = requests.get(url, headers=HEADERS)
        html = html.text
        
        papers = HTMLparsers.schoolarParser(html)
        print("Papers found from Scholar: "+str(len(papers)))
        
        papersInfo = getPapersInfo(papers)
        info_valids = 0
        for x in papersInfo:
            if x.crs_DOI!=None:
                info_valids += 1
        print("Papers info from Crossref: "+str(info_valids))
     
        SciHubDownload(papersInfo, dwn_dir, proxies)
        
        print("Next -> ",i+1)
        
        
def SciHubDownload(papers, dwnl_dir, proxies):
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}

    SciHub_URLs = ["https://sci-hub.tw/"]
    
    for p in papers:
        pdf_dir = dwnl_dir + p.getFileName()
        print("Downloading -> "+str(p.getFileName()))
        
                    
        i = 0;
        use_sc_link = False
        while p.downloaded==False and i<len(SciHub_URLs):        
            
            try:   
                if use_sc_link==False and p.crs_DOI!=None:
                    url = SciHub_URLs[i]+p.crs_DOI
                else:
                    url = SciHub_URLs[i]+p.sc_link
                
                
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
                
            i = i + 1
            if p.downloaded==False and i==len(SciHub_URLs) and use_sc_link==False and p.crs_DOI!=None:
                i = 0
                use_sc_link = True
                    
        
    
def similarStrings(a, b):
    return SequenceMatcher(None, a, b).ratio()


def getPapersInfo(papers):
    papers_return = []
    for paper in papers:
        title = paper[0].lower()
        queries = {'query.bibliographic': title,'sort':'relevance',"select":"title,DOI,author"}

        found = False;
        paper_found = Paper(title)
        paper_found.sc_link = paper[1]
        for el in iterate_publications_as_json(max_results=30, queries=queries):
            
            if found==False and ("title" in el) and similarStrings(title ,el["title"][0].strip().lower())>0.75:
                if "title" in el:
                    paper_found.sc_title = el["title"][0].strip().lower()
                if "DOI" in el:
                    paper_found.crs_DOI = el["DOI"].strip().lower()
                if "author" in el:
                    paper_found.setAuthors(el["author"])
               
                try: 
                    url_bibtex = "http://api.crossref.org/works/" + paper_found.crs_DOI + "/transform/application/x-bibtex"
                    x = requests.get(url_bibtex)
                    paper_found.crs_bibtex = x.text
                except:
                    pass
 
                found = True
                paper_found.crossref_found = True
                papers_return.append(paper_found)
        
            
        if found == False:
            print("NOT FOUND -> "+title)
                
        time.sleep(random.randint(1,5))
        
    return papers_return

    
if __name__ == "__main__":
    query = "text analysis for accounting"
    paper_num = 100
    dwn_dir = "E:/Users/Vito/Desktop/testPaperbot/"
    proxies = ["https://107.191.41.188:8080","https://142.93.117.211:3128","https://209.141.49.11:8080"]
    main(query, paper_num, dwn_dir, proxies)