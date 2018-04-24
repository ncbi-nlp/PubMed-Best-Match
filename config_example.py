# An API key is needed to go over 3 request/sec to fetch articles
# https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/
api_key = ""

# Solr config, if solrInterface.py is used
solr_ip = "0.0.0.0:8983"
order = "relevance" # date or relevance
nbres = 500 # Fetch how many results
topn = 50 # How many items from the GS are considered

# Several path setups - modification is not recommended
import sys, os
from os.path import join
root = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(root, "data/")
gs_path = os.path.join(data_path, "gold_standard/")
results_path = os.path.join(data_path, "results/")
articles_path = os.path.join(data_path, "articles/")
dataset_path = os.path.join(data_path, "training/")
