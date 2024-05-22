import time
import requests
import functools
from .HTMLparsers import schoolarParser
from .Crossref import getPapersInfo
from .NetInfo import NetInfo


def waithIPchange():
    while True:
        inp = input('You have been blocked, try changing your IP or using a VPN. '
                    'Press Enter to continue downloading, or type "exit" to stop and exit....')
        if inp.strip().lower() == "exit":
            return False
        elif not inp.strip():
            print("Wait 30 seconds...")
            time.sleep(30)
            return True


def scholar_requests(scholar_pages, url, restrict, scholar_results=10):
    javascript_error = "Sorry, we can't verify that you're not a robot when JavaScript is turned off"
    to_download = []
    for i in scholar_pages:
        while True:
            res_url = url % (scholar_results * (i - 1))
            html = requests.get(res_url, headers=NetInfo.HEADERS)
            html = html.text

            if javascript_error in html:
                is_continue = waithIPchange()
                if not is_continue:
                    return to_download
            else:
                break

        papers = schoolarParser(html)
        if len(papers) > scholar_results:
            papers = papers[0:scholar_results]

        print("\nGoogle Scholar page {} : {} papers found".format(i, scholar_results))

        if len(papers) > 0:
            papersInfo = getPapersInfo(papers, url, restrict, scholar_results)
            info_valids = functools.reduce(lambda a, b: a + 1 if b.DOI is not None else a, papersInfo, 0)
            print("Papers found on Crossref: {}/{}\n".format(info_valids, len(papers)))

            to_download.append(papersInfo)
        else:
            print("Paper not found...")

    return to_download


def ScholarPapersInfo(query, scholar_pages, restrict, min_date=None, scholar_results=10, cites=None):
    url = r"https://scholar.google.com/scholar?hl=en&as_vis=1&as_sdt=1,5&start=%d"
    if query:
        url += f"&q={query}"
    if cites:
        url += f"&cites={cites}"
    if min_date:
        url += f"&as_ylo={min_date}"

    if len(query) > 7 and (query.startswith("http://") or query.startswith("https://")):
        url = query

    to_download = scholar_requests(scholar_pages, url, restrict, scholar_results)

    return [item for sublist in to_download for item in sublist]
