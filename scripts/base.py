import pandas as pd
from elasticsearch import Elasticsearch
from core.util import query_dict, mkdir
from core.elastic import query
from config.config import TOPIC, SINGLE_IDX, META, VALID_ID, RUN_DIR, QRELS_RND1, ROUND


def main():
    meta = pd.read_csv(META)
    valid = pd.read_csv(VALID_ID, names=['cord_uid'])
    queries = query_dict(TOPIC)

    es = Elasticsearch([{'host': 'localhost',
                         'port': 9200,
                         'timeout': 3600}])

    mkdir(RUN_DIR)

    qrels = None
    if ROUND == 2:
        qrels = pd.read_csv(QRELS_RND1,
                            sep='\s{1,}',
                            names=['topic', 'Q0', 'docid', 'rel'],
                            index_col=False)

    query(es, meta, valid, queries, qrels, IDX_NAME=SINGLE_IDX)


if __name__ == '__main__':
    main()
