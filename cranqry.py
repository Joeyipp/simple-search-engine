'''
  handling the specific input format of the query.text for the Cranfield data
'''

class CranQry:
    def __init__(self, qid, text):
        self.qid = qid
        self.text = text

def loadCranQry(qfile):
    queries = {}
    f = open(qfile)
    text = ''
    qid = ''
    for line in f:
        if '.I' in line:
            if qid !='':
                queries[qid] = CranQry(qid, text)
                #print 'qid:', qid, text
            qid = line.strip().split()[1].lstrip("0")
            text = ''
        elif '.W' in line:
            None
        else:
            text += line
    queries[qid] = CranQry(qid, text)
    return queries

def test():
    '''testing'''
    qrys =  loadCranQry('query.text')
    for q in qrys:
        print(q, qrys[q].text)
    print(len(qrys))

def qidMapping():
    ############# CREATE A MAPPING of qid in qrels.txt to qid in query.text ##############
    qrys = loadCranQry('query.text')
    query_Ids = qrys.iterkeys()
    query_Ids = sorted([int(queryId) for queryId in query_Ids])
    
    qids = []
    mapping = {}

    with open('qrels.text', 'r') as f:
        data = f.readlines()
        

        for line in data:
            qids.append(line.split()[0])

    qids = sorted(set(([int(qid) for qid in qids])))

    i = 0
    for qid in qids:
        mapping[query_Ids[i]] = qid
        i += 1
    
    with open('qrelsMapping.txt', 'w') as f:
        f.write("QrelsId\tQueryId\n")
        for key, value in mapping.iteritems():
            f.write("{}\t{}\n".format(value, key))
    
    return mapping
    ################################### END OF MAPPING ####################################

if __name__ == '__main__':
    #test()
    print(qidMapping())
