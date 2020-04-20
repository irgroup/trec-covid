import os
import time
import requests as rq
from bs4 import BeautifulSoup
from datetime import datetime

from config import EFETCH, ESEARCH, RETMODE, PUBMED_FETCH, PUBMED_SCRAPE, PUBMED_FRONT, RESULT_SIZE, TOPIC
from util import query_dict

queries = query_dict(TOPIC)

now = datetime.now()
date_str = now.date().strftime("%Y-%m-%d")

if not os.path.exists(PUBMED_FETCH + date_str):
    os.makedirs(PUBMED_FETCH + date_str)

for k, v in queries.items():

    if PUBMED_SCRAPE:
        res = rq.get(PUBMED_FRONT + v + '&size=' + str(RESULT_SIZE))
        soup = BeautifulSoup(res.content, 'lxml')

        ids = ''
        for id_field in soup.find_all('span', {"class": "docsum-pmid"}):
            ids = ids + id_field.text + ','
    else:
        res = rq.get(ESEARCH + v)
        soup = BeautifulSoup(res.content, 'lxml')
        ids = ''
        for id_field in soup.idlist.find_all('id'):
            ids = ids + id_field.text + ','

    res = rq.get(EFETCH + ids + RETMODE)

    soup = BeautifulSoup(res.content, 'lxml')

    file_path = os.path.join(PUBMED_FETCH, date_str, str(k)+'.xml')
    with open(file_path, 'w') as out:
        out.write(soup.prettify())
    time.sleep(5)
