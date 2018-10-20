from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem.porter import *
import re
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

# input: a word or a phrase
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

def booleanSearch(query):
    phrase =  False
    stList = []
    for e in query.split(' '):
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
                tempSet = set(allDoc).difference(getIndexSet(currentWord))
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
def phraseSearch(phrase):
# using previous boolean search function to find texts which have all
# words in the search term, ignoring whether they are neighbor or not.
    termList = phrase.split(' ')
    newquery = ' AND '.join(termList)
    bothExistList = booleanSearch(newquery)
    #print(bothExistList)
    result = []
    for textID in bothExistList:
        dic = {}
        for i, word in enumerate(termList):
            word = preprocess(word)[0]
            dic[i] = [e-i for e in indexdic[word][textID]]  #e-i means make all the word in a phrase to the same position
        conj = set.intersection(*(set(val) for val in dic.values()))
        if conj:
            result.append(textID)
    return result

def proximitySearch(searchTerm):
    m = re.match(r'#(\d+)\((.*?),(.*?)\)', searchTerm)
    dis = int(m.group(1))
    word1 = m.group(2).strip()
    word2 = m.group(3).strip()

    searchTermPro = word1 + ' AND ' + word2
    bothExistList = booleanSearch(searchTermPro)
    result = []
    word1 = preprocess(word1)[0]
    word2 = preprocess(word2)[0]

    for textID in bothExistList:
        flag = False
        indexList1 = indexdic[word1][textID]
        indexList2 = indexdic[word2][textID]
        for i in indexList1:
            for j in indexList2:
                if -dis<=(i-j)<=dis:
                    flag = True
        if flag:
            result.append(textID)
    return result

indexfile = path + '/index.txt'
indexdic = loadIndex(indexfile)

# get all the documents
allDoc = []
for word in indexdic:
    for doc in indexdic[word]:
        if doc not in allDoc:
            allDoc.append(doc)

with open(path+'/CW1collection/queries.boolean.txt') as f:
    for query in f:
        queryID, query = query.split(' ',1)
        query = query.strip()

        if "#" in query:
            result = proximitySearch(query)
        else:
            result = booleanSearch(query)

        with open(path+'/result/results.boolean.txt', 'a') as f:
            for d in result:
                f.write(str(queryID)+' 0 '+str(d)+' 0 1 0\n')
