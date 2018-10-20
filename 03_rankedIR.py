import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import *
import re
import math
import operator
from os import path

path = path.dirname(__file__)

# load index file into memory, output in dictionary form
def loadIndex(file):
    with open(file) as f:
        text = f.read()
    indexdic = {}
    for e in text.split('\n\n')[:-1]:
        word = e.split('\n')[0].replace(':','')
        l = e.split('\n\t')[1:]
        text_pos = {}
        for i in l:
            textID = i.split(': ')[0]
            posList = i.split(': ')[1].split(',')
            posList = list(map(int, posList))
            text_pos[int(textID)] = posList
            indexdic[word] = text_pos
    return indexdic

def tokenizer(text):
    # match all the words
    scanner = re.compile(r'\w+')
    newtext =  re.findall(scanner, text.lower())
    return newtext

def deleteStopWords(text):
    with open(path+'/stopwords.txt') as f:
        stopWords = f.read().split(' ')
    newtext = []
    for word in text:
        if word not in stopWords:
            newtext.append(word)
    return newtext

def stemmer(text):
    stemmer = PorterStemmer()
    newtext = [stemmer.stem(word) for word in text]
    return newtext

def preprocess(text):
    text = tokenizer(text)
    text = deleteStopWords(text)
    text = stemmer(text)
    return text

# output: a set of text ID having this word/phrase
def getIndexSet(word):
    if "\"" in word:
        phrase = word.replace("\"", '')
        index = phraseSearch(phrase)
    else:
        try:
            wordPro = preprocess(word)[0]
            index = list(indexdic[wordPro].keys())
        except:
            index = []
    return set(index)

def booleanSearch(searchTerm):
    phrase =  False
    stList = []
    for e in searchTerm.split(' '):
        if "\"" in e:
            if phrase==False:
                phrase = True
                stList.append(e)
            else:
                stList[-1] += ' '+e
                phrase = False
        else:
            stList.append(e)
    l = len(stList)

    op = '' # record current operator
    pos = 0 # the position of current word
    opnot = False # whether the operator is NOT
    resultSet = set()
    tempSet = set()
    FirstWord = True # if it's the first word, the operation will be a little different
    while pos<l:
        currentWord = stList[pos]
        if currentWord == 'AND':
            op = 'AND'
        elif currentWord == 'OR':
            op = 'OR'
        elif currentWord == 'NOT':
            opnot = True
        else:
            if opnot:
                tempSet = set(range(1,textNum+1)).difference(getIndexSet(currentWord))
                opnot = False
            else:
                tempSet = getIndexSet(currentWord)
            if FirstWord:
                resultSet = tempSet
                FirstWord = False
            if op == 'AND':
                resultSet = set.intersection(resultSet, tempSet)
                op = ''
            if op == 'OR':
                resultSet = set.union(resultSet, tempSet)
                op = ''
        pos += 1
    return sorted(resultSet)

# input: a phrase
# output: a list of text ID
def phraseSearch(searchTerm):
# using previous boolean search function to find texts which have all
# words in the search term, ignoring whether they are neighbor or not.
    searchTermList = searchTerm.split(' ')
    searchTermPro = ' AND '.join(searchTermList)
    bothExistList = booleanSearch(searchTermPro)
    #print(bothExistList)
    result = []
    for textID in bothExistList:
        dic = {}
        for i, word in enumerate(searchTermList):
            word = preprocess(word)[0]
            dic[i] = [e-i for e in indexdic[word][textID]]  #e-i means make all the word in a phrase to the same position
        conj = set.intersection(*(set(val) for val in dic.values()))
        if conj:
            result.append(textID)
    return result

def getTF(term, document):
    try: # term may not exist in document
        tf = len(indexdic[term][document])
    except:
        tf = 0
    return tf

def getDF(term):
    try:
        df = len(indexdic[term])
    except:
        df = 0
    return df

def termWeight(term, document):
    tf = getTF(term, document)
    df = getDF(term)
    idf = math.log10(N/df)
    if tf>0:
        w = (1+math.log10(tf))*idf
    else:
        w = 0
    return w

def Score(query, document):
    score = 0
    for term in query:
        score += termWeight(term, document)
    return score

def getAllDoc(query):
    ORquery = ' OR '.join(query)
    allDoc = booleanSearch(ORquery)
    return allDoc


indexfile = path + '/index.txt'
indexdic = loadIndex(indexfile)

# get all the documents
allDoc = []
for word in indexdic:
    for doc in indexdic[word]:
        if doc not in allDoc:
            allDoc.append(doc)
N = len(allDoc)

with open(path+'/CW1collection/queries.ranked.txt') as f:
    for query in f:
        queryID, query = query.split(' ',1)
        query = preprocess(query)
        allDoc = getAllDoc(query) # get index of documents having at least one word in query

        scoredic = {}
        for doc in allDoc:
            score = Score(query, doc)
            scoredic[doc] = score
        sorted_score = sorted(scoredic.items(), key=operator.itemgetter(1))[::-1]

        with open(path+'/result/results.ranked.txt', 'a') as f:
            for i, e in enumerate(sorted_score):
                if i < 1000:
                    f.write(str(queryID)+' 0 '+str(e[0])+' 0 '+str(round(e[1],4))+' 0\n')
