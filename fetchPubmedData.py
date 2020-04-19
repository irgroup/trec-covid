import os
import time
import requests as rq
from bs4 import BeautifulSoup
from datetime import datetime

from config import EFETCH, ESEARCH, RETMODE, PUBMED_FETCH, topic
from util import query_dict

queries = query_dict(topic)

now = datetime.now()
data_str = now.date().strftime("%Y-%m-%d")

if not os.path.exists(PUBMED_FETCH + data_str):
    os.makedirs(PUBMED_FETCH + data_str)

for k,v in queries.items():
    res = rq.get(ESEARCH + v)

    soup = BeautifulSoup(res.content, 'lxml')
    ids = ''
    for id_field in soup.idlist.find_all('id'):
        ids = ids + id_field.text + ','

    res = rq.get(EFETCH + ids + RETMODE)

    soup = BeautifulSoup(res.content, 'lxml')

    file_path = os.path.join(PUBMED_FETCH, data_str, str(k)+'.xml')
    with open(file_path, 'w') as out:
        out.write(soup.prettify())
    time.sleep(5)
