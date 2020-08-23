# PyPaperBot
PyPaperBot is a Python tool for **downloading scientific papers** using Google Scholar, Crossref, and SciHub.
The tool tries to download papers from different sources such as PDF provided da Scholar, Scholar related links, and Scihub.
PyPaerbot is also able to download the **bibtex** of each paper.

## Features
- Download papers given a query
- Download papers given paper's DOIs
- Download papers given a Google Scholar link
- Generate Bibtex of the downloaded paper
- Filter downloaded paper by year, journal and citations number

## How to use
PyPaperBot arguments:

| Arguments  | Description | Type
| ------------- | ------------- |------------- |
| \-\-query  | Query to make on Google Scholar or Google Scholar page link  |string|
| \-\-doi  |DOI of the paper to download (this option uses only SciHub to download)  |string|
| \-\-doi-file  |File .txt containing the list of paper's DOIs to download  |string|
| \-\-scholar-pages  | Number of Google Scholar pages to inspect. Each page has a maximum of 10 papers  |int|
| \-\-dwn-dir  | Directory path in which to save the result  |string|
| \-\-min-year  | Minimal publication year of the paper to download  |int|
| \-\-max-dwn-year  | Maximum number of papers to download sorted by year  |int|
| \-\-max-dwn-cites  | Maximum number of papers to download sorted by number of citations  |int|
| \-\-journal-filter  | CSV file path of the journal filter (More info on github)  |string|
| \-\-restrict  | 0:Download only Bibtex - 1:Down load only papers PDF  |int|
| \-h  | Shows the help  |--|

### Note
You can use only one of the arguments in the following groups
- *\-\-query*, *\-\-doi-file*, and *\-\-doi* 
- *\-\-max-dwn-year* and *and max-dwn-cites*

One of the arguments *\-\-scholar-pages*, *\-\-query *, and* \-\-file* is mandatory
The arguments *\-\-scholar-pages* is mandatory when using *\-\-query *
The argument *\-\-dwn-dir* is mandatory

The argument *\-\-journal-filter*  require the path of a CSV containing a list of journal name paired with a boolean which indicates whether or not to consider that journal (0: don't consider /1: consider) [Example](https://github.com/ferru97/PyPaperBot/blob/master/file_examples/jurnals.csv)

The argument *\-\-doi-file*  require the path of a txt file containing the list of paper's DOIs to download organized with one DOI per line [Example](https://github.com/ferru97/PyPaperBot/blob/master/file_examples/papers.txt)

## SchiHub access
If access to SciHub is blocked in your country, consider using a free VPN service like [ProtonVPN](https://protonvpn.com/)

## Example
Download a maximum of 30 papers given a query and starting from 2018:
`python PyPaperBot.py --query="Machine learning" --scholar-pages=3  --min-year=2018 --dwn-dir="C:\User\example\papers"`

Download a paper given the DOI:
`python PyPaperBot.py --doi="10.0086/s41037-711-0132-1" --dwn-dir="C:\User\example\papers"`

Download papers given a file containing the DOIs:
`python PyPaperBot.py --doi-file="C:\User\example\papers\file.txt" --dwn-dir="C:\User\example\papers"`

## Disclaimer
This application is for educational purpose only. I do not take responsibility of what you choose to do with this application.
