import time
import requests
import functools
from .HTMLparsers import schoolarParser
from .Crossref import getPapersInfo


HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
SciHub_URL = "https://sci-hub.tw/"   


def waithIPchange():
    input("You have been blocked, change your IP or VPN than press Enter...")
    print("Wait 30 seconds...")
    time.sleep(30)


def ScholarPapersInfo(query, scholar_pages, restrict):
   
    global HEADERS
    javascript_error = "Sorry, we can't verify that you're not a robot when JavaScript is turned off"
    
    url = "https://scholar.google.com/scholar?hl=en&q="+query+"&as_vis=1&as_sdt=1,5"
    if len(query)>7 and (query[0:7]=="http://" or query[0:8]=="https://"):
         url = query        
        
        
    to_download = []
    last_blocked = False
    i = 0
    while i < scholar_pages:
        html = requests.get(url, headers=HEADERS)
        html = html.text
        
        if javascript_error in html and last_blocked==False:
            waithIPchange()
            i -= 1
            continue
        else:
            last_blocked=False
        
        papers = schoolarParser(html)
        print("\nGoogle Scholar page {} : {} papers found".format((i+1),len(papers)))
        
        if(len(papers)>0):
            papersInfo = getPapersInfo(papers, url, restrict)
            info_valids = functools.reduce(lambda a,b : a+1 if b.DOI!=None else a, papersInfo, 0)
            print("Papers found on Crossref: {}/{}\n".format(info_valids,len(papers)))
            
            to_download.append(papersInfo)
        else:
            print("Paper not found...")

        i += 1
        url += "&start=" + str(10*i)
        
    return [item for sublist in to_download for item in sublist]