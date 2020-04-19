from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MultiMatch
from config import docs, topic, SINGLE_IDX, META, VALID_ID, RUN_DIR
import pandas as pd
from util import query_dict


if __name__ == '__main__':

    meta = pd.read_csv(META)
    valid = pd.read_csv(VALID_ID, names=['cord_uid'])

    es = Elasticsearch([{'host': 'localhost',
                         'port': 9200,
                         'timeout': 3600}])

    queries = query_dict(topic)

    if SINGLE_IDX is None:
        for idx,path in docs.items():
            with open('./runs/' + idx, 'w') as run:
                for num, title in queries.items():
                    query = MultiMatch(query=title,
                                       fields=['abstract', 'body_text'],
                                       fuzziness='AUTO')
                    s = Search(using=es, index=idx).query(query)
                    response = s.execute()
                    count = 1
                    for hit in s[:1000]:
                        line = num + ' Q0 ' + hit.paper_id + ' ' + str(count) + ' ' + str(hit.meta.score) + ' IRC ' + '\n'
                        run.write(line)
                        count += 1
    else:
        with open(RUN_DIR + SINGLE_IDX, 'w') as run:
            for num, title in queries.items():
                query = MultiMatch(query=title,
                                   fields=['abstract', 'body_text'],
                                   fuzziness='AUTO')
                s = Search(using=es, index=SINGLE_IDX).query(query)
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