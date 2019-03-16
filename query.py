
'''
query processing

'''

import sys
import doc
import math
import copy
import numpy as np

from util import *
from index import *
from cranqry import *
from norvig_spell import correction

class QueryProcessor:

    def __init__(self, query, index, collection):
        ''' index is the inverted index; collection is the document collection'''
        self.raw_query = query
        self.index = index
        self.docs = collection

    def preprocessing(self):
        ''' apply the same preprocessing steps used by indexing,
            also use the provided spelling corrector. Note that
            spelling corrector should be applied before stopword
            removal and stemming (why?)'''
            # Because if spelling corrector is applied AFTER stopword removal and stemming,
            # then the wrongly spelled stopwords will not get removed and will remain in the query,
            # and the wrongly spelled words will not get properly stemmed.

        #ToDo: return a list of terms (Done)

        # Tokenizing
        query_terms = lowerCaseAndSplit(self.raw_query)
        
        # # Apply Norvig's Spelling Corrector
        # query_terms_spell_checked = []
        # for term in query_terms:
        #     query_terms_spell_checked.append(correction(term))

        query_terms_spell_checked = query_terms

        # Remove stopwords from the list of query terms
        query_terms_spell_checked = removeStopWords(query_terms_spell_checked)

        # Stem the list of query terms
        query_terms_spell_checked = stemming(query_terms_spell_checked)

        # Generate the (query_term, position) pair
        query_terms_spell_checked_with_positions = []
        for i in range(len(query_terms_spell_checked)):
            query_terms_spell_checked_with_positions.append((query_terms_spell_checked[i], i+1))

        return query_terms_spell_checked, query_terms_spell_checked_with_positions

    def booleanQuery(self, preprocessed_query):
        ''' boolean query processing; note that a query like "A B C" is transformed to "A AND B AND C" for retrieving posting lists and merge them'''
        #ToDo: return a list of docIDs (Done)
        # Intersecting two posting lists

        def intersect(posting_1, posting_2):
            answer = [] # The final intersect of the two posting lists

            # Make a deep copy of the posting list to preserve the original posting in the invertedIndex
            posting_1_copy = copy.deepcopy(posting_1)
            posting_2_copy = copy.deepcopy(posting_2)

            while (len(posting_1_copy) != 0) and (len(posting_2_copy) != 0):
                if posting_1_copy[0] == posting_2_copy[0]:
                    answer.append(posting_1_copy[0])
                    posting_1_copy.pop(0)
                    posting_2_copy.pop(0)
                elif posting_1_copy[0] < posting_2_copy[0]:
                    posting_1_copy.pop(0)
                else:
                    posting_2_copy.pop(0)
            
            return answer

        # Approach: Optimize booleanQuery processing using Document Frequency
        # Rational: Since every term in the query are AND, during the merge/intersect, 
        # We can intersect the 2 smallest posting lists since all intermediate results will be no longer than the smallest posting list,
        # to minimize time and work needed

        term_doc_freq_postings = []

        # Create a list of (term, document frequency, sorted_postings) tuple
        for term in preprocessed_query:
            if self.index.find(term) == "None":
                continue
            term_doc_freq_postings.append((term, len(self.index.items[term].sorted_postings), self.index.items[term].sorted_postings))

        # Sort the tuple by increasing document frequency
        term_doc_freq_postings = sorted(term_doc_freq_postings, key=lambda elem : elem[1])

        # The MERGE
        answer = intersect(term_doc_freq_postings[0][2], term_doc_freq_postings[1][2])

        for i in range(2, len(term_doc_freq_postings)):
            answer = intersect(answer, term_doc_freq_postings[i][2])
        
        return answer

    def vectorQuery(self, preprocessed_query, k, test):
        ''' vector query processing, using the cosine similarity. '''
        # ToDo: return top k pairs of (docID, similarity), ranked by their cosine similarity with the query in the descending order (Done)
        # You can use term frequency or TFIDF to construct the vectors (Done)

        def cosine_similarity(query, document):
            # cosine_similarity(query, document) = dot_product(query, document) / ||query|| * ||document||

            dot_product = np.dot(query, document)
            query_l2_norm = math.sqrt(sum(np.square(query)))
            document_l2_norm = math.sqrt(sum(np.square(document)))

            if dot_product == float(0) or query_l2_norm == float(0) or document_l2_norm == float(0):
                return float(0)
            else:
                return dot_product / (query_l2_norm * document_l2_norm)

        # Filter out any term in preprocessed query that does not exist in the invertedIndex
        query_terms = []
        for term in preprocessed_query:
            if self.index.find(term) == "None":
                continue
            else:
                query_terms.append(term)
        
        # Compute the Query Term Frequency (TF)
        # TF is defined as the number of times the term appears in a given query
        # The current TF implementation does not account any log weighting or length normalization
        query_tf = {}
        for term in query_terms:
            if term not in query_tf:
                query_tf[term] = 1
            else:
                query_tf[term] += 1
        
        # Compute the Document Term Frequency
        document_tf = {}
        list_of_relevant_docs = []
        for term in query_terms:
            if term not in document_tf:
                document_tf[term] = {}
                postings = self.index.items[term].sorted_postings

                for docid in postings:
                    document_tf[term][docid] = self.index.items[term].posting[str(docid)].term_freq()
                    list_of_relevant_docs.append(docid)
            else:
                continue
        list_of_relevant_docs = set(list_of_relevant_docs)

        # Compute the Inverse Document Frequency
        document_idf = {}
        for term in query_terms:
            if term not in document_idf:
                document_idf[term] = self.index.idf(term)
            else:
                continue
        
        # Compute the Query TF-IDF Vector
        query_tf_idf = []
        for term in query_terms:
            query_tf_idf.append(query_tf[term] * document_idf[term])

        # Compute the Document TF-IDF Vector
        document_tf_idf = {}
        for docid in list_of_relevant_docs:
            document_tf_idf[docid] = []
            for term in query_terms:
                term_docs = [doc for doc in document_tf[term].iterkeys()]
                if docid in term_docs:
                    document_tf_idf[docid].append(document_tf[term][docid] * document_idf[term])
                else:
                    document_tf_idf[docid].append(0)
        
        # Compute the the Query Cosine Similarity of on ALL Relevant Documents
        cosine_similarity_score = []
        for docid in list_of_relevant_docs:
            cosine_similarity_score.append((docid, cosine_similarity(query_tf_idf, document_tf_idf[docid])))

        # Sort the Cosine Similarity Score on descending order (Highest score first)
        cosine_similarity_score = sorted(cosine_similarity_score, key=lambda elem : elem[1], reverse=True)

        # Return the top K results
        top_k = []
        for i in range(k):
            top_k.append(cosine_similarity_score[i])
        
        ### TESTS ###
        if test == "test":
            j = 0
            print("\n== Query Terms ==")
            for term in query_terms:
                print("-> {}".format(term))
                print("TF: {}\t\tIDF: {}\tTF-IDF: {}".format(query_tf[term], round(document_idf[term], 3), round(query_tf_idf[j], 3)))
                j += 1
            
            query_v = [0.702753576, 0.702753576]
            document_v = [0.140550715, 0.140550715]

            print("\n== Testing Cosine Similary Calculations using Mock Query & Doc TF-IDF Vectors ==")
            print("Mock Query Vec:\t[0.702753576, 0.702753576]")
            print("Mock Docum Vec:\t[0.140550715, 0.140550715]")
            print("Cosine Similary: {}".format(cosine_similarity(query_v, document_v)))
         ### TESTS ###

        return top_k

