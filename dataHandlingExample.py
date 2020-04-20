import os
import pandas as pd
from bs4 import BeautifulSoup as bs
import matchzoo as mz
from config import TOPIC, PUBMED_FETCH, PUBMED_DUMP_DATE
from util import query_dict

topic_train = 1
queries = query_dict(TOPIC)

text_left = []
id_left = []
text_right = []
id_right = []
label = []

if __name__ == '__main__':
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

    d_pack = mz.pack(df)

    print(d_pack.left.head())
    print(d_pack.right.head())
    print(d_pack.relation.head())
    print(d_pack.relation.tail())
