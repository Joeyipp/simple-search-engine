'''

Index structure:

    The Index class contains a list of IndexItems, stored in a dictionary type for easier access

    each IndexItem contains the term and a set of PostingItems

    each PostingItem contains a document ID and a list of positions that the term occurs

'''

import sys
import doc
import json
import math
import jsonpickle

from util import *
from cran import CranFile
from collections import OrderedDict

class Posting:
    def __init__(self, docID):
        self.docID = docID
        self.positions = []

    def append(self, pos):
        self.positions.append(pos)

    def sort(self):
        ''' sort positions'''
        self.positions.sort()

    def merge(self, positions):
        self.positions.extend(positions)

    def term_freq(self):
        ''' return the term frequency in the document'''
        # ToDo (Done)

        # if len(self.positions) > 0:
        #     return 1 + math.log(len(self.positions), 10)
        # else:
        #     return 0

        # TF is defined as the number of times the term appears in a given document
        # The current TF implementation does not account any log weighting or length normalization
        return len(self.positions)

class IndexItem:
    def __init__(self, term):
        self.term = term
        self.posting = {} # postings are stored in a python dict for easier index building
        self.sorted_postings = [] # may sort them by docID for easier query processing

    def add(self, docid, pos):
        ''' add a posting'''
        if not self.posting.has_key(docid):
            self.posting[docid] = Posting(docid)
        self.posting[docid].append(pos)

    def sort(self):
        ''' sort by document ID for more efficient merging. For each document also sort the positions'''
        # ToDo (Done)
        # Sort by document ID and save the sorted docID order to the self.sorted_postings list
        self.sorted_postings = sorted(self.posting.iterkeys())

        # Sort the positions within each document
        for docid in self.sorted_postings:
            self.posting[docid].sort()
        
class InvertedIndex:

    def __init__(self):
        self.items = {} # list of IndexItems
        self.nDocs = 0  # the number of indexed documents

    def indexDoc(self, doc, mode=0): # indexing a Document object
        ''' indexing a document, using the simple SPIMI algorithm, but no need to store blocks due to the small collection we are handling. Using save/load the whole index instead'''

        # ToDo: indexing only title and body; use some functions defined in util.py (Done)
        # (1) convert to lower cases, (Done)
        # (2) remove stopwords, (Done)
        # (3) stemming (Done)

        # Tokenizing
        document_terms = lowerCaseAndSplit(doc.body)
        if mode == "test":
            print("List of tokens (lowercased):\n{}\n".format(document_terms))

        # Remove stopwords
        document_terms = removeStopWords(document_terms)
        if mode == "test":
            # Test for stopwords removal
            print("After stopwords removal:\n{}\n".format(document_terms))

        # Stem the list of terms
        document_terms = stemming(document_terms)
        if mode == "test":
            # Test for stemming
            print("After stemming:\n{}\n".format(document_terms))

        # Generate the (term, position) pair
        terms_with_positions = []
        for i in range(len(document_terms)):
            terms_with_positions.append((document_terms[i], i+1))

        # Create an IndexItem object for each 
        for term in terms_with_positions:
            if term[0] not in self.items:
                self.items[term[0]] = IndexItem(term[0])
                self.items[term[0]].add(int(doc.docID), int(term[1]))
            else:
                self.items[term[0]].add(int(doc.docID), int(term[1]))
        
        self.nDocs += 1

    def sort(self):
        ''' sort all posting lists by docID'''
        # ToDo (Done)
        for term in self.items:
            self.items[term].sort()

        ''' sort the InvertedIndex by terms'''
        # ToDo (Done)
        self.items = OrderedDict(sorted(self.items.items(), key=lambda t: t[0]))

    def find(self, term):
        return self.items.get(term, "None")

    def save(self, filename):
        ''' save to disk'''
        # ToDo: using your preferred method to serialize/deserialize the index (Done)
        print("Saving to disk...")
        with open(filename, "w") as f:
            for term in self.items:
                f.write(jsonpickle.encode(self.items[term]))
                f.write('\n')
            f.write(jsonpickle.encode(self.nDocs))
        
        print("InvertedIndex successfully saved to {}\n".format(filename))

    def load(self, filename):
        ''' load from disk'''
        # ToDo (Done)
        print("Loading from disk...")
        with open(filename, "r") as f:
            data = f.readlines()
            for i in range(len(data)-1):
                indexItem = jsonpickle.decode(data[i])
                self.items[indexItem.term] = indexItem
            self.nDocs = jsonpickle.decode(data[-1])
        
        print("InvertedIndex successfully loaded to memory from {}\n".format(filename))

    def idf(self, term):
        ''' compute the inverted document frequency for a given term'''
        # ToDo: return the IDF of the term
        # log(total documents/ documents with term i)
        return math.log(self.nDocs / len(self.items[term].sorted_postings), 10)

    # more methods if needed

