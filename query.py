from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MultiMatch
from config import docs, topic


def query_dict(topic_file):
    queries = {}
    with open(topic_file, 'r') as topic:
        soup = BeautifulSoup(topic.read(), 'lxml')
        for top in soup.find_all('topic'):
            num = top.attrs.get('number')
            query = top.query.text
            question = top.question.text
            narrative = top.narrative.text

            queries[num] = query

    return queries


if __name__ == '__main__':

    es = Elasticsearch([{'host': 'localhost',
                         'port': 9200}])

    queries = query_dict(topic)

    for idx,path in docs.items():

        with open('./runs/' + idx, 'w') as run:

            for num, title in queries.items():

                query = MultiMatch(query=title,
                                   fields=['abstract', 'body_text'],
                                   fuzziness='AUTO')
                s = Search(using=es, index='noncomm').query(query)
                response = s.execute()

                count = 1
                for hit in s[:1000]:
                    line = num + ' Q0 ' + hit.paper_id + ' ' + str(count) + ' ' + str(hit.meta.score) + ' IRC ' + '\n'
                    run.write(line)
                    count += 1