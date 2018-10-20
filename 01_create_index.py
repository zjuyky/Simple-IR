import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem.porter import *
import re
from os import path

path = path.dirname(__file__)

def tokenizer(text):
    tokenizer = RegexpTokenizer(r'\w+')
    newtext = tokenizer.tokenize(text.lower())
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


textdic = {}
with open(path+'/CW1collection/trec.5000.txt') as f:
    for line in f:
        if 'ID: ' in line:
            m = re.match(r'ID: (\d+)', line)
            id = m.group(1)
            textdic[id] = []
        else:
            line = line.replace('HEADLINE:', '').replace('TEXT:', '')
            textdic[id].extend(preprocess(line))

indexdic = {}
for id in textdic:
    for i, word in enumerate(textdic[id]):
        if word not in indexdic:
            indexdic[word] = {}
        if id not in indexdic[word]:
            indexdic[word][id] = [i+1]
        else:
            indexdic[word][id].append(i+1)

with open(path+'/index.txt', 'w') as f:
    for key in indexdic:
        f.write(key+':\n')
        for id in indexdic[key]:
            f.write('\t'+str(id)+': '+','.join(str(e) for e in indexdic[key][id])+'\n')
        f.write('\n')
