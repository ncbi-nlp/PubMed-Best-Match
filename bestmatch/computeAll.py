#!/usr/bin/env python3
import sys
from features import *
import time


sortedQueries = True
relevantQueries = True
qcat = "simple"
gs = sys.argv[1]
fc = FeatureCalculator()
fc.setup(sortedQueries, relevantQueries, qcat)
queries = fc.queries
qids = fc.qids
target = "../target/pubmed/"+gs+"/L2R_dataset.txt"

try:
    os.remove(target)
except OSError:
    pass

progress = 0
for qid in qids:
    cliProgress(progress, len(qids))
    query = queries[qid]

    # Queries need to be normalized to compute the features
    clean = cleanQuery(query)

    qterms = clean.split()

    # Get results
    pubmed_results,pmscores = getPubMedRes(qid, gs)

    if gs == "logs":
        std_results = getPlainRes(qid, logres_path)
    else:
        std_results = getGoogleRes(qid)

    # Get result numbers
    # gResNb = getResNb("google")
    # pmResNb = getResNb("pubmed")

    # Get article data
    # TODO: Implement some controls when fetching the articles so this doesn't happen
    try:
        articles = fc.getArticles(qid, "pubmed", gs)
    except: pass

    features = []
    # Compute query-level features
    features.append(fc.getTokenNb(clean))
    features.append(fc.getUniQTokenNb(clean))
    features.append(fc.getNonAlphaNum(query))
    features.append(str(len(pubmed_results)))

    # Now for each document
    with open(target, "a") as f:
        for pmid in pubmed_results:

            # D-level features
            try:
                article = articles[pmid]
            except:
                # Skip the document if we don't have this information... This is very rare.
                # print("no article information\n")
                continue
            try:
                title = articles[pmid]["title"]
            except: title = ""
            try:
                abstract = articles[pmid]["abstract"]
            except: abstract = ""
            try:
                year = articles[pmid]["year"]
            except: year = "-1"
            try:
                language = articles[pmid]["language"]
            except: language = "abc"
            # TODO: add MeSH terms
            try:
                mesh = articles[pmid]["mesh"]
            except: mesh = ""
            try:
                issn = articles[pmid]["issn"]
            except: issn = ""

            features.append(fc.getTokenNb(title))
            features.append(fc.getTokenNb(abstract))
            features.append(fc.getSWRatio(title))
            features.append(fc.getSWRatio(abstract))
            features.append(year)
            features.extend(fc.getClicks(pmid))
            features.extend(fc.languageHotEncoding(language))
            try:
                pubTypes = articles[pmid]["pubTypes"]
            except: pubTypes = []
            features.extend(fc.pubTypeHotEncoding(pubTypes))

            # PATCH considering David's proposal
            features.append(fc.getFT(pmid))
            features.extend(fc.getFunding(pmid))
            features.extend(fc.getRank(issn))

            # QD-level features
            matchNumberTitle,qCoverageTitle,avgMatchPosTitle,sumIDFTextFieldTitle = fc.computeTextFeatures(title,qterms)
            matchNumberAbstract,qCoverageAbstract,avgMatchPosAbstract,sumIDFTextFieldAbstract = fc.computeTextFeatures(abstract,qterms)
            matchNumberMeSH,qCoverageMeSH,_,sumIDFTextFieldMeSH = fc.computeTextFeatures(mesh, qterms)
            _,_,_,sumIDFTitleFieldTitle = fc.computeTextFeatures(title,qterms,"title")
            _,_,_,sumIDFAbstractFieldAbstract = fc.computeTextFeatures(abstract,qterms,"abstract")
            features.append(matchNumberTitle)
            features.append(matchNumberAbstract)
            features.append(matchNumberMeSH)
            features.append(qCoverageTitle)
            features.append(qCoverageAbstract)
            features.append(qCoverageMeSH)
            features.append(avgMatchPosTitle)
            features.append(avgMatchPosAbstract)
            features.append(sumIDFTextFieldTitle)
            features.append(sumIDFTextFieldAbstract)
            features.append(sumIDFTitleFieldTitle)
            features.append(sumIDFAbstractFieldAbstract)
            features.append(sumIDFTextFieldMeSH)
            try:
                score = pmscores[pubmed_results.index(pmid)]
            except:
                score = "-1"
                continue
            features.append(score)
            features.extend(fc.getProximityFeature(title+" "+abstract, qterms))

            rel = computeRelevance(pmid, std_results)
            featureStr = str(rel)+" "+qid.replace("qid", "qid:")
            for idx, feature in enumerate(features):
                featureStr += " "+str(idx+1)+":"+str(feature)
            featureStr += " # docid="+pmid+"\n"
            features = features[:4]
            f.write(featureStr)
        progress += 1

print()
