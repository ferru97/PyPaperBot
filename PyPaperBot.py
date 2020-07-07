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
import argparse
import sys
import re



def main(query, scholar_pages, dwn_dir, min_date=None, num_limit=None, num_limit_type=None, filter_jurnal_file=None, restrict=None, file=None):
    
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
    
    to_download = []
    if file==None:
        if len(query)>2 and (query[0:7]=="http://" or query[0:8]=="https://"):
            url = query
        else:
            url = "https://scholar.google.com/scholar?hl=en&q="+query+"&as_vis=1&as_sdt=1,5";
        

        for i in range(0,scholar_pages):
            if i>0:
                url = url + "&start=" + str(10*i)
            html = requests.get(url, headers=HEADERS)
            html = html.text
            
            papers = HTMLparsers.schoolarParser(html)
            print("Google Scholar page "+str(i+1)+" : "+str(len(papers))+" papers found")
            
            papersInfo = getPapersInfo(papers, url, restrict)
            info_valids = 0
            for x in papersInfo:
                if x.sc_DOI!=None:
                    info_valids += 1
            print("Papers info from Crossref: "+str(info_valids))
            
            to_download.append(papersInfo)
         
            print("\n")
    else:
        print("Downloading papers from file\n")
        num = 1
        for title in file:
            url = "https://scholar.google.com/scholar?hl=en&q="+title+"&as_vis=1&as_sdt=1,5";
            html = requests.get(url, headers=HEADERS)
            html = html.text
            
            print("Searching paper {} of {} on Google".format(str(num),str(len(file))))
            papers = HTMLparsers.schoolarParser(html)
            paper = [getOnePaper(papers,title.lower())]
            
            papersInfo = getPapersInfo(paper, url, restrict)
            info_valids = 0
            for x in papersInfo:
                if x.sc_DOI!=None:
                    info_valids += 1
            
            to_download.append(papersInfo)
            num += 1
         
            print("\n")
                        
    
    to_download = [item for sublist in to_download for item in sublist] 
    
    if restrict==None or restrict!=0:
        
        if filter_jurnal_file!=None:
           to_download = filterJurnals(to_download,filter_jurnal_file)
        
        
        if min_date!=None:
            to_download = filter_min_date(to_download,min_date)  
         
     
        if num_limit_type!=None and num_limit_type==0:       
            to_download.sort(key=lambda x: int(x.sc_year) if x.sc_year!=None else 0, reverse=True)
            
        if num_limit_type!=None and num_limit_type==1:       
            to_download.sort(key=lambda x: int(x.sc_cites) if x.sc_cites!=None else 0, reverse=True)
    
    
        SciHubDownload(to_download, dwn_dir, num_limit)
          
    Paper.generateReport(to_download,dwn_dir+"result.csv")
    Paper.generateBibtex(to_download,dwn_dir+"bibtex.bib")
    
    
def getOnePaper(papers,title):
    most_similar = papers[0]
    similar_score = 0
    
    for p in papers:
        score = similarStrings(p[0], title.lower())
        if score>similar_score:
            similar_score = score
            most_similar = p
            
    return most_similar
    

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
        if paper.sc_year!=None and int(paper.sc_year)>=min_year:
             new_list.append(paper)
            
    return new_list


def saveFile(file_name,content, paper,dwn_source):    
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
            
            if p.getFileName()!=None:
                pdf_dir = dwnl_dir + re.sub('[^\w\-_\. ]', '_', p.getFileName())
            else:
                pdf_dir = dwnl_dir + re.sub('[^\w\-_\. ]', '_', p.sc_title) + ".pdf"
                                    
            faild = 0
            while p.downloaded==False and faild!=4:        
                try:   
                    
                    url = ""
                    dwn_source = 1 #1 scihub 2 scholar 3 scholar PDF(if exists)
                    if faild==0 and p.sc_DOI!=None:
                        url = SciHub_URL + p.sc_DOI
                    if faild==1 and p.sc_link!=None:
                        url = SciHub_URL + p.sc_link
                    if faild==2 and p.sc_link!=None:
                        if p.sc_link[-3:]=="pdf":
                            url = p.sc_link
                        dwn_source = 2
                    if faild==3 and p.sc_pdf_link!=None:
                        url = p.sc_pdf_link
                        dwn_source = 2
                        
                
                    if url!="":
                        r = requests.get(url, headers=HEADERS)
                        content_type = r.headers.get('content-type')
                        
                        if dwn_source==1 and 'application/pdf' not in content_type:
                            time.sleep(random.randint(1,5))
                            
                            pdf_link = HTMLparsers.getSchiHubPDF(r.text)
                            if(pdf_link != None):
                                r = requests.get(pdf_link, headers=HEADERS)
                                content_type = r.headers.get('content-type')
    
                        if 'application/pdf' in content_type:
                            saveFile(pdf_dir,r.content,p,dwn_source)
                        
                    faild += 1
                except:
                    faild += 1
                    
        
    
