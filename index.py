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
        #ToDo (Done)
        if len(self.positions) > 0:
            return 1 + math.log(len(self.positions), 10)
        else:
            return 0

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

    def indexDoc(self, doc): # indexing a Document object
        ''' indexing a document, using the simple SPIMI algorithm, but no need to store blocks due to the small collection we are handling. Using save/load the whole index instead'''

        # ToDo: indexing only title and body; use some functions defined in util.py (Done)
        # (1) convert to lower cases, (Done)
        # (2) remove stopwords, (Done)
        # (3) stemming (Done)

        # Tokenizing
        document_terms = lowerCaseAndSplit(doc.body)
        
        # Remove stopwords
        document_terms = removeStopWords(document_terms)

        # Stem the list of terms
        document_terms = stemming(document_terms)

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
        return self.items["term"]

    def save(self, filename):
        ''' save to disk'''
        # ToDo: using your preferred method to serialize/deserialize the index (Done)
        print("Saving to disk...\n")
        with open(filename, "w") as f:
            for term in self.items:
                f.write(jsonpickle.encode(self.items[term]))
                f.write('\n')
            f.write(jsonpickle.encode(self.nDocs))
        
        print("InvertedIndex successfully saved to {}".format(filename))

    def load(self, filename):
        ''' load from disk'''
        # ToDo (Done)
        print("Loading from disk...\n")
        with open(filename, "r") as f:
            data = f.readlines()
            for i in range(len(data)-1):
                indexItem = jsonpickle.decode(data[i])
                self.items[indexItem.term] = indexItem
            self.nDocs = jsonpickle.decode(data[-1])
        
        print("InvertedIndex successfully loaded to memory from {}".format(filename))

    def idf(self, term):
        ''' compute the inverted document frequency for a given term'''
        # ToDo: return the IDF of the term
        # log(total documents/ documents with term i)
        return math.log(self.nDocs / len(self.items[term].sorted_postings), 10)

    # more methods if needed

def test():
    ''' test your code thoroughly. put the testing cases here'''
    # ### Testing
    # print("Before Loading Index")
    # print(invertedIndex.items["experiment"].term, invertedIndex.items["experiment"].sorted_postings)
    # print(invertedIndex.items["experiment"].posting[1].positions)
    # print(invertedIndex.items["experiment"].posting[1].term_freq())
    # print("IDF: ", invertedIndex.idf("experiment"))

    # print("After Loading Index")
    # invertedIndex.load("index_file")
    # print(invertedIndex.items["experiment"].term, invertedIndex.items["experiment"].sorted_postings)
    # print(invertedIndex.items["experiment"].posting["1"].positions)
    # print(invertedIndex.items["experiment"].posting["1"].term_freq())
    # print("IDF: ", invertedIndex.idf("experiment"))

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
