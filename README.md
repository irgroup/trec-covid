# trec-covid

## Setup

* Install docker. When running on HPC (Ubuntu VM):  
``` 
sudo usermod -aG docker $USER
```
* Download data from [semanticscholar](https://pages.semanticscholar.org/coronavirus-research), extract it and place it in `./data/`. 
``` 
./getDataSets.sh
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
* Adapt settings in `config.py`  

## Workflow

* Download image and run Elasticsearch container
```shell script
python3 docker-run.py
```

* Index data  
```shell script
python3 index.py
```

* Write run files
```shell script
python3 query.py
```

* Optionally, delte the docker container and remove the image  
```shell script
python3 docker-rm.py
```

* Fetch data for 30 topics from PubMed (will be written to `artifact` directory with timestamp)
```shell script
python3 fetchPubmedData.py
```

## `config.py`

| param | comment |
| ---  | --- |
| `docs` | dictionary with index names as keys and paths to data as values |
| `BULK` | if set to `True` data is indexed in bulk |   
| `SINGLE_IDX` | if is not `None`, all data is indexed into one instance |   
| `topic` | path to topic file | 

## `runs`

| name | comment |
| ---  | --- |
| `comm` | run retrieved from index with [commercial use subset](https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-04-10/comm_use_subset.tar.gz) data |
| `noncomm` | run retrieved from index with [non-commercial use subset](https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-04-10/noncomm_use_subset.tar.gz) data |   
| `custom` | run retrieved from index with [custom license subset ](https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-04-10/custom_license.tar.gz) data |   
| `biorxiv` | run retrieved from index with [bioRxiv/medRxiv subset](https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-04-10/biorxiv_medrxiv.tar.gz) data | 
| `trec-covid` | run retrieved from one single index with all subsets | 
