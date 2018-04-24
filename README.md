# PubMed Best Match
This repository demonstrates how the new Best Match sort order in PubMed works. This is the research code that was implemented in production later on, relying on Solr. The code provided in this repository essentially allows you to:
1. *Curate/classify queries* in PubMed, we train only on queries that contain no field or boolean operators, as these are taken care of by the search engine.
2. *Identify the top articles* for a query using a TF-IDF like approach. A sample dataset is provided to simulate this fetching. A real-world approach would need you to have a search engine to retrieve the documents and their search engine-related features (BM25 score, sum of IDFs, etc.).
3. *Calculate features* for each paper retrieved. Search engine features are precalculated in the sample data.
4. *Train a model* based on the feature calculation.
5. *Evaluate* approaches.
6. *Convert the XML model* to a JSON format (for Solr, see below).

As a result, this exposes the offline research for developing the new Best Match algorithm and model computation. For a live implementation, we recommend to take a look at [Solr](https://github.com/apache/lucene-solr) and its [ltr](https://github.com/apache/lucene-solr/tree/master/solr/contrib/ltr) plugin.

## Setup
A full solution consists of an information retrieval system to fetch articles matching the query and an implementation of LambdaMART to rerank the results. While this repository focuses on training a ranking model as implemented in the Best Match sort order of PubMed, we provide sample data to simulate the fetching steps.

## Usage
'''
Usage:
    pbm classify
    pbm fetch
'''
Please note that feature calculation can take some time as-is. This was a research project and optimizations were then made on the Solr end.

## Disclaimer
The gold standard dataset used in this repository serves only to show how learning-to-rank converges better towards an effective relevance model. It is not derived from PubMed logs, it is artificial and computationally generated.
