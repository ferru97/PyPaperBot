from crossref_commons.iteration import iterate_publications_as_json
from crossref_commons.retrieval import get_entity
from crossref_commons.types import EntityType, OutputType
from .PapersFilters import similarStrings
from .Paper import Paper
import requests
import time
import random


def getBibtex(DOI):
    try:
        url_bibtex = "http://api.crossref.org/works/" + DOI + "/transform/application/x-bibtex"
        x = requests.get(url_bibtex)
        return str(x.text)
    except:
        return None


def getPapersInfoFromDOIs(DOI, restrict):
    paper_found = Paper()
    paper_found.DOI = DOI

    try:
        paper = get_entity(DOI, EntityType.PUBLICATION, OutputType.JSON)
        if paper!=None and len(paper)>0:
            if "title" in paper:
                paper_found.title = paper["title"][0]
            if "short-container-title" in paper and len(paper["short-container-title"])>0:
                paper_found.jurnal = paper["short-container-title"][0]

            if restrict==None or restrict!=1:
                paper_found.setBibtex(getBibtex(paper_found.DOI))
    except:
        print("Paper not found "+DOI)

    return paper_found


#Get paper information from Crossref and return a list of Paper
def getPapersInfo(papers, scholar_search_link, restrict, scholar_results):
    papers_return = []
    num = 1
    for paper in papers:
        while num <= scholar_results:
            title = paper['title']
            queries = {'query.bibliographic': title.lower(),'sort':'relevance',"select":"DOI,title,deposited,author,short-container-title"}

            print("Searching paper {} of {} on Crossref...".format(num,scholar_results))
            num += 1

            found_timestamp = 0
            paper_found = Paper(title,paper['link'],scholar_search_link, paper['cites'], paper['link_pdf'], paper['year'], paper['authors'])
            while True:
                try:
                    for el in iterate_publications_as_json(max_results=30, queries=queries):

                        el_date = 0
                        if "deposited" in el and "timestamp" in el["deposited"]:
                            el_date = int(el["deposited"]["timestamp"])

                        if (paper_found.DOI==None or el_date>found_timestamp) and "title" in el and similarStrings(title.lower() ,el["title"][0].lower())>0.75:
                            found_timestamp = el_date

                            if "DOI" in el:
                                paper_found.DOI = el["DOI"].strip().lower()
                            if "short-container-title" in el and len(el["short-container-title"])>0:
                                paper_found.jurnal = el["short-container-title"][0]

                            if restrict==None or restrict!=1:
                                paper_found.setBibtex(getBibtex(paper_found.DOI))

                    break
                except ConnectionError as e:
                    print("Wait 10 seconds and try again...")
                    time.sleep(10)

            papers_return.append(paper_found)

            time.sleep(random.randint(1,10))

    return papers_return
