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



gErrors = ["This page appears when Google automatically detects requests coming from your computer network which appear to be in violation of the","Attiva JavaScript"]
avoid_texts = ["[PDF]","[HTML]","ACNP Full Text","Full View",""]
a_title_tag = "data-clk-atid"
# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    title = False;
    lastSquare = False;
    string_title = "";
    
    titles_found =  []
    
    def handle_starttag(self, tag, attrs):
            if tag=="a":
                for x in attrs:
                   if x[0] == a_title_tag:
                       self.title = True;
            return
   
    def handle_endtag(self, tag):
            Title = self.string_title.strip()
            if tag=="a" and self.title==True and len(Title)>0:
                self.titles_found.append(Title)
                self.string_title = "";
                self.title = False;
            return
   
    def handle_data(self, data):
        if data[0]=='[':
                self.lastSquare = True
                
        if self.title==True and self.lastSquare==False and (data.strip() not in avoid_texts):
                self.string_title += data;    
                
        
        if data[0]!="[" and self.lastSquare==True:
            self.lastSquare = False
        
                
        if data.strip() in gErrors:
            print ("SGAMATO!")
    
    def getTitlesFound(self):
        return self.titles_found;
    
    def resetTitles(self):
        self.titles_found =  []

    

def main(query, number):
    
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
    url = "https://scholar.google.com/scholar?q="+query;
    

    parser = MyHTMLParser()
    for i in range(0,int(number/10)):
        if i>0:
            url = url + "&start=" + str(10*i)
        html = requests.get(url, headers=HEADERS)
        html = html.text
        parser.feed(html)
        
        papers = getPapersInfo(parser.getTitlesFound())
        for p in papers:
            print(p["DOI"])
        
        parser.resetTitles()
        print("Next -> ",i+1)
    
        
    
def similarStrings(a, b):
    return SequenceMatcher(None, a, b).ratio()


def getPapersInfo(titles):
    papers_return = []
    for title in titles:
        title = title.strip().lower()
        queries = {'query.bibliographic': title,'sort':'relevance'}

        found = False;
        cache = []
        paper_found = {"name_original":title,"name_found":"","timestamp":"0","DOI":""};
        for el in iterate_publications_as_json(max_results=10, queries=queries):
            not_empty = True
            try:
              el_title = el["title"][0].strip().lower()
              el_doi = el["DOI"].strip().lower()
              el_timestamp = int(el["created"]["timestamp"])
              cache.append("-"+el_title)
            except:
              not_empty = False
            
            if not_empty==True and similarStrings(title ,el_title)>0.75:
                found = True;
                if el_timestamp > int(paper_found["timestamp"]):
                    paper_found["name"] = el_title
                    paper_found["timestamp"] = str(el_timestamp)
                    paper_found["DOI"] = el_doi
                break
            
        papers_return.append(paper_found)
            
        if found == False:
            print("NOT FOUND -> "+title)
            for c in cache:
                print(c)
                
        time.sleep(random.randint(5,10))
        
    return papers_return
        

    
if __name__ == "__main__":
    query = "textual analysis accounting"
    paper_num = 20
    main(query,paper_num)
