"""
Defines the computation of features
Requires Python3.4+ and a few packages described below
"""
from bestmatch.utils import *
from itertools import chain

class FeatureCalculator() :

    ######################################################################
    # SETUP PART
    ######################################################################
    def __init__(self):
        """
        Definition of some paths.
        This shouldn't be modified
        """
        self.q_path = ""
        self.FT_path = os.path.join(data_path, "FT.txt")
        self.synonyms_path = os.path.join(data_path, "synonyms.txt")
        self.textIDF_path = os.path.join(data_path, "IDFs/tiab.txt")
        self.titleIDF_path = os.path.join(data_path, "IDFs/title.txt")
        self.abstractIDF_path = os.path.join(data_path, "IDFs/abstract.txt")
        self.BM25_path = os.path.join(data_path, "BM25.json")

        """
        Other important definitions
        Stopwords could be better but this is only for the sake of the example
        """
        self.stopwords = ["a","about","above","after","again","against","all","am","an","and","any","are","aren't","as","at","be","because","been","before","being","below","between","both","but","by","can't","cannot","could","couldn't","did","didn't","do","does","doesn't","doing","don't","down","during","each","few","for","from","further","had","hadn't","has","hasn't","have","haven't","having","he","he'd","he'll","he's","her","here","here's","hers","herself","him","himself","his","how","how's","i","i'd","i'll","i'm","i've","if","in","into","is","isn't","it","it's","its","itself","let's","me","more","most","mustn't","my","myself","no","nor","not","of","off","on","once","only","or","other","ought","our","ours	ourselves","out","over","own","same","shan't","she","she'd","she'll","she's","should","shouldn't","so","some","such","than","that","that's","the","their","theirs","them","themselves","then","there","there's","these","they","they'd","they'll","they're","they've","this","those","through","to","too","under","until","up","very","was","wasn't","we","we'd","we'll","we're","we've","were","weren't","what","what's","when","when's","where","where's","which","while","who","who's","whom","why","why's","with","won't","would","wouldn't","you","you'd","you'll","you're","you've","your","yours","yourself","yourselves"]
        self.languages = ["afr","alb","amh","ara","arm","aze","ben","bos","bul","cat","chi","cze","dan","dut","eng","epo","est","fin","fre","geo","ger","gla","gre","heb","hin","hrv","hun","ice","ind","ita","jpn","kin","kor","lat","lav","lit","mac","mal","mao","may","mul","nor","per","pol","por","pus","rum","rus","san","slo","slv","spa","srp","swe","tha","tur","ukr","und","urd","vie","wel"]
        self.pubTypes = ["Addresses","Autobiography","Bibliography","Biography","Case Reports","Classical Article","Clinical Conference","Clinical Study","Clinical Trial","Clinical Trial, Phase I","Clinical Trial, Phase II","Clinical Trial, Phase III","Clinical Trial, Phase IV","Collected Works","Comment","Comparative Study","Congresses","Consensus Development Conference","Consensus Development Conference, NIH","Controlled Clinical Trial","Corrected and Republished Article","Dataset","Dictionary","Directory","Duplicate Publication","Editorial","English Abstract","Evaluation Studies","Festschrift","Government Publications","Guideline","Historical Article","Interactive Tutorial","Interview","Introductory Journal Article","Journal Article","Lectures","Legal Cases","Legislation","Letter","Meta-Analysis","Multicenter Study","News","Newspaper Article","Observational Study","Overall","Patient Education Handout","Periodical Index","Personal Narratives","Portraits","Practice Guideline","Pragmatic Clinical Trial","Publication Components","Publication Formats","Publication Type Category","Published Erratum","Randomized Controlled Trial","Research Support, American Recovery and Reinvestment Act","Research Support, N.I.H., Extramural","Research Support, N.I.H., Intramural","Research Support, Non-U.S. Gov't","Research Support, U.S. Gov't, P.H.S.","Retracted Publication","Retraction of Publication","Review","Scientific Integrity Review","Study Characteristics","Support of Research","Technical Report","Twin Study","Validation Studies","Video-Audio Media","Webcasts","book"]

    def setup(self, sortedQueries, relevantQueries, qcat="none", dataset="logs"):
        """
        Some variables that need to be stored/updated
        so that they're computed only once and can be fetched afterward
        """
        self.q_path = data_path + "queries/" + ("sorted/" if sortedQueries else "queries_"+dataset+".txt") + ("relevant/" if relevantQueries and sortedQueries else "") + (qcat+"_queries.txt" if sortedQueries else "")
        self.queries,self.qids = loadQueries(self.q_path)
        self.loadWordPairs()
        self.loadIDFs()
        self.loadIDFs("title")
        self.loadIDFs("abstract")
        self.loadSolr()
    ######################################################################
    # EOF SETUP
    ######################################################################

    ######################################################################
    # VARIOUS LOADING FUNCTIONS
    ######################################################################
    '''
    If Solr is to be used, which isn't the case in the example repository.
    '''
    def loadSolr(self):
        self.s = requests.Session()

    '''
    This is a synonym sample, it is a lot richer in reality
    '''
    def loadWordPairs(self):
       self.synonyms = {}
       with open(self.synonyms_path) as f:
           for line in f:
                pair = line.strip()
                if pair[0] in self.synonyms:
                    self.synonyms[pair[0]].append(pair[1])
                else:
                    self.synonyms[pair[0]] = [pair[1]]

    def loadIDFs(self, src = "text"):
        if src == "title":
            p = self.titleIDF_path
        elif src == "abstract":
            p = self.abstractIDF_path
        else:
            p = self.textIDF_path
        IDFs = {}
        try:
            with open(p) as f:
                for line in f:
                   term, idf = line.split()
                   IDFs[term] = float(idf)
            if src == "title":
                global qIDFsT
                self.qIDFsT = IDFs
            elif src == "abstract":
                global qIDFsA
                self.qIDFsA = IDFs
            else:
                global qIDFs
                self.qIDFs = IDFs
        except: pass

    '''
    Transforms XML articles to a python manageable object.
    '''
    def getArticles(self, qid):
        self.articles = {}
        with open(articles_path+qid+".txt", "rb") as f:
            xmldata = f.read().decode("utf8")
        if len(xmldata) > 0:
            try:
                PubmedArticleSet = ElementTree.fromstring(xmldata)
                resnb = 0
                for PubmedArticle in PubmedArticleSet:
                    year = month = day = "0"
                    pubs = []
                    mesh = ""
                    if PubmedArticle.find("MedlineCitation"):
                        citation = PubmedArticle.find('MedlineCitation')
                        cpmid = citation.find('PMID').text.encode('ascii', 'ignore').decode('ascii')
                        if citation.find("DateCompleted").findall('Year'):
                            year = str(citation.find("DateCompleted").findall('Year')[0].text)
                        article = citation.find('Article')
                        title = article.find('ArticleTitle').text.encode('ascii', 'ignore').decode('ascii')
                        abstracts = article.find('Abstract')
                        language = article.find('Language').text.encode('ascii', 'ignore').decode('ascii')
                        types = article.find("PublicationTypeList")
                        try:
                            issn = citation.find('.//ISSNLinking').text
                        except: issn = ""
                        try:
                            for typ in types:
                                pubs.append(typ.text.encode('ascii', 'ignore').decode('ascii'))
                        except:
                            pass
                        meshHeadings = citation.find("MeshHeadingList")
                        try:
                            for meshHeading in meshHeadings:
                                for descriptorName in meshHeading:
                                    mesh += " "+descriptorName.text.encode('ascii', 'ignore').decode('ascii').replace("*", "")
                        except:
                            pass
                    elif PubmedArticle.find("BookDocument"):
                        bookdoc = PubmedArticle.find('BookDocument')
                        cpmid = bookdoc.find('PMID').text.encode('ascii', 'ignore').decode('ascii')
                        article = bookdoc.find('Book')
                        try:
                            issn = bookdoc.find('.//ISSNLinking')
                        except: issn = ""
                        if not article == None and article.find("PubDate"):
                            if article.find("PubDate").findall("Year"):
                                year = str(article.find("PubDate").findall("Year")[0].text)
                        title = article.find('BookTitle').text.encode('ascii', 'ignore').decode('ascii')
                        abstracts = bookdoc.find('Abstract')
                        language = bookdoc.find('Language').text.encode('ascii', 'ignore').decode('ascii')
                        pubs.append("book")
                    abstract = ""
                    try:
                        for a in abstracts:
                            if a.tag == "AbstractText":
                                abstract += " "+a.text.encode('ascii', 'ignore').decode('ascii')
                    except:
                        pass
                    abstract = abstract.strip().replace("  "," ")
                    title = re.sub(r"[^\P{P}-]+", "", title).replace("-"," ")
                    abstract = re.sub(r"[^\P{P}-]+", "", abstract).replace("-"," ")
                    mesh = re.sub(r"[^\P{P}-]+", "", mesh).replace("-"," ")
                    self.articles[cpmid] = {"title":title.casefold(), "abstract":abstract.casefold(),"year":year, "pubTypes":pubs, "language":language, "mesh":mesh.casefold(), "issn": issn}

            except Exception as e:
                # exc_type, exc_obj, exc_tb = sys.exc_info()
                # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                # print(e,exc_type, fname, exc_tb.tb_lineno)
                # print("ERROR with qid "+qid+", PMID " + cpmid)
                pass
    ######################################################################
    # EOF LOADING FUNCTIONS
    ######################################################################

    ######################################################################
    # FEATURE CALCULATION
    ######################################################################
    '''
    Function calculating all features in an order similar to that in the paper
    Some features are unavailable (e.g. click data due to privacy reasons) or
    simulated (because a real search engine would be needed). Still, this
    framework allows to reproduce the experiments with meaningful features.
    '''
    def computeFeatures(self, query, pmid):
        try:
            article = self.articles[pmid]
            title = article["title"]
            abstract = article["abstract"]
            F1 = article["year"]
            F2_3 = self.getFT(pmid) # Click information is not available, replaced with FT availability
            F4_77 = self.pubTypeHotEncoding(article["pubTypes"])
            F78 = self.getTokenNb(title)
            F79 = self.getTokenNb(abstract)
            F80_140 = self.languageHotEncoding(article["language"])
            F141 = self.getSWRatio(title)
            F142 = self.getSWRatio(abstract)
            F143 = 0 #self.getBM25(pmid)
            queryTerms = cleanQuery(query).split(" ")
            F168, F144, F147, F171 = self.computeTextFeatures(title, queryTerms)
            F169, F145, F148, F173 = self.computeTextFeatures(abstract, queryTerms, "abstract")
            F170, F146, _, F175 = self.computeTextFeatures(title+" "+abstract, queryTerms, "tiab") # MeSH is replaced by title+abstract here
            F149_167 = self.getProximityFeature(title+" "+abstract, queryTerms)
            F176 = 0 # Number of results isn't available in this example
            F177 = self.getNonAlphaNum(query)
            F178 = self.getTokenNb(query)
            F179 = self.getUniQTokenNb(query)
            features = [F1, F2_3, F4_77, F78, F79, F80_140, F141, F142, F143, F144, F145, F146, F147, F148, F149_167, F168, F169, F170, F171, F173, F175, F176, F177, F178, F179]
            flattened = flatten(features)
            return flattened
        except: return [] # If some articles fail to be retrieved

    # Number of tokens
    def getTokenNb(self, text):
        return str(len(text.split()))

    # Number of unique terms
    def getUniQTokenNb(self, text):
        return str(len(set(text.split())))

    # Number of non-alphanumeric chars
    def getNonAlphaNum(self, text):
        return str(sum(not c.isalnum() for c in text.replace(" ", "")))

    """
    Computes several values given a text and query terms:
    - the number of matches
    - the query coverage
    - the average position of query terms in the text
    - the sum of DF values of matches
    """
    def computeTextFeatures(self, text, terms, source="title"):
        if source == "abstract":
            IDFSet = self.qIDFsA
        elif source == "tiab":
            IDFSet = self.qIDFs
        else:
            IDFSet = self.qIDFsT
        extTerms = self.getExtendedTerms(terms)
        syns = extTerms.keys()
        msum = 0
        matches = set()
        avgPos = 0
        tokens = text.split()
        pos = 0
        IDFSum = 0
        for tk in tokens:
            for t in set(syns):
                if tk == t:
                    msum += 1
                    matches.add(extTerms[t])
                    avgPos += pos
                    try:
                        IDFSum += IDFSet[t]
                    except:
                        pass
            pos += 1
        cov = len(matches)/len(set(terms))
        if msum > 0:
            avgPos /= msum
        else:
            avgPos = -1
        return str(msum),str(cov),str(round(avgPos,3)),str(IDFSum)

    # Stopword ratio in text
    def getSWRatio(self, text):
        tokens = text.split()
        swFreeTokens = [word for word in tokens if word not in self.stopwords]
        try:
            swRatio = (len(tokens)-len(swFreeTokens))/len(tokens)
        except:
            swRatio = 0
        return str(round(swRatio,5))

    def getProximityFeature(self, text,terms):
        # Extend the terms...
        qterms = self.getExtendedTerms(terms)
        syns = qterms.keys()

        # More elaborated proximity features
        # Step 1, get the tokens
        tsplit = text.split()

        # Step 2, find the matches
        matches = []
        pos = 0
        for word in tsplit:
            if word in syns:
                matches.append(pos)
            pos += 1

        # Step 3, get spans out of the matching positions
        th = 10
        spans = []
        lastMatch = ""
        lastPos = -1
        lastLastMatch = ""
        lastLastpos = -1
        begin = -1
        for i in range(len(matches)):
            pos = matches[i]
            match = qterms[tsplit[pos]]

            # If this is the first match
            if begin == -1:
                begin = pos
                lastPos = pos
                lastLastpos = pos

            # When X...X, end the span at the last match
            # X|X
            # No match for too long, close the span
            # When X........., then X|
            if match == lastMatch or pos-lastPos > th:
                spans.append([begin,lastPos])
                begin = pos
                lastMatch = ""
                lastLastMatch = ""

            # When X...Y...X, split on the largest distance
            # When X........Y..X, X|YX
            #     llp      lp  m
            if match == lastLastMatch and (len(spans) == 0 or lastLastPos not in spans[len(spans)-1]):
                dist1 = pos-lastPos
                dist2 = lastPos-lastLastPos
                if dist1 <= dist2:
                    spans.append([begin,lastLastPos])
                    begin = lastPos
                else:
                    spans.append([begin,lastPos])
                    begin = pos

            # Update lastMatch and lastLastMatch
            lastLastMatch = lastMatch
            lastMatch = match
            lastLastPos = lastPos
            lastPos = pos
        # add the one that was being built
        if begin != -1:
            spans.append([begin,lastPos])

        # Step 4, compute the features
        feats = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        maxLen = 0
        maxqtnum = 0
        maxdensity = 0
        maxDensityLen = 0
        maxLenDensity = 0
        for span in spans:
            # Span is only 1 qterm long (begin = end)
            if span[0] == span[1]:
                spansp = [tsplit[span[0]]]
                spanLength = th
            # Or normal
            else:
                spansp = tsplit[span[0]:span[1]+1]
                spanLength = span[1]-span[0]+1

            qtnum = 0
            indefinitenb = 0
            definitenb = 0
            stopwordnb = 0

            for sp in spansp:
                if sp in syns:
                    qtnum += 1
                if sp == "a" or sp == "an":
                    indefinitenb += 1
                if sp == "the":
                    definitenb += 1
                if sp in self.stopwords:
                    stopwordnb += 1
            if qtnum > 1:
                feats[0] += 1
            if qtnum > 3:
                feats[1] += 1
            feats[2] += spanLength # Sum of span lengths, either th or the length
            feats[3] += qtnum # Sum of qt in spans
            try:
                density = qtnum/spanLength
                feats[4] += density # Sum of span densities
            except:
                feats[4] = 0
            feats[5] += indefinitenb # Sum of indefinite articles
            feats[6] += definitenb # Sum of definite articles
            feats[7] += stopwordnb # Sum of stopwords
            if len(spansp) == stopwordnb:
                feats[8] += 1 # Sum of (isOnlyStopwords(qt))
            try:
                feats[9] += (qtnum*qtnum*qtnum)/spanLength # Sum of relevance contributions
            except:
                feats[9] = 0
            if spanLength > maxLen:
                maxLen = spanLength
                maxLenDensity = feats[4]
            if qtnum > maxqtnum:
                maxqtnum = qtnum
            if density > maxdensity:
                maxdensity = density
                maxDensityLen = spanLength
        feats[10] = len(spans)
        feats[11] = maxLen
        try:
            feats[12] = feats[2]/len(spans)
        except:
            feats[12] = 0
        feats[13] = maxqtnum
        try:
            feats[14] = feats[3]/len(spans)
        except:
            feats[14] = 0
        feats[15] = maxdensity
        try:
            feats[16] = feats[4]/len(spans)
        except:
            feats[16] = 0
        feats[17] = maxDensityLen
        feats[18] = maxLenDensity
        return feats

    def getExtendedTerms(self, terms):
        # Compute extended terms, including synonyms
        extTerms = {}
        for term in terms:
            if term in self.synonyms:
                syns = self.synonyms[term]
                for syn in syns:
                    extTerms[syn] = term
            extTerms[term] = term
        return extTerms

    def languageHotEncoding(self, lang):
        hotenc = [0] * 61
        try:
            index = self.languages.index(lang)
            hotenc[index] = 1
        except: pass
        return hotenc

    def pubTypeHotEncoding(self, pts):
        hotenc = [0] * 74
        for t in pts:
            try:
                index = self.pubTypes.index(t)
                hotenc[index] = 1
            except: pass
        return hotenc

    # FT availability
    def loadFT(self):
        self.FT = set()
        with open(self.FT_path) as f:
            for line in f:
                self.FT.add(line.strip())

    def getFT(self, d):
        if not hasattr(self, "FT"):
            self.loadFT()
        if d in self.FT:
            return 1
        else: return 0
