from config import *
import regex as re
import urllib.parse
import requests
from xml.etree import ElementTree
import math
import collections

def flatten(l):
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el

def loadQueries(q_path):
    queries = {}
    with open(q_path) as f:
        for line in f:
           (key, val) = line.split("|")
           queries[key] = val.strip().casefold()
    qids = sorted(queries)
    return queries,qids

def cleanQuery(query):
    cleanQuery = query.replace('"', " ") # Remove all quotes
    cleanQuery = re.sub(r"[^\P{P}-]+", " ", cleanQuery).replace("-"," ") # Remove punctuation
    cleanQuery = ' '.join(cleanQuery.split())
    return cleanQuery

def getPlainRes(qid, path):
    plainRes = []
    with open(path+qid+".txt") as f:
        for line in f:
            plainRes.append(line.strip())
    return plainRes

def computeRelevance(pmid, gold):
    if pmid in gold:
        index = gold.index(pmid)
        if index < 10:
            rel = 12 - index
        elif index <= 20:
            rel = 2
        else:
            rel = 1
    else:
        rel = 0
    return str(rel)

def createSplits(dataset):
    # First count the queries
    qid = ""
    total_queries = 0
    with open(dataset) as f:
        for line in f:
            cur_qid = line.split(" ")[1]
            if cur_qid != qid:
                total_queries += 1
                qid = cur_qid

    # Then actually write the files
    qid = ""
    cur_queries = 0
    with open(dataset) as f, \
         open(dataset_path+"train.txt", "w") as ftrain, \
         open(dataset_path+"val.txt", "w") as fval, \
         open(dataset_path+"test.txt", "w") as ftest:
        for line in f:
            cur_qid = line.split(" ")[1]
            if cur_qid != qid:
                cur_queries += 1
                qid = cur_qid
                if cur_queries/total_queries < train_split:
                    cur_file = ftrain
                elif cur_queries/total_queries < train_split+validation_split:
                    cur_file = fval
                else:
                    cur_file = ftest
            cur_file.write(line)
