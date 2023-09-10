from __future__ import division
import os, re, string, math, codecs, csv
import nltk   #<---- Need to install this package manually using pip

os.chdir('/Users/alvinzuyinzheng/Dropbox/PythonWorkshop/scripts/') #<===The location of your csv files
corpusSubPath = "./txt/" #<===The subfolder with the extracted text files.
tf_name = "tf.csv"
tfidf_name = "tfidf.csv"

nltk.download("stopwords")
tokenizer = nltk.RegexpTokenizer(r'\w+', flags=re.UNICODE)# "\w" means "any word character"
stopwords = nltk.corpus.stopwords.words('english')
stemmer = nltk.stem.PorterStemmer()

#from nltk.corpus import PlaintextCorpusReader
#from sklearn.feature_extraction.text import TfidfVectorizer



# Input: a string of text
# Output: a {word: frequency} dict
def bagOfWords(text, STEM=False):
    try:
        #convert to lower case 
        raw = text.lower()

        #tokenize document string
        tokens = tokenizer.tokenize(raw)

        #remove stop words from tokens
        tokens = [t for t in tokens if t not in stopwords]
        

        #extract word stems
        if STEM:
            tokens = [stemmer.stem(t) for t in tokens]
    
        return tokens

    except:
        return None

def term_frequency(tokenized_document, term):
    return tokenized_document.count(term)

def doc_term_frequencies(tokenized_documents,all_tokens_set):
    tf_documents = []
    for document in tokenized_documents:
        doc_tf = []
        for term in all_tokens_set:
            tf = term_frequency(document,term)
            doc_tf.append(tf)
        tf_documents.append(doc_tf)
    return tf_documents    
    

def sublinear_term_frequency(term, tokenized_document):
    count = tokenized_document.count(term)
    if count == 0:
        return 0
    return 1 + math.log(count)
 
def augmented_term_frequency(term, tokenized_document):
    max_count = max([term_frequency(t, tokenized_document) for t in tokenized_document])
    return (0.5 + ((0.5 * term_frequency(term, tokenized_document))/max_count))
 
def inverse_document_frequencies(tokenized_documents, all_tokens_set):
    idf_values = {}    
    for tkn in all_tokens_set:
        contains_token = map(lambda doc: tkn in doc, tokenized_documents)
        idf_values[tkn] = 1 + math.log(len(tokenized_documents)/(sum(contains_token)))
    return idf_values
 
def tfidf(tokenized_documents, all_tokens_set):  
    idf = inverse_document_frequencies(tokenized_documents, all_tokens_set)
    tfidf_documents = []
    for document in tokenized_documents:
        doc_tfidf = []
        for term in idf.keys():
            tf = sublinear_term_frequency(term, document)
            doc_tfidf.append(tf * idf[term])
        tfidf_documents.append(doc_tfidf)
    return tfidf_documents

def main():

    documents=[]
    files = os.listdir(corpusSubPath)
    for doc in files: # read all files in the ./txt/ subfolder
        f = open(corpusSubPath+doc, 'r').read()
        documents.append(f)

    tokenized_documents = [bagOfWords(d) for d in documents]
    tokens = set([item for sublist in tokenized_documents for item in sublist])
    tokens = list(tokens)

    tf_all = doc_term_frequencies(tokenized_documents, tokens)
    tfidf_all = tfidf(tokenized_documents, tokens)
        
    tokens_encode= [s for s in tokens]
    tokens_encode.insert(0,"document")  # The first column in the output file shows the document name
    
    tf_file = open(tf_name, 'wb')
    tfwriter = csv.writer(tf_file,quoting = csv.QUOTE_NONNUMERIC)
    tfwriter.writerow(tokens_encode)
    i=0
    for row in tf_all:
        row.insert(0,files[i])
        tfwriter.writerow(row)
        i += 1
        
    tf_file.close()

    tfidf_file = open(tfidf_name, 'wb')
    tfidfwriter = csv.writer(tfidf_file,quoting = csv.QUOTE_NONNUMERIC)
    tfidfwriter.writerow(tokens_encode)
    i=0
    for row in tfidf_all:
        row.insert(0,files[i])
        tfidfwriter.writerow(row)
        i += 1
        
    tfidf_file.close()
    
    print "done!"
            

if __name__ == "__main__":
    main()
