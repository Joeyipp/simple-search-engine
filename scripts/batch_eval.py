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
import warnings

from util import *
from index import *
from query import *
from metrics import *
from cranqry import *

def batch_eval(qrys, query_Ids, query_qrels_mapping, qrels_dict, invertedIndex, collection, k):
    # Instantiate the QueryProcessor
    queryProcessor = QueryProcessor("None", invertedIndex, collection)
    
    # Initialize Boolean and Vector NDCG Scores
    boolean_ndcg_scores = []
    total_boolean_ndcg_scores = 0

    vector_ndcg_scores = []
    total_vector_ndcg_scores = 0

    for queryId in query_Ids:
        print("Processing QueryID: {}".format(queryId))

        # Get the corresponding qrels_Id of the queryId
        qrels_Id = query_qrels_mapping[queryId]

        # Get the corresponding list of relevant qrels docs 
        list_of_relevant_qrels_docs = qrels_dict[qrels_Id]

        queryProcessor.raw_query = qrys[str(queryId)].text
    
        # Preprocess the raw query
        preprocessed_query, preprocessed_query_with_positions = queryProcessor.preprocessing()

        # Score the preprocessed_query with Boolean Model
        y_true_boolean = []
        y_score_boolean = []

        list_of_docIDs = queryProcessor.booleanQuery(preprocessed_query)

        if list_of_docIDs:
            for docID in list_of_docIDs:
                if docID not in list_of_relevant_qrels_docs:
                    y_true_boolean.append(0)
                else:
                    y_true_boolean.append(1)
                y_score_boolean.append(1)
            
            while len(y_true_boolean) != k:
                y_true_boolean.append(0)
                y_score_boolean.append(0)
            
            boolean_ndcg_score = ndcg_score(y_true_boolean, y_score_boolean, k) 
            if math.isnan(boolean_ndcg_score):
                boolean_ndcg_score = float(0)
            
            boolean_ndcg_scores.append(boolean_ndcg_score)
            total_boolean_ndcg_scores += boolean_ndcg_score

            #print("QueryID: {}\tBoolean NDCG: {}".format(queryId, round(boolean_ndcg_score, 5)))
            
        else:
            boolean_ndcg_scores.append(float(0))
            total_boolean_ndcg_scores += float(0)

        # Score the preprocessed_query with Vector Model 
        y_true_vector = []
        y_score_vector = []

        top_k_pairs = queryProcessor.vectorQuery(preprocessed_query, k, test=0)
        
        for pair in top_k_pairs:
            if pair[0] not in list_of_relevant_qrels_docs:
                y_true_vector.append(0)
            else:
                y_true_vector.append(1)
            y_score_vector.append(pair[1])
        
        vector_ndcg_score = ndcg_score(y_true_vector, y_score_vector, k)
        if math.isnan(vector_ndcg_score):
            vector_ndcg_score = float(0)

        vector_ndcg_scores.append(vector_ndcg_score)
        total_vector_ndcg_scores += vector_ndcg_score

        #print("QueryID: {}\tNDCG Score: {}".format(queryId, round(vector_ndcg_score, 5)))

    # Compute the Average NDCG Scores for both Boolean and Vector Models
    average_boolean_ndcg_scores = total_boolean_ndcg_scores / len(boolean_ndcg_scores)
    average_vector_ndcg_scores = total_vector_ndcg_scores / len(vector_ndcg_scores)

    # Compute the p-value using wilcoxon-test on Boolean and Vector NDCGs
    warnings.simplefilter("ignore") # Ignore SciPy warnings when computing Wilcoxon with zero-values Boolean NDCG vector
    p_value = scipy.stats.wilcoxon(boolean_ndcg_scores, vector_ndcg_scores)[1]

    print("\nAvg. Boolean NDCG Scores:\t{}".format(round(average_boolean_ndcg_scores, 5)))
    print("Avg. Vector  NDCG Scores:\t{}".format(round(average_vector_ndcg_scores, 5)))
    print("Wilcoxon Test P-Value:\t\t{}\n".format(p_value))

    if p_value < 0.05:
        print("There is significant difference between Boolean and Vector Retrieval Model!")
    else:
        print("There is NO significant difference between Boolean and Vector Retrieval Model!")

def eval():
    # ToDo (Done)
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
    query_qrels_mapping, qrels_query_mapping = qidMapping()

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
        ### N QUERY PROCESSING ###
        # Get N random query Ids using the random function
        rand_qrels_Id = [random.randint(1, 225) for i in range(int(n))]
        rand_query_Ids = [qrels_query_mapping[qid] for qid in rand_qrels_Id]

        # N queries evaluation
        batch_eval(qrys, rand_query_Ids, query_qrels_mapping, qrels_dict, invertedIndex, cf.collection, k)
        
    else:
        ### BATCH QUERIES PROCESSING ###
        # Get ALL query Ids
        query_Ids = qrys.iterkeys()
        query_Ids = sorted([int(queryId) for queryId in query_Ids])

        # ALL queries evaluation
        batch_eval(qrys, query_Ids, query_qrels_mapping, qrels_dict, invertedIndex, cf.collection, k)

    print('Done')

if __name__ == '__main__':
    eval()
