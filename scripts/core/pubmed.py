import os
import time
import requests as rq
from bs4 import BeautifulSoup

from config.config import (EFETCH, ESEARCH, RETMODE, PUBMED_FETCH, PUBMED_SCRAPE,
                           PUBMED_FRONT, RESULT_SIZE, ESEARCH_PMC, EFETCH_PMC,
                           FULLTEXT_PMC)


def fetch(queries, date_str):
    for k, v in queries.items():

        if PUBMED_SCRAPE:
            res = rq.get(PUBMED_FRONT + v + '&size=' + str(RESULT_SIZE))
            soup = BeautifulSoup(res.content, 'lxml')

            ids = ''
            for id_field in soup.find_all('span', {"class": "docsum-pmid"}):
                ids = ids + id_field.text + ','
        else:
            if FULLTEXT_PMC:
                res = rq.get(ESEARCH_PMC + v)
            else:
                res = rq.get(ESEARCH + v)

            soup = BeautifulSoup(res.content, 'lxml')
            ids = ''
            for id_field in soup.idlist.find_all('id'):
                ids = ids + id_field.text + ','

        if FULLTEXT_PMC:
            res = rq.get(EFETCH_PMC + ids + RETMODE)
        else:
            res = rq.get(EFETCH + ids + RETMODE)

        soup = BeautifulSoup(res.content, 'lxml')

        file_path = os.path.join(PUBMED_FETCH, date_str, str(k) + '.xml')
        with open(file_path, 'w') as out:
            out.write(soup.prettify())
        time.sleep(5)
