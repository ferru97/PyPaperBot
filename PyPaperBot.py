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

        

def main(query, scholar_pages, dwn_dir, min_date=None, num_limit=None):
    
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
    url = "https://scholar.google.com/scholar?q="+query+"&as_vis=1&as_sdt=1,5";
    
    to_download = []

    for i in range(0,scholar_pages):
        if i>0:
            url = url + "&start=" + str(10*i)
        html = requests.get(url, headers=HEADERS)
        html = html.text
        
        papers = HTMLparsers.schoolarParser(html)
        print("Papers found from Scholar at page "+str(i+1)+" : "+str(len(papers)))
        
        print("Searching on Crossref...")
        papersInfo = getPapersInfo(papers, url)
        info_valids = 0
        for x in papersInfo:
            if x.crs_DOI!=None:
                info_valids += 1
        print("Papers info from Crossref: "+str(info_valids))
        
        to_download.append(papersInfo)
     
        print("Next page -> ",i+2)
        print("\n")
    
    

    to_download = [item for sublist in to_download for item in sublist] 
    
    if min_date!=None:
        to_download = filter_min_date(to_download,min_date)
        
    to_download.sort(key=lambda x: x.crs_year, reverse=True)
    
    SciHubDownload(to_download, dwn_dir, num_limit)
          
    Paper.generateReport(to_download,dwn_dir+"result.csv")
    Paper.generateBibtex(to_download,dwn_dir+"bibtex.bib")
    


    
def filter_min_date(list_papers,min_year):
    new_list = []
    
    for paper in list_papers:
        if paper.crs_year!=None and paper.crs_year>=min_year:
             new_list.append(paper)
            
    return new_list

        
    
def SciHubDownload(papers, dwnl_dir, num_limit):
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
    SciHub_URL = "https://sci-hub.tw/"
    
    num_downloaded = 0
    for p in papers: 
        if p.canBeDownloaded() and (num_limit==None or num_downloaded<num_limit):        
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
                            num_downloaded += 1
                    except:
                        pass
                            
                            
                    if p.downloaded==False and pdf_used==False and p.sc_link[-3:]=="pdf":
                        pdf_used = True
                        
                        r = requests.get(p.sc_link, headers=HEADERS)
                        with open(pdf_dir, 'wb') as f:
                                f.write(r.content)
                                p.downloaded = True  
                                num_downloaded += 1
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


def getPapersInfo(papers, scholar_search_link):
    papers_return = []
    for paper in papers:
        title = paper[0].lower()
        queries = {'query.bibliographic': title,'sort':'relevance',"select":"title,DOI,author"}

        found = False;
        found_timestamp = 0
        paper_found = Paper(title,paper[1],scholar_search_link)
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
    query = "machine learning gut microbioma"
    scholar_pages = 2 #each page has max 10 paper
    dwn_dir = "E:/Users/Vito/Desktop/testPaperbot/"
    
    #params query keyword - max scholar pages - download dir - min year - max papers to download
    main(query, scholar_pages, dwn_dir, 2017,3)
    
    
    
    