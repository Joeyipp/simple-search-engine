
'''
   utility functions for processing terms

    shared by both indexing and query processing
'''

from nltk.stem import PorterStemmer

def lowerCaseAndSplit(sentence):
    tokens = sentence.lower().strip().split()
    cleaned_tokens = []

    for token in tokens:
        token = token.replace("'", "").strip("/,'.()=+-*")
        if token == "":
            continue
        cleaned_tokens.append(token)

    return cleaned_tokens

def isStopWord(word):
    ''' using the NLTK functions, return true/false'''
    
    # ToDo (Done)
    list_of_stop_words = []

    with open("stopwords", "r") as file:
        data = file.readlines()

        for line in data:
            list_of_stop_words.append(line.strip())
    
    return True if word in list_of_stop_words else False

def removeStopWords(words):

    list_without_stop_words = []

    for word in words:
        if not isStopWord(word):
            list_without_stop_words.append(word)
    
    return list_without_stop_words

def stemming(words):
    ''' return the stem, using a NLTK stemmer. check the project description for installing and using it'''

    # ToDo (Done)
    ps = PorterStemmer()
    list_of_stemmed_words = []
    
    for word in words:
        list_of_stemmed_words.append(str(ps.stem(word)))

    return list_of_stemmed_words