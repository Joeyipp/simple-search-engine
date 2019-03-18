## Information Retrieval
### Description
A **Simple Search Engine** on Cranfield Dataset and **Query Processor** using **Boolean** and **Vector** (TF-IDF) Retrieval Models (Information Retrieval Spring 2019)

### Instructions
To run the scripts locally:
1. Clone this repository. **NOTE:** Scripts are written with **Python 2.7.x.**
2. Navigate to the **scripts** folder and run ```pip install requirements.txt``` to install dependencies. 
3. For complete documentation, refer [to this document](https://github.com/Joeyipp/simple-search-engine/blob/master/documentation/Design_Documentation.pdf).

### System Architecture
![Sample](https://github.com/Joeyipp/simple-search-engine/blob/master/documentation/Design_Flowchart.png)

### Part 1: Building the Inverted Index
> ```python index.py cran.all index_file```

![Sample](https://github.com/Joeyipp/simple-search-engine/blob/master/images/index_file.png)

### Part 2: Query Processing
![Sample](https://github.com/Joeyipp/simple-search-engine/blob/master/images/query_preprocessing.png)

### Query Processing using Boolean Retrieval Model
> ```python query.py index_file 0 query.text batch```

![Sample](https://github.com/Joeyipp/simple-search-engine/blob/master/images/query_boolean.png)

### Query Processing using Vector Retrieval Model
> ```python query.py index_file 1 query.text 284```

![Sample](https://github.com/Joeyipp/simple-search-engine/blob/master/images/query_vector.png)

### Part 3: Search Results Evaluation with NDCGs
> ```python batch_eval.py index_file query.text qrels.text 10```

![Sample](https://github.com/Joeyipp/simple-search-engine/blob/master/images/batch_eval.png)

### References
* [TF-IDF & Cosine Similarity](https://janav.wordpress.com/2013/10/27/tf-idf-and-cosine-similarity/)
