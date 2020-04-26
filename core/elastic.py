import os
import json
import docker
from tqdm import tqdm
from elasticsearch import helpers
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MultiMatch
from config.config import IMAGE_TAG, CONTAINER_NAME, RUN_DIR, DOCS


settings = {"settings":
    {
        "index.mapping.total_fields.limit": 100000
    }
}


def start_container():
    client = docker.from_env(timeout=86400)
    client.containers.run(IMAGE_TAG,
                          ports={'9300/tcp': 9300, '9200/tcp': 9200},
                          name=CONTAINER_NAME,
                          environment={"discovery.type": "single-node"},
                          detach=True)
    print("Elasticsearch is running.")


def stop_rm_container():
    client = docker.from_env(timeout=86400)
    container = client.containers.get(CONTAINER_NAME)
    container.stop()
    container.remove()
    print('Removed container!')
    client.images.remove(IMAGE_TAG)
    print('Removed image!')


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


def multi_idx(es, DOCS, BULK):
    for idx, path in DOCS.items():
        if BULK:
            print('Indexing data for', idx)
            es.indices.create(index=idx, body=settings)
            helpers.bulk(es, load_json(path), index=idx, doc_type='publication')
        else:
            print('Indexing data for', idx)
            es.indices.create(index=idx, body=settings)
            seq_idx(idx, path, es)


def single_idx(es, DOCS, BULK, IDX_NAME):
    es.indices.create(index=IDX_NAME, body=settings)
    for idx, path in DOCS.items():
        if BULK:
            print('Indexing data for', idx)
            helpers.bulk(es, load_json(path), index=IDX_NAME, doc_type='publication')
        else:
            print('Indexing data for', idx)
            seq_idx(IDX_NAME, path, es)


def index(es, DOCS, BULK=True, IDX_NAME=None):
    if IDX_NAME:
        single_idx(es, DOCS, BULK, IDX_NAME)
    else:
        multi_idx(es, DOCS, BULK)


def query_multi_idx(es, queries, DOCS):
    for idx, path in DOCS.items():
        with open('./runs/' + idx, 'w') as run:
            for num, title in queries.items():
                query = MultiMatch(query=title,
                                   fields=['abstract', 'body_text'],
                                   fuzziness='AUTO')
                s = Search(using=es, index=idx).query(query)
                s.execute()
                count = 1
                for hit in s[:1000]:
                    line = num + ' Q0 ' + hit.paper_id + ' ' + str(count) + ' ' + str(hit.meta.score) + ' irc_base\n'
                    run.write(line)
                    count += 1


def query_single_idx(es, meta, valid, queries, IDX_NAME):

    with open(RUN_DIR + IDX_NAME, 'w') as run:
        for num, title in queries.items():
            query = MultiMatch(query=title,
                               fields=['abstract', 'body_text'],
                               fuzziness='AUTO')
            s = Search(using=es, index=IDX_NAME).query(query)
            response = s.execute()
            count = 1
            id_store = []
            for hit in s[:5000]:
                cord_uid_series = meta[meta['sha'] == hit.sha]['cord_uid']
                cord_uid = None
                try:
                    if len(cord_uid_series.values) > 1:
                        pass
                    cord_uid = cord_uid_series.values[0]
                except:
                    continue

                if cord_uid in valid.values and cord_uid not in id_store:
                    line = num + ' Q0 ' + cord_uid + ' ' + str(count) + ' ' + str(hit.meta.score) + ' IRC ' + '\n'
                    run.write(line)
                    id_store.append(cord_uid)
                    count += 1

                if count > 1000:
                    break


def query(es, meta, valid, queries, IDX_NAME=None):
    if IDX_NAME:
        query_single_idx(es, meta, valid, queries, IDX_NAME)
    else:
        query_multi_idx(es, queries, DOCS=DOCS)