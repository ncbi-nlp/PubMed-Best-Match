# PubMed Best Match
This repository demonstrates how the new Best Match sort order in PubMed works. This is the research code that was implemented in production later on, relying on Solr. The code provided in this repository essentially allows you to:
1. Curate/classify queries: in PubMed, we train only on queries that contain no field or boolean operators, as these are taken care of by the search engine.
2. Fetch the top articles for a query using a TF-IDF like approach
3. Calculate features for each paper retrieved
4. Train a model based on the feature calculation
5. Evaluate the model
6. Convert the XML model to a JSON format (for Solr, see below)

As a result, this exposes the offline research for developing the new Best Match algorithm and model computation. For a live implementation, we recommend to take a look at [Solr](https://github.com/apache/lucene-solr) and its [ltr](https://github.com/apache/lucene-solr/tree/master/solr/contrib/ltr) plugin.
