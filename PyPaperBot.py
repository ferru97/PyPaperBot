# -*- coding: utf-8 -*-
"""
Spyder Editor
This is a temporary script file.
"""
import requests
import time
import random
from crossref_commons.iteration import iterate_publications_as_json
from difflib import SequenceMatcher
import HTMLparsers
from Paper import Paper
from os import path
import pandas as pd
import sys
import argparse



def main(query, scholar_pages, dwn_dir, min_date=None, num_limit=None, filter_jurnal_file=None):
    
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
    url = "https://scholar.google.com/scholar?q="+query+"&as_vis=1&as_sdt=1,5";
    
    to_download = []

    for i in range(0,scholar_pages):
        if i>0:
            url = url + "&start=" + str(10*i)
        html = requests.get(url, headers=HEADERS)
        html = html.text
        
        papers = HTMLparsers.schoolarParser(html)
        print("Google Scholar page "+str(i+1)+" : "+str(len(papers))+" papers found")
        
        print("Searching on Crossref...")
        papersInfo = getPapersInfo(papers, url)
        info_valids = 0
        for x in papersInfo:
            if x.crs_DOI!=None:
                info_valids += 1
        print("Papers info from Crossref: "+str(info_valids))
        
        to_download.append(papersInfo)
     
        print("\n")
    
    

    to_download = [item for sublist in to_download for item in sublist] 
    
    if filter_jurnal_file!=None:
       to_download = filterJurnals(to_download,filter_jurnal_file)
    
    if min_date!=None:
        to_download = filter_min_date(to_download,min_date)
        
    to_download.sort(key=lambda x: x.crs_year if x.crs_year!=None else int(x.sc_year) , reverse=True)
    
    SciHubDownload(to_download, dwn_dir, num_limit)
          
    Paper.generateReport(to_download,dwn_dir+"result.csv")
    Paper.generateBibtex(to_download,dwn_dir+"bibtex.bib")
    

def filterJurnals(papers,csv_path):
    result = []
    df = pd.read_csv(csv_path, sep=";")
    journal_list = list(df["journal_list"])
    include_list = list(df["include_list"])
    
    for p in papers:
        good = False if (p.getJurnal()!=None and len(p.getJurnal())>0) else True
        if p.getJurnal()!=None:   
            for jurnal,include in zip(journal_list,include_list):
                if include==1 and similarStrings(p.getJurnal(),jurnal)>=0.8: 
                    good = True
            
        if good == True:
            result.append(p)
    
    return result

    
def filter_min_date(list_papers,min_year):
    new_list = []
    
    for paper in list_papers:
        if paper.crs_year!=None and paper.crs_year>=min_year:
             new_list.append(paper)
            
    return new_list


def saveFile(file_name,content, paper, dwn_source):    
    if path.exists(file_name):
       file_name_temp = file_name
       n = 2
       while path.exists(file_name_temp):
           file_name_temp = "("+str(n)+")"+file_name 
           n += 1
       file_name = file_name_temp
       
    
    with open(file_name, 'wb') as f:
        f.write(content)
        paper.downloaded = True
        paper.downloadedFrom = dwn_source
        
    
def SciHubDownload(papers, dwnl_dir, num_limit):
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
    SciHub_URL = "https://sci-hub.tw/"
    
    num_downloaded = 0
    paper_number = 1
    for p in papers: 
        if p.canBeDownloaded() and (num_limit==None or num_downloaded<num_limit):        
            print("Download "+str(paper_number)+" of "+str(len(papers))+" -> "+str(p.sc_title))
            paper_number += 1
                        
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
                        pdf_dir = dwnl_dir + p.getFileName(1)
                        r = requests.get(url, headers=HEADERS)
                        content_type = r.headers.get('content-type')
                        if 'application/pdf' in content_type:
                            saveFile(pdf_dir,r.content,p,1)
                            num_downloaded += 1
                        else:                          
                            pdf_link = HTMLparsers.getSchiHubPDF(r.text)
                            
                            time.sleep(random.randint(1,5))
                            
                            if(pdf_link != None):
                                r2 = requests.get(pdf_link, headers=HEADERS)
                                saveFile(pdf_dir,r2.content,p,1)
                                num_downloaded += 1
                    except:
                        pass
                            
                            
                    if p.downloaded==False and pdf_used==False and p.sc_link[-3:]=="pdf":
                        pdf_used = True
                        pdf_dir = dwnl_dir + p.getFileName(2)
                        r = requests.get(p.sc_link, headers=HEADERS)
                        saveFile(pdf_dir,r.content,p,2)
                        num_downloaded += 1
                except Exception as e:
                    print(e)
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
        queries = {'query.bibliographic': title,'sort':'relevance',"select":"title,DOI,author,short-container-title"}

        found = False;
        found_timestamp = 0
        paper_found = Paper(title,paper[1],scholar_search_link,paper[2])
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
                if "short-container-title" in el:
                    paper_found.crs_jurnal = str(el["short-container-title"][0])
                                   
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
    
    parser = argparse.ArgumentParser(description='PyPaperBot is python tool to search and dwonload scientific papers from Scholar, Crossref and SciHub')
    parser.add_argument('--query', type=str, help='Query to make on Google Scholar')
    parser.add_argument('--scholar-pages', required=True, type=int, help='Number of Google Scholar pages to inspect. Each page has a maximum of 10 papers')
    parser.add_argument('--dwn-dir', default="/", type=str, help='Directory path in which to save the result (Default=current)')
    parser.add_argument('--min-year', default=None, type=str, help='Minimal publication year of the paper to download')
    parser.add_argument('--max-dwn', default=None, type=str, help='Maximum number of papers to download')
    parser.add_argument('--journal-filter', default=None, type=str ,help='CSV file path of the journal filter (More info on github)')

    args = parser.parse_args()
    dwn_dir = args.dwn_dir
    if dwn_dir!=None and dwn_dir[len(dwn_dir)-1]!='/':
        dwn_dir = dwn_dir + "/"
    main(args.query, args.scholar_pages, dwn_dir, args.min_year , args.max_dwn, args.journal_filter)
    
    query = "textual analysis for accounting"
    scholar_pages = 1 #each page has max 10 paper
    dwn_dir = "E:/Users/Vito/Desktop/testPaperbot/"
    jurnal_filter_path = "E:/Users/Vito/Desktop/testPaperbot/filter.csv"
    
    
    
    
    