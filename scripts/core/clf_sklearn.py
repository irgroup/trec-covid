from core.util import query_dict, map_sha_path, text
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np


def sk_train_data(qrels, meta, msp, topic_train):

    x = []
    y = []
    txt_list = []
    for idx, row in qrels[qrels['topic'] == int(topic_train)].iterrows():
        sha = meta[meta['cord_uid'] == row['docid']]['sha']
        if sha.empty:
            continue
        try:
            path = msp[sha.values[0]]
            with open(path, 'r') as open_file:
                txt_list.append(text(open_file.read()))
        except:
            continue

    vectorizer = TfidfVectorizer()
    vectorizer.fit_transform(txt_list)

    for idx, row in qrels[qrels['topic'] == int(topic_train)].iterrows():
        sha = meta[meta['cord_uid'] == row['docid']]['sha']
        if sha.empty:
            continue
        try:
            path = msp[sha.values[0]]
            with open(path, 'r') as open_file:

                txt = text(open_file.read())
                x.append(np.array(vectorizer.transform([txt]).todense()).flatten())
                rel = (1 if int(row['rel']) > 0 else 0)
                y.append(rel)
        except Exception as e:
            continue

    return vectorizer, x, y