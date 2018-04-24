#!/usr/bin/env python3
from config import *
from bestmatch.features import *
import threading
from queue import Queue

try:
    os.remove(dataset_path+"train.txt")
    os.remove(dataset_path+"val.txt")
    os.remove(dataset_path+"test.txt")
except OSError:
    pass

fc = FeatureCalculator()
fc.setup(True, False, "simple")
queries = fc.queries
qids = fc.qids

progress = 0
def getResults(qid):
    global progress

    sys.stdout.write("\r{0}".format(progress))
    sys.stdout.flush()

    query = queries[qid]

    # Order selection
    sortParam = ""
    if order == "date":
        sortParam = "&sort=presort+desc"

    '''
    Solr query
        - fl: All features should be calculated at the search engine level and can be returned
        - rq: https://lucene.apache.org/solr/guide/7_0/learning-to-rank.html
    '''
    ssearchurl = solr_ip+"select?rows="+str(nbres)+"&fl=id,[features]&wt=json&rq=&q="+urllib.parse.quote_plus(query)+sortParam
    try:
        data = fc.s.get(ssearchurl).json()
    except:
        print(ssearchurl)
        pass
    srres = []
    srres_feat = {}
    try:
        for item in data['response']['docs']:
            srres.append(str(item['id']))
            srres_feat[str(item['id'])] = item["[features]"]
    except:
        pass

    # Load gold standard
    gsres = getPlainRes(qid, gs_path)[:topn]
    if len(srres) > 20 and len(gsres) > 0:
        topten = 0
        for sr in srres:
            if sr in gsres:
                index = gsres.index(sr)
                if index < 10:
                    topten += 1
        if topten > 4:
            lines = ""
            for sr in srres:
                rel = computeRelevance(sr, gsres)
                lines += str(rel) + " " + qid.replace("qid", "qid:") + " "
                lines += srres_feat[sr].replace(",", " ").replace("=", ":")
                lines += " #docid=" + sr + "\n"
            with open(dataset_path+"dataset.txt", "a") as f:
                f.write(lines)
    progress += 1

def worker():
    while True:
        item = q.get()
        getResults(item)
        q.task_done()

q = Queue()
for i in range(20):
     t = threading.Thread(target=worker)
     t.daemon = True
     t.start()

for qid in qids:
    q.put(qid)
q.join()

createSplits(dataset_path+"dataset.txt")
