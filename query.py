
'''
query processing

'''

import sys
import doc

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
        
        # Apply Norvig's Spelling Corrector
        query_terms_spell_checked = []
        for term in query_terms:
            query_terms_spell_checked.append(correction(term))

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
        #ToDo: return a list of docIDs

        def intersect(posting_1, posting_2):
            answer = [] # The final intersect of the two posting lists

            print(posting_1)
            print(posting_2)

            while (len(posting_1) != 0) and (len(posting_2) != 0):
                print("Checking posting_1: {} with posting_2: {}".format(posting_1[0], posting_2[0]))

                if posting_1[0] == posting_2[0]:
                    answer.append(posting_1[0])
                    posting_1.pop(0)
                    posting_2.pop(0)
                elif posting_1[0] < posting_2[0]:
                    posting_1.pop(0)
                else:
                    posting_2.pop(0)
            
            return answer

        # Approach: Optimize booleanQuery processing using Document Frequency
        # Rational: Since every term in the query are AND, during the merge/intersect, 
        # We can intersect the 2 smallest posting lists since all intermediate results will be no longer than the smallest posting list,
        # to minimize time and work needed

        term_doc_freq_postings = []

        # Create a list of (term, document frequency, sorted_postings) tuple
        for term in preprocessed_query:
            term_doc_freq_postings.append((term, len(self.index.items[term].sorted_postings), self.index.items[term].sorted_postings))

        # Sort the tuple by increasing document frequency
        term_doc_freq_postings = sorted(term_doc_freq_postings, key=lambda elem : elem[1])

        ######### RESUME FROM HERE #########
        answer = intersect(term_doc_freq_postings[0][2], term_doc_freq_postings[1][2])

        print(answer)




    def vectorQuery(self, k):
        ''' vector query processing, using the cosine similarity. '''
        #ToDo: return top k pairs of (docID, similarity), ranked by their cosine similarity with the query in the descending order
        # You can use term frequency or TFIDF to construct the vectors

def test():
    ''' test your code thoroughly. put the testing cases here'''
    print('Pass')

def query():
    ''' the main query processing program, using QueryProcessor'''

    # ToDo: the commandline usage: "echo query_string | python query.py index_file processing_algorithm"
    # processing_algorithm: 0 for booleanQuery and 1 for vectorQuery
    # for booleanQuery, the program will print the total number of documents and the list of document IDs
    # for vectorQuery, the program will output the top 3 most similar documents

    # Parse the commandline
    index_file = sys.argv[1]

    if sys.argv[2] != "0" and sys.argv[2] != "1":
        print("Invalid processing_algorithm. Please try again with 0 for Boolean and 1 for Vector.")
        exit()
    else:
        processing_algorithm = sys.argv[2]

    query_text = sys.argv[3]
    query_id = sys.argv[4]

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

    # Preprocess the raw query
    preprocessed_query, preprocessed_query_with_positions = queryProcessor.preprocessing()

    # Process with preprocessed_query
    if processing_algorithm == "0":
        queryProcessor.booleanQuery(preprocessed_query)
    else:
        queryProcessor.vectorQuery(3)

if __name__ == '__main__':
    #test()
    query()
