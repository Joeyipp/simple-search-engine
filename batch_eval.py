'''
a program for evaluating the quality of search algorithms using the vector model

it runs over all queries in query.text and get the top 10 results,
and then qrels.text is used to compute the NDCG metric

usage:
    python batch_eval.py index_file query.text qrels.text n

    output is the average NDCG over all the queries for boolean model and vector model respectively.
	also compute the p-value of the two ranking results. 
'''

import sys
import doc
import math
import scipy
import random

from util import *
from index import *
from query import *
from metrics import *
from cranqry import *

def eval():

    # ToDo
    # Parse the commandline
    index_file = sys.argv[1]
    query_text = sys.argv[2]
    qrels_text = sys.argv[3]

    # Number of randomly selected queries from query_text
    n = sys.argv[4]

    # Top K pairs
    # k = int(input("Top K Pairs? "))
    k = 10

    # Open the Cran.all Collection
    cf = CranFile ('cran.all')

    # Instantiate an invertedIndex
    invertedIndex = InvertedIndex()

    # Load the index_file into memory and reconstruct the invertedIndex
    invertedIndex.load(index_file)

    # Load the query_text file into qrys dictionary
    qrys = loadCranQry(query_text)

    # Get the qrels_text to query_text ID Mappings
    qrels_query_mapping = qidMapping()

    # Create the qrels_text (Ground Truth Relevance) dictionary
    qrels_dict = {}

    with open(qrels_text, 'r') as f:
        data = f.readlines()

        for line in data:
            dat = line.split()
            dat = [int(elem) for elem in dat]

            if dat[0] not in qrels_dict.iterkeys():
                qrels_dict[dat[0]] = []
                qrels_dict[dat[0]].append(dat[1])
            else:
                qrels_dict[dat[0]].append(dat[1])

    if n != "batch":
        ############################### N QUERY PROCESSING ###############################
        rand_queries = [random.randint(1, 225) for i in range(n)]


        ############################### N QUERY PROCESSING ###############################

    else:
        ############################# BATCH QUERIES PROCESSING #############################
        query_Ids = qrys.iterkeys()
        query_Ids = sorted([int(queryId) for queryId in query_Ids])

        # Instantiate the QueryProcessor
        queryProcessor = QueryProcessor("None", invertedIndex, cf.collection)

        boolean_ndcg_scores = []
        total_boolean_ndcg_scores = 0

        vector_ndcg_scores = []
        total_vector_ndcg_scores = 0

        for queryId in query_Ids:
            # Get the corresponding qrels_Id of the queryId
            qrels_Id = qrels_query_mapping[queryId]

            queryProcessor.raw_query = qrys[str(queryId)].text
        
            # Preprocess the raw query
            preprocessed_query, preprocessed_query_with_positions = queryProcessor.preprocessing()

            # Process with preprocessed_query with Boolean Model
            # list_of_docIDs = queryProcessor.booleanQuery(preprocessed_query)
            # if list_of_docIDs:
            #     print("QueryID: {}\t#Docs: {}\tDocIDs: {}".format(queryId, len(list_of_docIDs), list_of_docIDs))


            # Process with preprocessed_query with Vector Model    
            top_k_pairs = queryProcessor.vectorQuery(preprocessed_query, k)
            list_of_relevant_qrels_docs = qrels_dict[qrels_Id]
            y_true = []
            y_score = []
            
            for pair in top_k_pairs:
                if pair[0] not in list_of_relevant_qrels_docs:
                    y_true.append(0)
                else:
                    y_true.append(1)
                y_score.append(pair[1])
            
            vector_ndcg_score = ndcg_score(y_true, y_score, k)
            if math.isnan(vector_ndcg_score):
                vector_ndcg_score = float(0)

            vector_ndcg_scores.append(vector_ndcg_score)
            total_vector_ndcg_scores += vector_ndcg_score

            print("QueryID: {}\tNDCG Score: {}".format(queryId, round(vector_ndcg_score, 5)))


        average_vector_ndcg_scores = total_vector_ndcg_scores / len(vector_ndcg_scores)
        print("\nAverage Vector NDCG Scores: {}".format(round(average_vector_ndcg_scores, 5)))

        ############################# BATCH QUERIES PROCESSING #############################

    print('Done')

if __name__ == '__main__':
    eval()
