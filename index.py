from elasticsearch import Elasticsearch
from config.config import DOCS, BULK, SINGLE_IDX
from core.elastic import index


def main():
    es = Elasticsearch([{'host': 'localhost',
                         'port': 9200,
                         'timeout': 3600}])

    index(es, DOCS, BULK=BULK, IDX_NAME=SINGLE_IDX)


if __name__ == '__main__':
    main()

