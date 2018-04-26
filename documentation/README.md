## Additional documentation

This folder provides a lot more information on various experiments conducted on the pipeline. Particularly, since we cannot share the set of queries used for training L2R for PubMed, we provide here more details regarding the queries, their distribution, their click-through rates, etc. We also evaluated various first layers besides BM25 and we report the results of these experiments.

### First layer
Our choice of using BM25 is not arbitrary. It is justified by some internal experiments we conducted which led to the same conclusions as in the past literature (e.b. Managing Gigabytes: Compressing and Indexing Documents and Images by Witten I, Moffat A, and Bell TC. 1999). Our experiments used Divergence from randomness (Amati et al. 2002) as a competitor for BM25. However, given the very high number of results we fetch for reranking (500), there is not much difference between this approach and BM25. We also studied how a combination of them, following (Fox and Shaw, 1994) especially the COMBSUM combination, would perform. The results are displayed in the table below.

| Evaluation         | BM25 | DfR - I(ne)L2 | BM25 & DfR (using the COMBSUM junction) |
| -------------      | ------------| ---         | ---         |
| Precision@500      | 0.037 | 0.037 | 0.036 |
| Recall@500         | 0.445 | 0.447 | 0.444 |
| NDCG@20            | 0.151 | 0.151 | 0.151 |
| NDCG@20 after L2R  | **0.483** | **0.483** | 0.481 |

As can be seen, the true value lies in the addition of L2R. The ranking quality of the top 20 results improves dramatically by a factor of 3.

### Query analysis
We provide in this section further information regarding the queries. Particularly, we focus on their popularity distribution, the CTR associated to this distribution, the NDCG distributions and the improvement or deterioration brought by L2R.

#### Query occurrences
Some PubMed queries are very popular, however, they only represent a very small fraction of total queries. The figures below depict the volume of queries in PubMed based on how many times they occur in a year, with a focus on queries occurring one to ten times. As can be seen, 87.3% of queries are unique in PubMed, and 98.8% of queries occur less than 10 times in a year.

![Query_occurrence_distribution](https://raw.githubusercontent.com/ncbi-nlp/PubMed-Best-Match/master/images/Query_occurrence_distribution.png =250x)
![Query_occurrence_distribution_1-10](https://raw.githubusercontent.com/ncbi-nlp/PubMed-Best-Match/master/images/Query_occurrence_distribution_1-10.png =250x)

#### CTR per occurrence number
The set of 46,000 queries we used for training in PubMed contains unique queries only (i.e. duplicates are removed). The figures below depict the average CTR@20 (click through rate below the 20th document for a query) observed with respect to different query popularities, with a focus on the 10 first. It clearly looks like unique queries are driving the overall CTR@20 of 0.4 observed.

![Query_occurrence_CTR](https://raw.githubusercontent.com/ncbi-nlp/PubMed-Best-Match/master/images/Query_occurrence_CTR.png =250x)
![Query_occurrence_CTR_1-10](https://raw.githubusercontent.com/ncbi-nlp/PubMed-Best-Match/master/images/Query_occurrence_CTR_1-10.png =250x)

#### NDCG distribution
The histogram below shows the NDCG distribution for the test dataset. While BM25 yields a skewed distribution (with many queries close to NDCG@20=0), L2R provides a more homogeneous distribution which explains its overall quality.

[[https://github.com/ncbi-nlp/PubMed-Best-Match/blob/master/documentation/images/BM25_L2R_distributions.png]]

#### NDCG improvement/deterioration
The density curve below shows the proportion of queries in the test set for which the results deteriorated after adding L2R (below 0) and the proportion for which the results improved after L2R's addition. As can be seen (and the numbers at the top help), the area under the curve is higher in the improvement side.

![BM25_L2R_improvement](https://raw.githubusercontent.com/ncbi-nlp/PubMed-Best-Match/master/images/BM25_L2R_improvement.png=500x)
