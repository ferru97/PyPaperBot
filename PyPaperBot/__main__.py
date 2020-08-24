# -*- coding: utf-8 -*-

import argparse
import sys
from Paper import Paper
from PapersFilters import filterJurnals, filter_min_date, similarStrings
from Downloader import downloadPapers
from Scholar import ScholarPapersInfo
from Crossref import getPapersInfoFromDOIs


def start(query, scholar_pages, dwn_dir, min_date=None, num_limit=None, num_limit_type=None, filter_jurnal_file=None, restrict=None, DOIs=None):
    
    to_download = []
    if DOIs==None:
        print("Query: {}".format(query)) 
        to_download = ScholarPapersInfo(query, scholar_pages, restrict)
    else:
        print("Downloading papers from DOIs\n")
        num = 1
        i = 0
        while i<len(DOIs):
            DOI = DOIs[i]
            print("Searching paper {} of {} with DOI {}".format(num,len(DOIs),DOI))
            papersInfo = getPapersInfoFromDOIs(DOI, restrict)
            to_download.append(papersInfo)

            num += 1
            i +=  1
                        
    
    if restrict!=0:
        if filter_jurnal_file!=None:
           to_download = filterJurnals(to_download,filter_jurnal_file)
       
        if min_date!=None:
            to_download = filter_min_date(to_download,min_date)  
         
        if num_limit_type!=None and num_limit_type==0:       
            to_download.sort(key=lambda x: int(x.sc_year) if x.sc_year!=None else 0, reverse=True)
            
        if num_limit_type!=None and num_limit_type==1:       
            to_download.sort(key=lambda x: int(x.sc_cites) if x.sc_cites!=None else 0, reverse=True)
    
    
    downloadPapers(to_download, dwn_dir, num_limit)
    Paper.generateReport(to_download,dwn_dir+"result.csv")
    Paper.generateBibtex(to_download,dwn_dir+"bibtex.bib")
    



def main():
    print("PyPaperBot is a Python tool for downloading scientific papers using Google Scholar, Crossref and SciHub.\n")
    
    parser = argparse.ArgumentParser(description='PyPaperBot is python tool to search and dwonload scientific papers using Google Scholar, Crossref and SciHub')
    parser.add_argument('--query', type=str, default=None, help='Query to make on Google Scholar or Google Scholar page link')
    parser.add_argument('--doi', type=str, default=None, help='DOI of the paper to download (this option uses only SciHub to download)')
    parser.add_argument('--doi-file', type=str, default=None, help='File .txt containing the list of paper\'s DOIs to download')
    parser.add_argument('--scholar-pages', type=int, help='Number of Google Scholar pages to inspect. Each page has a maximum of 10 papers (required for --query)')
    parser.add_argument('--dwn-dir', type=str, help='Directory path in which to save the results')
    parser.add_argument('--min-year', default=None, type=int, help='Minimal publication year of the paper to download')
    parser.add_argument('--max-dwn-year', default=None, type=int, help='Maximum number of papers to download sorted by year')
    parser.add_argument('--max-dwn-cites', default=None, type=int, help='Maximum number of papers to download sorted by number of citations')
    parser.add_argument('--journal-filter', default=None, type=str ,help='CSV file path of the journal filter (More info on github)')
    parser.add_argument('--restrict', default=None, type=int ,choices=[0,1], help='0:Download only Bibtex - 1:Down load only papers PDF')

    args = parser.parse_args()
    
    if args.query==None and args.doi_file==None and args.doi==None:
        print("Error, provide at least one of the following arguments: --query or --file")
        sys.exit()
        
    if (args.query!=None and args.doi_file!=None) or (args.query!=None and args.doi!=None) or (args.doi!=None and args.doi_file!=None):
        print("Error: Only one option between '--query', '--doi-file' and '--doi' can be used")
        sys.exit()

    if args.dwn_dir==None:
        print("Error, provide the directory path in which to save the results")
        sys.exit()
    
    dwn_dir = args.dwn_dir.replace('\\', '/')
    if dwn_dir[len(dwn_dir)-1]!='/':
        dwn_dir = dwn_dir + "/"
    
    if args.max_dwn_year != None and args.max_dwn_cites != None:
        print("Error: Only one option between '--max-dwn-year' and '--max-dwn-cites' can be used ")
        sys.exit()
        
    if(args.query != None and args.scholar_pages==None):
        print("Error: with --query provide also --scholar-pages")
        sys.exit()
         
    DOIs = None    
    if args.doi_file!=None:
        DOIs = [] 
        f = args.doi_file.replace('\\', '/')
        with open(f) as file_in:
            for line in file_in:
                if line[len(line)-1]=='\n':
                    DOIs.append(line[:-1])
                else:
                    DOIs.append(line)   

    if args.doi!=None: 
        DOIs = [args.doi]     
    
    max_dwn = None
    max_dwn_type = None
    if args.max_dwn_year != None:
        max_dwn = args.max_dwn_year
        max_dwn_type = 0
    if args.max_dwn_cites != None:
        max_dwn = args.max_dwn_cites
        max_dwn_type = 1
                

    start(args.query, args.scholar_pages, dwn_dir, args.min_year , max_dwn, max_dwn_type , args.journal_filter, args.restrict, DOIs)


if __name__ == "__main__":
    main()