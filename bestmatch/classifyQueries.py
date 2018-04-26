#!/usr/bin/env python3
import json
import os, sys

base_path = os.path.dirname(os.path.abspath(__file__))+"/../data/queries/"
sorted_path = base_path + "sorted/"

# Defines the query type according to very simple rules
def query_type(q):
    q = q.strip().casefold()
    if '*' in q:
        return 'REGEX'
    if '[' in q and ']' in q:
        return 'FIELD'
    if q.startswith(('"', "'", "('", '("')):
        return 'PHRASE'
    qtokens = q.split()
    if 'and' in qtokens or 'or' in qtokens or 'not' in qtokens:
        return 'BOOLEAN'
    return 'SIMPLE'

# Query classification
print("Classifying queries...")
regex_nb = 0
field_nb = 0
phrase_nb = 0
boolean_nb = 0
simple_nb = 0
with open(base_path+"queries.txt", encoding='utf8') as f, \
     open(sorted_path+"regex_queries.txt", "w", encoding='utf8') as regex_file, \
     open(sorted_path+"field_queries.txt", "w", encoding='utf8') as field_file, \
     open(sorted_path+"phrase_queries.txt", "w", encoding='utf8') as phrase_file, \
     open(sorted_path+"boolean_queries.txt", "w", encoding='utf8') as boolean_file, \
     open(sorted_path+"simple_queries.txt", "w", encoding='utf8') as simple_file:
    for line in f:
        (key, val) = line.split("|")
        qtype = query_type(val)
        if qtype == "REGEX":
            regex_file.write(key+"|"+val.strip()+"\n")
            regex_nb += 1
        elif qtype == "FIELD":
            field_file.write(key+"|"+val.strip()+"\n")
            field_nb += 1
        elif qtype == "PHRASE":
            phrase_file.write(key+"|"+val.strip()+"\n")
            phrase_nb += 1
        elif qtype == "BOOLEAN":
            boolean_file.write(key+"|"+val.strip()+"\n")
            boolean_nb += 1
        else:
            simple_file.write(key+"|"+val.strip()+"\n")
            simple_nb += 1

print(str(regex_nb)+" queries contained regular expressions.")
print(str(field_nb)+" queries contained fields (e.g. [author]).")
print(str(phrase_nb)+" queries contained quoted phrases.")
print(str(boolean_nb)+" queries contained Boolean expressions.")
print(str(simple_nb)+" queries were classified as 'simple'. These will be used for training the model.")
