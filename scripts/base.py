import pandas as pd
from elasticsearch import Elasticsearch
from core.util import query_dict, mkdir
from core.elastic import query
from config.config import TOPIC, SINGLE_IDX, META, VALID_ID, RUN_DIR


def main():
    meta = pd.read_csv(META)
    valid = pd.read_csv(VALID_ID, names=['cord_uid'])
    queries = query_dict(TOPIC)

    es = Elasticsearch([{'host': 'localhost',
                         'port': 9200,
                         'timeout': 3600}])

    mkdir(RUN_DIR)

    query(es, meta, valid, queries, IDX_NAME=SINGLE_IDX)


if __name__ == '__main__':
    main()
