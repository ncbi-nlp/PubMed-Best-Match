# PubMed Best Match
This repository demonstrates how the new Best Match sort order in PubMed works. This is the research code that was implemented in production later on, relying on Solr. The code provided in this repository essentially allows you to:
1. *Curate/classify queries* in PubMed, we train only on queries that contain no field or boolean operators, as these are taken care of by the search engine.
2. *Identify the top articles* for a query using a TF-IDF like approach. A sample dataset is provided to simulate this fetching. A real-world approach would need you to have a search engine to retrieve the documents and their search engine-related features (BM25 score, sum of IDFs, etc.).
3. *Calculate features* for each paper retrieved. Search engine features are precalculated in the sample data.
4. *Train a model* based on the feature calculation.
5. *Evaluate* approaches.
6. *Convert the XML model* to a JSON format (for Solr, see below).

As a result, this exposes the offline research for developing the new Best Match algorithm and model computation. For a live implementation, we recommend to take a look at [Solr](https://github.com/apache/lucene-solr) and its [LTR](https://github.com/apache/lucene-solr/tree/master/solr/contrib/ltr) plugin.

## Setup
A full solution consists of an information retrieval system to fetch articles matching the query and an implementation of LambdaMART to rerank the results. While this repository focuses on training a ranking model as implemented in the Best Match sort order of PubMed, we provide sample data to simulate the fetching steps.

### Prerequisites
Everything has been tested on OSX. Unix should work well too, but the install might run into some problems on Windows. If this is the case, you will not be able to run the commands but, of course, you will be able to run the Python scripts – assuming it is installed. The code enforces the use of Python 3.4+ as it has not been tested on earlier versions. `pip` will be needed to install the dependencies too.

### Installation
In order to setup the environment, please run the following commands. First, you need to download the repository, either from GitHub or via Git (if installed):
```
git clone https://github.com/ncbi-nlp/PubMed-Best-Match.git
```

Then, you will need to install the module. This will take care of installing all dependencies and allow you to run commands for an easy access to generating data and training on queries. You may want to [create a virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtualenv/) for this project:
```
cd PubMed-Best-Match
python3 -m virtualenv env
source env/bin/activate
pip install -e .
```

### Configuration
The `config_example.py` file at the root of the folder allows you to tweak various parameters. You will need to rename it to `config.py` whether or not you want to update it:
```
mv config_example.py config.py
```

#### api_key
An API key is needed in order to allows a higher throughput when downloading articles. [More information here.](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/)

#### Splits
By default, 65% of queries are use for training, 15% for validating and 20% for testing. Please make sure that these numbers add up to 1 as there is no further check in the code.

#### RankLib parameter
RankLib is a Java library used in various step of this project. The corresponding settings set the minimum and maximum memory used by RankLib, as well as the optimization metric for learning (and evaluating).

#### Solr parameters
This repository proposes a Solr interface (`bestmatch/solrInterface.py`) that allows one to plug Solr in this pipeline in lieu of simulated data. This section in the configuration file sets some parameters specific to Solr. None of them are useful if the simulated data are used.

#### Additional parameters
Finally, there are some path definitions. We recommend not to touch them unless you know what you are doing.

## Usage
Once installed, you will be provided with a handy set of commands. Please **run the commands in this specific order** (from top to bottom), since some depend on each other.
```python
Usage:
    pbm load
    pbm classify
    pbm fetch
    pbm calculate
    pbm train
    pbm evaluate (before|after)
    pbm export
```

### pbm load
This command will download some data. This includes the PMCID-PMIC mapping file to identify which articles have a full text available and [RankLib](https://sourceforge.net/p/lemur/wiki/RankLib/), a very useful Java library that implements many learning-to-rank algorithms.

### pbm classify
A sample dataset is provided in this repository, from a [previously published day of logs](https://ftp.ncbi.nlm.nih.gov/pub/wilbur/DAYSLOG). This classification step aims at roughly filtering queries that are relevant for training. Essentially, we want to discard queries with fields, regular expressions or boolean operations. The remaining set is the one used for training, since the other categories of queries are better handled by the search engine.

### pbm fetch
Once the queries are curated, we need to fetch the corresponding articles in XML format (in `data/articles`) according to the sample dataset results (in `data/results`). We use eutils for this process and there are some limitations. By default, only 3 requests per second can be performed, but by generating an API key and entering it in the config file (see above), 10rps are allowed. [More information here.](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/)

### pbm calculate
The next step is to calculate the features for each document for each query. This will generate a `data/training/dataset.txt` file which will then be split according to the train/validation/test split entered in the configuration file. Please note that feature calculation can take some time as-is. This was a research project and further optimizations were then made on Solr's end.

### pbm train
This command will allow you to train on the training set, validate on the validation set and test on the test set defined above. the output of the RankLib library in this process will be output. Note that because of the small amount of data, the training will tend to overfit. Still, there is a three-fold (0.1821 to 0.5225) improvement on unseen data (the test set) that proves the pipeline's ability to learn and generalize relevance.

### pbm evaluate (before|after)
Either `before` or `after` must be entered for this command. `before` will evaluate the test set before reranking, i.e. based on BM25 results. `after` will evaluate the test set after reranking using the trained model in the previous step. The NDCG@t value is provided for both, where t can be defined in the configuration file.

### pbm export
If you are using Solr and you need to add the calculated model for its LTR plugin, use this command. This will create a `data/training/model.json` file that will be compatible with Solr's LTR functions. This command essentially parses the model created from RankLib and translate it in Solr's format.

## More detailed analysis
We refer you to the documentation in this repository for additional data and conclusions drawn from them. It includes additional tables, explanations and some figures.

#### Disclaimer
The gold standard dataset used in this repository serves only to show how learning-to-rank converges better towards an effective relevance model. It is not derived from PubMed logs, it is artificial and computationally generated.
