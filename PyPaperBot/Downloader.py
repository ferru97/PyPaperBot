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
        print(
            "\nNo working Sci-Hub instance found!\nIf in your country Sci-Hub is not available consider using a VPN or a proxy")
        NetInfo.SciHub_URL = "https://sci-hub.st"


def getSaveDir(folder, fname):
    dir_ = path.join(folder, fname)
    n = 1
    while path.exists(dir_):
        n += 1
        dir_ = path.join(folder, f"({n}){fname}")

    return dir_


def saveFile(file_name, content, paper, dwn_source):
    f = open(file_name, 'wb')
    f.write(content)
    f.close()

    paper.downloaded = True
    paper.downloadedFrom = dwn_source


def downloadPapers(papers, dwnl_dir, num_limit, SciHub_URL=None):
    def URLjoin(*args):
        return "/".join(map(lambda x: str(x).rstrip('/'), args))

    NetInfo.SciHub_URL = SciHub_URL
    if NetInfo.SciHub_URL is None:
        setSciHubUrl()

    num_downloaded = 0
    paper_number = 1
    paper_files = []
    for p in papers:
        if p.canBeDownloaded() and (num_limit is None or num_downloaded < num_limit):
            print("Download {} of {} -> {}".format(paper_number, len(papers), p.title))
            paper_number += 1

            pdf_dir = getSaveDir(dwnl_dir, p.getFileName())

            faild = 0
            url = ""
            while not p.downloaded and faild != 4:
                try:
                    dwn_source = 1  # 1 scihub 2 scholar
                    if faild == 0 and p.DOI is not None:
                        url = URLjoin(NetInfo.SciHub_URL, p.DOI)
                    if faild == 1 and p.scholar_link is not None:
                        url = URLjoin(NetInfo.SciHub_URL, p.scholar_link)
                    if faild == 2 and p.scholar_link is not None and p.scholar_link[-3:] == "pdf":
                        url = p.scholar_link
                        dwn_source = 2
                    if faild == 3 and p.pdf_link is not None:
                        url = p.pdf_link
                        dwn_source = 2

                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
                    }

                    proxies = {
                        'http': 'socks5h://localhost:9050',
                        'https': 'socks5h://localhost:9050'
                    }

                    if url != "":
                        r = requests.get(url, headers=headers, proxies=proxies)
                        content_type = r.headers.get('content-type')
                        print("Initial request content type:", content_type)  # Debug print

                        if dwn_source == 1 and 'application/pdf' not in content_type:
                            time.sleep(random.randint(1, 5))

                            pdf_link = getSchiHubPDF(r.text)
                            print("pdf link:", pdf_link)  # Debug print
                            if pdf_link is not None:
                                r = requests.get(pdf_link, headers=headers, proxies=proxies, stream=True)
                                content_type = r.headers.get('content-type')
                                print("Content type for SciHub PDF:", content_type)  # Debug print

                        # Force save the file if we have the PDF URL, regardless of content type
                        if 'application/pdf' in content_type or pdf_link is not None:
                            print("Attempting to save PDF for:", p.title)  # Debug print
                            saveFile(pdf_dir, r.content, p, dwn_source)
                            num_downloaded += 1
                            p.downloaded = True
                            print("Download successful for:", p.title)  # Debug print
                        else:
                            print("Failed to retrieve PDF. Content type:", content_type)  # Debug print
                except Exception:
                    print("Failed to download paper:", p.title)  # Debug print
                    pass

                faild += 1

    return paper_files