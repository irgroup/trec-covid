import os
import json
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup as bs
import matchzoo as mz
from config.config import TOPIC, PUBMED_FETCH, PUBMED_DUMP_DATE, FULLTEXT_PMC, RERANK_WEIGHT
from PyPDF2 import PdfFileReader


def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def date_str():
    now = datetime.now()
    return now.date().strftime("%Y-%m-%d")


def text_from_pdf(file):
    txt = ''
    with open(file, "rb") as filehandle:
        pdf = PdfFileReader(filehandle)
        txt = ''
        for nr in range(0, pdf.getNumPages()):
            page = pdf.getPage(nr)
            txt += page.extractText()
    return txt


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
    queries = query_dict(TOPIC)

    text_left = []
    id_left = []
    text_right = []
    id_right = []
    label = []

    for k, v in queries.items():
        file_path = os.path.join(PUBMED_FETCH, PUBMED_DUMP_DATE, str(k)+'.xml')
        with open(file_path, 'r') as input:
            soup = bs(input.read(), 'lxml')

            if FULLTEXT_PMC:
                articles = soup.find('pmc-articleset').find_all('article')
                for article in articles:
                    pbmid_str = article.find("article-id", {"pub-id-type": "pmc"}).text.replace('\n', ' ').strip()
                    txt = ''
                    abstract = article.abstract
                    if abstract:
                        txt = abstract.text.replace('\n', ' ').strip(' ')
                    sections = article.find_all('sec')
                    titles = article.find_all('article-title')

                    for title in titles:
                        title_text = title.text.replace('\n', ' ').strip(' ')
                        ''.join([txt, ' ', title_text])
                    for section in sections:
                        section_text = section.text.replace('\n', '').strip(' ')
                        ''.join([txt, ' ', section_text])

                    rel = (1 if k == str(topic_train) else 0)
                    id_left.append(str(k))
                    text_left.append(v)
                    id_right.append(pbmid_str)
                    text_right.append(txt)
                    label.append(rel)

            else:
                articles = soup.find_all('pubmedarticle')
                for article in articles:
                    pbmid = article.find('articleid', {"idtype": "pubmed"})
                    pbmid_str = pbmid.text.replace('\n', '').strip()
                    abstract = article.find('abstract')
                    if abstract is None:
                        continue
                    else:
                        abstract_text = abstract.text.replace('\n', '')

                    title = article.articletitle.text.replace('\n', '').strip()
                    txt = title + abstract_text

                    rel = (1 if k == str(topic_train) else 0)
                    id_left.append(str(k))
                    text_left.append(v)
                    id_right.append(pbmid_str)
                    text_right.append(txt)
                    label.append(rel)

    df = pd.DataFrame(data={'text_left': text_left,
                            'id_left': id_left,
                            'text_right': text_right,
                            'id_right': id_right,
                            'label': label})

    return mz.pack(df)


def map_sha_path(dir):
    out = {}
    for path, subdir, file in os.walk(dir):
        extensions = tuple([".json"])
        files = [f for f in file if f.endswith(extensions)]
        for f in files:
            out[f[:-5]] = os.path.join(path, f)
    return out


def text(file):
    j = json.loads(file)
    body_text = ''
    for t in j['body_text']:
        body_text = body_text + t.get('text')

    abstract = ''
    if j.get('abstract') is not None:
        for t in j.get('abstract'):
            abstract = abstract + t.get('text')

    return abstract + ' ' + body_text


def test_data(topic_number, cord_uids, query, meta, msp):
    text_left = []
    id_left = []
    text_right = []
    id_right = []
    label = []
    for cord_uid in cord_uids:
        sha = meta[meta['cord_uid'] == cord_uid]['sha'].values[0]
        path = msp[sha]
        with open(path, 'r') as open_file:
            txt = text(open_file.read())
            id_left.append(str(topic_number))
            text_left.append(query)
            id_right.append(cord_uid)
            text_right.append(txt)
            label.append(0)

            df = pd.DataFrame(data={'text_left': text_left,
                                    'id_left': id_left,
                                    'text_right': text_right,
                                    'id_right': id_right,
                                    'label': label})

    return mz.pack(df)


def merge_rankings(df_baseline, df_rerank, rerank_weight):
    for topic_number, query in query_dict(TOPIC).items():
        topic_base = df_baseline[df_baseline['topic'] == int(topic_number)]
        cord_uids_base = topic_base['cord_uid']
        topic_rerank = df_rerank[df_rerank['topic'] == int(topic_number)]
        cord_uids_rerank = topic_rerank['cord_uid']

        # normalize baseline scores
        baseline_score_normalized = (topic_base['score'] - topic_base['score'].min()) / (
                    topic_base['score'].max() - topic_base['score'].min())

        # normalize rerank scores
        rerank_score_normalized = (topic_rerank['score'] - topic_rerank['score'].min()) / (
                    topic_rerank['score'].max() - topic_rerank['score'].min())

        # merge scores and ids into one data frame
        df_scores = pd.DataFrame({'cord_uid': cord_uids_base,
                                  'base_score': baseline_score_normalized,
                                  'rerank_score': baseline_score_normalized})

        df_rerank_norm = pd.DataFrame({'cord_uid': cord_uids_rerank,
                                       'rerank_score': rerank_score_normalized})

        for index, row in df_rerank_norm.iterrows():
            df_scores.at[df_scores[df_scores['cord_uid'] == row['cord_uid']].index, 'rerank_score'] = row['rerank_score']

        weighted = ((1 - rerank_weight) * df_scores['base_score'] + rerank_weight * df_scores['rerank_score'])
        final_score = pd.DataFrame({'cord_uid': df_scores['cord_uid'], 'weighted_score': weighted})

        return final_score.sort_values(by=['weighted_score'], ascending=False)