def eval(queryId, queryProcessor, processing_algorithm, mode, k, test=0):
    # Preprocess the raw query
    preprocessed_query, preprocessed_query_with_positions = queryProcessor.preprocessing()

    if test == "test":
        print("Preprocessed query:\n{}".format(preprocessed_query))

    # Evaluate the preprocessed_query with Boolean Model
    if processing_algorithm == "0":
        list_of_docIDs = queryProcessor.booleanQuery(preprocessed_query)

        if test != "test":
            if mode == "batch":
                if list_of_docIDs:
                        print("QueryID: {}\t#Docs: {}\tDocIDs: {}".format(queryId, len(list_of_docIDs), list_of_docIDs))
            else:
                print("QueryID: {}\t#Docs: {}\tDocIDs: {}".format(queryId, len(list_of_docIDs), list_of_docIDs))

    # Evaluate the preprocessed_query with Vector Model
    elif processing_algorithm == "1":
        top_k_pairs = queryProcessor.vectorQuery(preprocessed_query, k, test)

        if test != "test":
            print("QueryID: {}".format(queryId))
            for pair in top_k_pairs:
                print("DocID: {}\tScore: {:.3f}".format(pair[0], pair[1]))
            print("\n")
                
def test():
    ''' test your code thoroughly. put the testing cases here'''
    
    # Parse the commandline
    index_file = sys.argv[1]

    if sys.argv[2] != "0" and sys.argv[2] != "1":
        print("Invalid processing_algorithm. Please try again with 0 for Boolean and 1 for Vector.")
        exit()
    else:
        processing_algorithm = sys.argv[2]

    query_text = sys.argv[3]
    query_id = sys.argv[4]
    
    # Prompt the user for top K results for Vector Model
    if processing_algorithm == "1":
        k = 3
    else:
        k = 0
        
    # Open the Cran.all Collection
    cf = CranFile ('cran.all')

    # Instantiate an invertedIndex
    invertedIndex = InvertedIndex()

    # Load the index_file into memory and reconstruct the invertedIndex
    invertedIndex.load(index_file)

    # Load the query_text file into qrys dictionary
    qrys = loadCranQry(query_text)

    # Retrieve the specific (raw) query based on query_id from the qrys dictionary
    query = qrys[query_id].text

    # Instantiate the QueryProcessor
    queryProcessor = QueryProcessor(query, invertedIndex, cf.collection)

    # Evaluate the single query with test cases (embedded in respective functions)
    print("Original query:\n{}".format(query))
    eval(query_id, queryProcessor, processing_algorithm, "single", k, "test")

    print('\nPass')

