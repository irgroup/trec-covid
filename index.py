import json
import os
from elasticsearch import Elasticsearch, helpers
from tqdm import tqdm
from config import DOCS, BULK, SINGLE_IDX


def prep(file):
    j = json.load(file)
    body_text = ''
    for t in j['body_text']:
        body_text = body_text + t.get('text')

    abstract = ''
    if j.get('abstract') is not None:
        for t in j.get('abstract'):
            abstract = abstract + t.get('text')

    sha = file.name.split('/')[-1][:-5]

    title = j.get('metadata').get('title')

    return {'sha': sha,
            'title': title,
            'abstract': abstract,
            'body_text': body_text}


def full_path(dir):
    full_path = []
    for path, subdir, file in os.walk(dir):
        extensions = tuple([".json"])
        files = [f for f in file if f.endswith(extensions)]
        for f in files:
            full_path.append(os.path.join(path, f))

    return full_path


def seq_idx(idx, path, es_client):
    paths = full_path(path)
    with tqdm(total=len(paths)) as pbar:
        for fp in paths:
            with open(fp) as file:
                j = prep(file)

                es_client.index(index=idx,
                                doc_type='publication',
                                id=j['paper_id'],
                                body=j)
                pbar.update()


def load_json(directory):
    for path, subdir, file in os.walk(directory):
        extensions = tuple([".json"])
        files = [f for f in file if f.endswith(extensions)]
        for f in files:

            with open(os.path.join(path, f), 'r') as open_file:
                yield prep(open_file)


def main():
    es = Elasticsearch([{'host': 'localhost',
                         'port': 9200,
                         'timeout': 3600}])

    settings = {"settings":
                    {
                        "index.mapping.total_fields.limit": 100000
                    }
                }

    if SINGLE_IDX is None:
        for idx,path in DOCS.items():
            if BULK:
                print('Indexing data for', idx)
                es.indices.create(index=idx, body=settings)
                helpers.bulk(es, load_json(path), index=idx, doc_type='publication')
            else:
                print('Indexing data for', idx)
                es.indices.create(index=idx, body=settings)
                seq_idx(idx, path, es)
    else:
        es.indices.create(index=SINGLE_IDX, body=settings)
        for idx, path in DOCS.items():
            if BULK:
                print('Indexing data for', idx)
                helpers.bulk(es, load_json(path), index=SINGLE_IDX, doc_type='publication')
            else:
                print('Indexing data for', idx)
                seq_idx(SINGLE_IDX, path, es)


if __name__ == '__main__':
    main()

