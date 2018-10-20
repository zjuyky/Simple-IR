# TTDS Coursework1

## Getting Started
These instructions will help you run the code on your machine for testing purposes.
### Install NLTK
NLTK is a platform for building Python programs to work with human language data.  
If you haven't install it: `pip install nltk`   
### Check the files
There are 3 executable python files in the root directory:   
  * 01_create_index.py
  * 02_search.py
  * 03_rankedIR.py

Collections and queries are stored in `CW1collection` folder.
* `queries.boolean.txt`: queries for boolean search, in the following format:  
```
1 term11 AND term12         
2 "term21 term22"           
3 #15(term1, term2)
```
Phrase should be involved in double quotes. Query 3 is proximity search, `#15` means the distance of term1 and term2.    

* `queries.ranked.txt`: queries for ranked search, in the following format:   
```
1 income tax reduction  
2 stock market in Japan  
```
Search results will be stored in `Result` folder.

## Running the code  
### 1. Run 01_create_index.py
It will create a index file named `index.txt`, which will be used in other codes. The format of index is:  
```
term: 
       docID: pos1, pos2, .... 
       docID: pos1, pos2, ....
```
Here I have run this code in advance.  

### 2. Run 02_search.py to do boolean search
It searchs documents in collections using queries in `queries.boolean.txt`, the result is in `/result/results.boolean.txt`.  

### 3. Run 03_rankedIR.py to do ranked search based TFIDF
It searchs most related documents using queries in `queries.ranked.txt`, the result is in `/result/results.ranked.txt`.
