from os import path
import requests
import time
from .HTMLparsers import getSchiHubPDF, SciHubUrls
import random
from .NetInfo import NetInfo

def setSciHubUrl():
    r = requests.get(NetInfo.SciHub_URLs_repo, headers=NetInfo.HEADERS)
    links = SciHubUrls(r.text)
    found = False

    for l in links:
        try:
            r = requests.get(l, headers=NetInfo.HEADERS)
            if r.status_code == 200:
                found = True
                NetInfo.SciHub_URL = l
                break
        except:
            pass
    if found:
        print("\nUsing {} as Sci-Hub instance".format(NetInfo.SciHub_URL))
    else:
        print("\nNo working Sci-Hub instance found!\nIf in your country Sci-Hub is not available consider using a VPN or a proxy")
        NetInfo.SciHub_URL = "https://sci-hub.st"


def getSaveDir(folder, fname):
    dir_ = path.join(folder, fname)
    n = 1
    while path.exists(dir_):
       n += 1
       dir_ = path.join(folder, "("+str(n)+")"+fname)

    return dir_

def saveFile(file_name,content, paper,dwn_source):
    f = open(file_name, 'wb')
    f.write(content)
    f.close()

    paper.downloaded = True
    paper.downloadedFrom = dwn_source

def downloadPapers(papers, dwnl_dir, num_limit, scholar_results, SciHub_URL=None):
    def URLjoin(*args):
        return "/".join(map(lambda x: str(x).rstrip('/'), args))

    NetInfo.SciHub_URL = SciHub_URL
    if NetInfo.SciHub_URL==None:
        setSciHubUrl()

    num_downloaded = 0
    paper_number = 1
    paper_files = []
    for p in papers:
        if p.canBeDownloaded() and (num_limit==None or num_downloaded<num_limit):
            print("Download {} of {} -> {}".format(paper_number, scholar_results, p.title))
            paper_number += 1

            pdf_dir = getSaveDir(dwnl_dir, p.getFileName())

            faild = 0
            while p.downloaded==False and faild!=4:
                try:
                    dwn_source = 1 #1 scihub 2 scholar
                    if faild==0 and p.DOI!=None:
                        url = URLjoin(NetInfo.SciHub_URL, p.DOI)
                    if faild==1 and p.scholar_link!=None:
                        url = URLjoin(NetInfo.SciHub_URL, p.scholar_link)
                    if faild==2 and p.scholar_link!=None and p.scholar_link[-3:]=="pdf":
                        url = p.scholar_link
                        dwn_source = 2
                    if faild==3 and p.pdf_link!=None:
                        url = p.pdf_link
                        dwn_source = 2

                    if url!="":
                        r = requests.get(url, headers=NetInfo.HEADERS)
                        content_type = r.headers.get('content-type')

                        if dwn_source==1 and 'application/pdf' not in content_type:
                            time.sleep(random.randint(1,5))

                            pdf_link = getSchiHubPDF(r.text)
                            if(pdf_link != None):
                                r = requests.get(pdf_link, headers=NetInfo.HEADERS)
                                content_type = r.headers.get('content-type')

                        if 'application/pdf' in content_type:
                            paper_files.append(saveFile(pdf_dir,r.content,p,dwn_source))
                except Exception:
                    pass

                faild += 1