def query():
    ''' the main query processing program, using QueryProcessor'''

    # ToDo: the commandline usage: "echo query_string | python query.py index_file processing_algorithm" (Done)
    # processing_algorithm: 0 for booleanQuery and 1 for vectorQuery (Done)
    # for booleanQuery, the program will print the total number of documents and the list of document IDs (Done)
    # for vectorQuery, the program will output the top 3 most similar documents (Done)

    # Parse the commandline
    index_file = sys.argv[1]

    if sys.argv[2] != "0" and sys.argv[2] != "1":
        print("Invalid processing_algorithm. Please try again with 0 for Boolean and 1 for Vector.")
        exit()
    else:
        processing_algorithm = sys.argv[2]

    query_text = sys.argv[3]
    query_id = sys.argv[4]

    # Prompt the user for top K results for Vector Model
    if processing_algorithm == "1":
        k = int(input("Top K Pairs? "))
    else:
        k = 0
        
    # Open the Cran.all Collection
    cf = CranFile ('cran.all')

    # Instantiate an invertedIndex
    invertedIndex = InvertedIndex()

    # Load the index_file into memory and reconstruct the invertedIndex
    invertedIndex.load(index_file)

    # Load the query_text file into qrys dictionary
    qrys = loadCranQry(query_text)

    if query_id != "batch":
        ### SINGLE QUERY PROCESSING ###
        # Retrieve the specific (raw) query based on query_id from the qrys dictionary
        query = qrys[query_id].text

        # Instantiate the QueryProcessor
        queryProcessor = QueryProcessor(query, invertedIndex, cf.collection)

        # Evaluate the single query
        eval(query_id, queryProcessor, processing_algorithm, "single", k)

    else: 
        ### BATCH QUERIES PROCESSING ###
        query_Ids = qrys.iterkeys()
        query_Ids = sorted([int(queryId) for queryId in query_Ids])

        # Instantiate the QueryProcessor
        queryProcessor = QueryProcessor("None", invertedIndex, cf.collection)

        # Evaluate ALL queries
        for queryId in query_Ids:
            queryProcessor.raw_query = qrys[str(queryId)].text
            eval(queryId, queryProcessor, processing_algorithm, "batch", k)

if __name__ == '__main__':
    #test()
    query()
