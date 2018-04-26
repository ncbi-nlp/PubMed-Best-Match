'''
Note that fetching articles this way is very inefficient, because we don't want to
overload the servers and there can be errors due to the file size we are fetching.
Ideally, we would rely on a search engine that would retrieve all calculated features
for matching articles.
'''
import sys
from config import *
from bestmatch.utils import getPlainRes
import threading
from queue import Queue
import requests

progress = 0
def getArticle(item, params):
    global progress
    sys.stdout.write("\r{0}/{1}".format(progress, match))
    sys.stdout.flush()
    try:
        data = requests.post("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi", params).text
        with open(articles_path+item, "wb") as f:
            f.write(data.encode('utf-8'))
    except: pass
    progress += 1

def worker():
    while True:
        item = q.get()
        getArticle(item[0], item[1])
        q.task_done()

# Slow down if no API key
threads = 3
if api_key == "":
    threads = 1
    print("No API key was set in the configuration file. Download will be slower to ensure eutils doesn't restrict access to the papers.")
q = Queue()
for i in range(threads):
     t = threading.Thread(target=worker)
     t.daemon = True
     t.start()

print()
print("Downloading...")
match = 0
for item in os.listdir(results_path):
    if not item.startswith('.') and os.path.isfile(os.path.join(results_path, item)):
        with open(results_path+item) as res:
            qid = item.replace(".txt", "")
            pidList = getPlainRes(qid, results_path)
            pubmedIDs = ",".join(pidList)
            if pubmedIDs == "":
                with open(articles_path+qid+".txt", "w") as res:
                    res.write("")
            else:
                if api_key != '':
                    params = {"db": "pubmed", "retmode": "xml", "id":pubmedIDs, "api_key":api_key}
                else:
                    params = {"db": "pubmed", "retmode": "xml", "id":pubmedIDs}
                item = qid+".txt"
                q.put([item,params])
                match += 1

q.join()
print()