def test():
    ''' test your code thoroughly. put the testing cases here'''

    # Import the cran.all collection
    cf = CranFile(sys.argv[1])

    # Instantiate an invertedIndex
    invertedIndex_1 = InvertedIndex()

    # Index the first 2 documents
    for i in range(2):
        print("Indexing document {}\n".format(cf.docs[i].docID))
        invertedIndex_1.indexDoc(cf.docs[i], "test")

    # Check number of document indexed
    print("# of documents indexed: {}".format(invertedIndex_1.nDocs))

    # Check number of terms indexed
    print("# of terms indexed: {}\n".format(len([item for item in invertedIndex_1.items.iterkeys()])))

    # Sort the invertedIndex
    invertedIndex_1.sort()

    # Check the posting list, term frequency, and IDF
    print("== Statistics for the term 'lift' BEFORE saving the index to disk (invertedIndex_1) ==")
    print("Posting list:\t{}".format(invertedIndex_1.find("lift").sorted_postings))
    print("Positions:\t{}".format(invertedIndex_1.find("lift").posting[1].positions))
    print("TF:\t\t{}".format(invertedIndex_1.find("lift").posting[1].term_freq()))
    print("IDF:\t\t{}\n".format(round(invertedIndex_1.idf("lift"), 5)))

    # Save the invertedIndex
    invertedIndex_1.save(sys.argv[2])

    # Instantiate a new invertedIndex
    invertedIndex_2 = InvertedIndex()

    # Load the invertedIndex
    invertedIndex_2.load(sys.argv[2])

    # Check the posting list, term frequency, and IDF
    print("== Statistics for the term 'lift' AFTER loading the index from disk (invertedIndex_2) ==")
    print("Posting list:\t{}".format(invertedIndex_2.find("lift").sorted_postings))
    print("Positions:\t{}".format(invertedIndex_2.find("lift").posting["1"].positions))
    print("TF:\t\t{}".format(invertedIndex_2.find("lift").posting["1"].term_freq()))
    print("IDF:\t\t{}\n".format(round(invertedIndex_2.idf("lift"), 5)))

    print('Pass')

def indexingCranfield():
    # ToDo: indexing the Cranfield dataset and save the index to a file (Done)
    # command line usage: "python index.py cran.all index_file" (Done)
    # the index is saved to index_file (Done)

    # Import the cran.all collection
    cf = CranFile(sys.argv[1])

    # Instantiate an invertedIndex
    invertedIndex = InvertedIndex()

    # Loop through and index each document in the Cran collection
    for doc in cf.docs:
        print("Indexing document {}".format(doc.docID))
        invertedIndex.indexDoc(doc)

    print("\nTotal documents indexed: {}".format(invertedIndex.nDocs))

    # Sort the invertedIndex
    invertedIndex.sort()

    # Save the invertedIndex
    invertedIndex.save(sys.argv[2])

    print('Done')

if __name__ == '__main__':
    #test()
    indexingCranfield()
