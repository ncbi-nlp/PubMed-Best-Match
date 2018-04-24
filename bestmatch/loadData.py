from config import *
import urllib.request
import requests
import gzip

'''
Download the PMCID references
Then unzip it and parse it for lower storage and easier access
'''
print("Loading PMCID-PMID correspondence")
print("    Downloading...")
urllib.request.urlretrieve('ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/PMC-ids.csv.gz', data_path+"pmcid.gz")
print("    Unzipping...")
pmids = []
with gzip.open(data_path+"pmcid.gz", 'rt') as f:
    next(f) # Skip headers
    for line in f:
        pmids.append(line.split(",")[9])
print("    Cleaning up...")
with open(data_path+"FT.txt", "w") as f:
    for pmid in pmids:
        f.write(pmid+"\n")
try:
    os.remove(data_path+"pmcid.gz")
except OSError:
    pass
print("Done.\n")

'''
Download the latest version of RankLib
'''
print("Loading RankLib")
print("    Downloading...")
url = 'https://sourceforge.net/projects/lemur/files/lemur/RankLib-2.9/RankLib-2.9.jar/download'
r = requests.get(url, allow_redirects=True)
with open(data_path+"/RankLib.jar", 'wb') as f:
    f.write(r.content)
print("Done.\n")
