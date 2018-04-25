#!/usr/bin/env python3
from config import *
from bestmatch.features import *
from bestmatch.utils import cliProgress

fc = FeatureCalculator()
fc.setup(True, False, "simple")
queries = fc.queries
qids = fc.qids

def createEntries(qid):
    query = queries[qid]

    # Load results
    srres = getPlainRes(qid, results_path)
    # Load gold standard
    gsres = getPlainRes(qid, gs_path)

    '''
    In order to be eligible for training, queries need to fulfill some requirements:
        - they need to yield at least 20 results
        - In the 500 (at most) items returned, at least 5 need to be in the top 10 of the gold standard
    '''
    if len(srres) > 20 and len(gsres) > 0:
        topten = 0
        for sr in srres:
            if sr in gsres:
                index = gsres.index(sr)
                if index < 10:
                    topten += 1
        # Check that at least 5 are in the GS top 10
        if topten > 4:
            fc.getArticles(qid) # Locally stores the articles for this query in a python object
            lines = ""
            # Compute each line for the dataset
            for sr in srres:
                rel = computeRelevance(sr, gsres) # Relevance score
                lines += str(rel) + " " + qid.replace("qid", "qid:") + " "
                features = fc.computeFeatures(query, sr) # Feature calculation
                fi = 1
                for feature in features:
                    if feature != 0:
                        lines += str(fi)+":"+str(feature)+" "
                    fi += 1
                lines += "#docid=" + sr + "\n"
            with open(dataset_path+"dataset.txt", "a") as f:
                f.write(lines)

# TODO: add processing information
try:
    os.remove(dataset_path+"dataset.txt")
except OSError:
    pass
print("Calculating features...")
i = 0
for qid in qids:
    createEntries(qid)
    cliProgress(i, len(qids))
    i += 1

# Now creating splits
createSplits(dataset_path+"dataset.txt")
