# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 11:59:42 2020

@author: Vito
"""
from bs4 import BeautifulSoup

def schoolarParser(html):
    result = []
    soup = BeautifulSoup(html, "html.parser")
    for element in soup.findAll("div", class_="gs_r gs_or gs_scl"):
        if isBook(element) == False:
            title = None
            link = None
            link_pdf = None
            cites = None
            year = None
            authors = None
            for h3 in element.findAll("h3", class_="gs_rt"):
                found = False
                for a in h3.findAll("a"):
                    if found == False:
                        title = a.text
                        link = a.get("href")
                        found = True
            for a in element.findAll("a"):
                 if "Cited by" in a.text:
                     cites = int(a.text[8:])
                 if "[PDF]" in a.text:
                     link_pdf = a.get("href")
            for div in element.findAll("div", class_="gs_a"):
                try:
                    authors, source_and_year, source = div.text.replace('\u00A0', ' ').split(" - ")
                except ValueError:
                    continue

                if not authors.strip().endswith('\u2026'):
                    # There is no ellipsis at the end so we know the full list of authors
                    authors = authors.replace(', ', ';')
                else:
                    authors = None
                try:
                    year = int(source_and_year[-4:])
                except ValueError:
                    continue
                if not (1000 <= year <= 3000):
                    year = None
                else:
                    year = str(year)
            if title!=None:
                result.append({
                    'title' : title,
                    'link' : link,
                    'cites' : cites,
                    'link_pdf' : link_pdf,
                    'year' : year,
                    'authors' : authors})
    return result



def isBook(tag):
    result = False
    for span in tag.findAll("span", class_="gs_ct2"):
        if span.text=="[B]":
            result = True
    return result



def getSchiHubPDF(html):
    result = None
    soup = BeautifulSoup(html, "html.parser")

    iframe = soup.find(id='pdf')
    plugin = soup.find(id='plugin')

    if iframe!=None:
        result = iframe.get("src")

    if plugin!=None and result==None:
        result = plugin.get("src")

    if result!=None and result[0]!="h":
        result = "https:"+result

    return result

def SciHubUrls(html):
    result = []
    soup = BeautifulSoup(html, "html.parser")

    for ul in soup.findAll("ul"):
        for a in ul.findAll("a"):
            link = a.get("href")
            if link.startswith("https://sci-hub.") or link.startswith("http://sci-hub."):
                result.append(link)

    return result