def similarStrings(a, b):
    return SequenceMatcher(None, a, b).ratio()


def getTimestamp(paper):
    timestamp = 0
    if "deposited" in paper:
        if "timestamp" in paper["deposited"]:
            timestamp = int(paper["deposited"]["timestamp"])
    return timestamp


def getPapersInfo(papers, scholar_search_link, restrict):
    papers_return = []
    num = 1
    for paper in papers:
        title = paper[0].lower()
        queries = {'query.bibliographic': title,'sort':'relevance',"select":"DOI,title,deposited,author,short-container-title"}
        
        print("Searching paper {} of {} on Crossref...".format(int(num),int(len(papers))))
        num += 1

        found = False;
        found_timestamp = 0
        paper_found = Paper(title,paper[1],scholar_search_link, paper[2], paper[3])
        for el in iterate_publications_as_json(max_results=30, queries=queries):
           
            el_date = getTimestamp(el);
            
            if (found==False or el_date>found_timestamp) and ("title" in el) and similarStrings(title ,el["title"][0].strip().lower())>0.75:
                found_timestamp = el_date

                if "DOI" in el:
                    paper_found.sc_DOI = el["DOI"].strip().lower()
                if "author" in el:
                    paper_found.setAuthors(el["author"])
                if "short-container-title" in el:
                    paper_found.sc_jurnal = el["short-container-title"][0]
                   
                if restrict==None or restrict!=1:    
                    #get bibtex from scholary    
                    try: 
                        url_bibtex = "http://api.crossref.org/works/" + paper_found.sc_DOI + "/transform/application/x-bibtex"
                        x = requests.get(url_bibtex)
                        paper_found.setBibtex(str(x.text))
                    except:
                        pass
 
                found = True        
            
        papers_return.append(paper_found)
                
        time.sleep(random.randint(1,10))
        
    return papers_return

    
if __name__ == "__main__":
    print("PyPaperBot is a Python tool to download scientific papers found on Google Scholar and downloaded with SciHub\n")
    
    parser = argparse.ArgumentParser(description='PyPaperBot is python tool to search and dwonload scientific papers using Google Scholar, Crossref and SciHub')
    parser.add_argument('--query', type=str, default=None, help='Query to make on Google Scholar or Google Scholar page link')
    parser.add_argument('--file', type=str, default=None, help='File .txt containing the list of papers to download')
    parser.add_argument('--scholar-pages', required=True, type=int, help='Number of Google Scholar pages to inspect. Each page has a maximum of 10 papers')
    parser.add_argument('--dwn-dir', type=str, help='Directory path in which to save the result')
    parser.add_argument('--min-year', default=None, type=int, help='Minimal publication year of the paper to download')
    parser.add_argument('--max-dwn-year', default=None, type=int, help='Maximum number of papers to download sorted by year')
    parser.add_argument('--max-dwn-cites', default=None, type=int, help='Maximum number of papers to download sorted by number of citations')
    parser.add_argument('--journal-filter', default=None, type=str ,help='CSV file path of the journal filter (More info on github)')
    parser.add_argument('--restrict', default=None, type=int ,choices=[0,1], help='0:Download only Bibtex - 1:Down load only papers PDF')


    args = parser.parse_args()
    dwn_dir = args.dwn_dir.replace('\\', '/')
    if dwn_dir!=None and dwn_dir[len(dwn_dir)-1]!='/':
        dwn_dir = dwn_dir + "/"
    
    if args.query==None and args.file==None:
        print("Error, provide at least one of the following arguments: --query or --file")
        sys.exit()
        
    if args.query!=None and args.file!=None:
        print("Error: Only one option between '--query' and '--file' can be used")
        sys.exit()
    
    if args.max_dwn_year != None and args.max_dwn_cites != None:
        print("Error: Only one option between '--max-dwn-year' and '--max-dwn-cites' can be used ")
        sys.exit()
         
    titles = None    
    if args.file!=None:
        titles = [] 
        f = args.file.replace('\\', '/')
        with open(f) as file_in:
            for line in file_in:
                titles.append(line)
        
    if args.query!=None:
        print("Query: {} \n".format(args.query))    
    
    max_dwn = None
    max_dwn_type = None
    if args.max_dwn_year != None:
        max_dwn = args.max_dwn_year
        max_dwn_type = 0
    if args.max_dwn_cites != None:
        max_dwn = args.max_dwn_cites
        max_dwn_type = 1
                

    main(args.query, args.scholar_pages, dwn_dir, args.min_year , max_dwn, max_dwn_type , args.journal_filter, args.restrict, titles)
    
    
    


    
    

    