from os import path
import requests
import time
from .HTMLparsers import getSchiHubPDF
import random


HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
SciHub_URL = "https://sci-hub.tw/" 

def saveFile(file_name,content, paper,dwn_source):    
    if path.exists(file_name):
       file_name_temp = file_name
       n = 2
       while path.exists(file_name_temp):
           file_name_temp = "("+str(n)+")"+file_name 
           n += 1
       file_name = file_name_temp
         
    f = open(file_name, 'wb')
    f.write(content)
    f.close()

    paper.downloaded = True
    paper.downloadedFrom = dwn_source
            
    
def downloadPapers(papers, dwnl_dir, num_limit):
    global HEADERS
    global SciHub_URL
    
    num_downloaded = 0
    paper_number = 1
    paper_files = []
    for p in papers: 
        if p.canBeDownloaded() and (num_limit==None or num_downloaded<num_limit):        
            print("Download {} of {} -> {}".format(paper_number, len(papers), p.title))
            paper_number += 1
            
            pdf_dir = dwnl_dir + p.getFileName()
                                    
            faild = 0
            while p.downloaded==False and faild!=4:        
                try:   
                    
                    dwn_source = 1 #1 scihub 2 scholar 
                    if faild==0 and p.DOI!=None:
                        url = SciHub_URL + p.DOI
                    if faild==1 and p.scholar_link!=None:
                        url = SciHub_URL + p.scholar_link
                        
                    if faild==2 and p.scholar_link!=None and p.scholar_link[-3:]=="pdf":
                        url = p.scholar_link
                        dwn_source = 2
                    if faild==3 and p.pdf_link!=None:
                        url = p.pdf_link
                        dwn_source = 2
                        
                
                    if url!="":
                        r = requests.get(url, headers=HEADERS)
                        content_type = r.headers.get('content-type')
                        
                        if dwn_source==1 and 'application/pdf' not in content_type:
                            time.sleep(random.randint(1,5))
                            
                            pdf_link = getSchiHubPDF(r.text)
                            if(pdf_link != None):
                                r = requests.get(pdf_link, headers=HEADERS)
                                content_type = r.headers.get('content-type')
    
                        if 'application/pdf' in content_type:
                            paper_files.append(saveFile(pdf_dir,r.content,p,dwn_source))
                        
                except:
                    pass
                
                faild += 1