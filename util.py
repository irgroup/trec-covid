import os
import pandas as pd
from bs4 import BeautifulSoup as bs
import matchzoo as mz
from config import topic, PUBMED_FETCH, PUBMED_DUMP_DATE


def query_dict(topic_file):
    queries = {}
    with open(topic_file, 'r') as topic:
        soup = bs(topic.read(), 'lxml')
        for top in soup.find_all('topic'):
            num = top.attrs.get('number')
            query = top.query.text
            question = top.question.text
            narrative = top.narrative.text

            queries[num] = query

    return queries


def train_data(topic_train):
    queries = query_dict(topic)

    text_left = []
    id_left = []
    text_right = []
    id_right = []
    label = []

    for k, v in queries.items():
        file_path = os.path.join(PUBMED_FETCH, PUBMED_DUMP_DATE, str(k)+'.xml')
        with open(file_path, 'r') as input:
            soup = bs(input.read(), 'lxml')

            articles = soup.find_all('pubmedarticle')
            for article in articles:
                pbmid = article.find('articleid', {"idtype": "pubmed"})
                pbmid_str = pbmid.text.replace('\n', '').strip()
                abstract = article.find('abstract')
                if abstract is None:
                    continue
                else:
                    abstract_text = abstract.text.replace('\n', '')
                rel = (1 if k == str(topic_train) else 0)
                id_left.append(str(k))
                text_left.append(v)
                id_right.append(pbmid_str)
                text_right.append(abstract_text)
                label.append(rel)

    df = pd.DataFrame(data={'text_left': text_left,
                            'id_left': id_left,
                            'text_right': text_right,
                            'id_right': id_right,
                            'label': label})

    return mz.pack(df)
