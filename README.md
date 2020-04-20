# trec-covid
## Workflow 
![workflow](doc/workflow.png)
### Setup
Our retrieval pipeline relies on the following dependencies:  
[[docker](https://docker-py.readthedocs.io/en/stable/)][[elasticsearch](https://elasticsearch-py.readthedocs.io/en/master/)][[requests](https://2.python-requests.org/en/master/)][[beautifulsoup](https://www.crummy.com/software/BeautifulSoup/)][[matchzoo](https://github.com/NTMC-Community/MatchZoo)]

* Install docker. When running on HPC (Ubuntu VM):  
``` 
sudo usermod -aG docker $USER
```
* Make virtual environment and activate it
``` 
python3 -m venv venv
source venv/bin/activate
``` 
* Install requirements:   
```shell script
pip3 install -r requirements.txt
```  
Run `python3` and install nltk data:  
```shell script
>>> import nltk
>>> nltk.download('punkt')
```
* Download data from [semanticscholar](https://pages.semanticscholar.org/coronavirus-research), extract it and place it in `./data/`. 
``` 
./getDataSets.sh
``` 
* Fetch data for 30 topics from PubMed (will be written to `artifact` directory with timestamp)
```shell script
python3 fetchPubmedData.py
```
* **Optional:** Adapt settings in `config.py`  

### Baseline run 
* Download image and run Elasticsearch container
```shell script
python3 docker-run.py
```
* Index data  
```shell script
python3 index.py
```
* Write baseline run file
```shell script
python3 query.py
```
* **Optional:** Delete the docker container and remove the image  
```shell script
python3 docker-rm.py
```

### Reranking
* Train model for each of the 30 topics and save models to `./artifact/model/<model-type>`
```shell script
python3 train.py
```
* Rerank baseline ranking:
```shell script
python3 rerank.py
```

### `config.py`
| param | comment |
| ---  | --- |
| docs | dictionary with index names as keys and paths to data as values |
| BULK | if set to `True` data is indexed in bulk |   
| SINGLE_IDX | if is not `None`, all data is indexed into one instance |   
| topic | path to topic file | 
| BASELINE | name of the baseline run |
| DATA | path to directory with subsets |
| META | path to `metadata.csv` |
| VALID_ID | path to xml file with valid doc ids |
| ESEARCH | pubmed eutils api to retrieve pmids given a query term |
| EFETCH | pubmed eutils to retrieve document data given one or more pmids |
| RETMODE | datatype of pubmed eutils results |
| PUBMED_FETCH | directory to fetched data from pubmed |
| PUBMED_DUMP_DATE | specify date of pubmed data for training |
| MODEL_DUMP | path to directory where model weights are stored |
| MODEL_TYPE | specify model type. at the moment `dense` and `drmm` are supported |
| RUN_DIR | path to the output runs |
| RERANKED_RUN | name of the reranked run |
| PUBMED_SCRAPE | bool. if set to `True`, pmids are scraped from pubmed frontend |
| PUBMED_FRONT | URL of the pubmed frontend |
| RESULT_SIZE | number of results to be retrieved from PUBMED_FRONT |
| RERANK_WEIGHT | weight param for reranker score. `default: 0.5` |

### Datasets
| name | link |
| ---  | --- |
| `comm` | [commercial use subset](https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-04-10/comm_use_subset.tar.gz) |
| `noncomm` | [non-commercial use subset](https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-04-10/noncomm_use_subset.tar.gz) |   
| `custom` | [custom license subset ](https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-04-10/custom_license.tar.gz) |   
| `biorxiv` | [bioRxiv/medRxiv subset](https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-04-10/biorxiv_medrxiv.tar.gz) | 