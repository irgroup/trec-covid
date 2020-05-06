import os
import numpy as np
import pandas as pd
import matchzoo as mz
from bs4 import BeautifulSoup as bs
from core.util import text, query_dict
from config.config import MODEL_DUMP, MODEL_TYPE, TOPIC, FULLTEXT_PMC, PUBMED_FETCH, PUBMED_DUMP_DATE


def dense_preprocess(train_raw, task):
    preprocessor = mz.preprocessors.BasicPreprocessor()
    preprocessor.fit(train_raw)
    train_processed = preprocessor.transform(train_raw)
    model = mz.models.DenseBaseline()
    model.params['task'] = task
    model.params.update(preprocessor.context)
    model.guess_and_fill_missing_params(verbose=0)
    model.params['mlp_num_fan_out'] = 30
    return train_processed, model


def drmm_preprocess(train_raw, task, embed_out_dim):
    preprocessor = mz.preprocessors.BasicPreprocessor(fixed_length_left=10,
                                                      fixed_length_right=100,
                                                      remove_stop_words=False)
    preprocessor.fit(train_raw)
    train_processed = preprocessor.transform(train_raw)
    bin_size = 30
    model = mz.models.DRMM()
    model.params.update(preprocessor.context)
    model.params['input_shapes'] = [[10, ], [10, bin_size, ]]
    model.params['task'] = task
    model.params['mask_value'] = 0
    model.params['embedding_output_dim'] = embed_out_dim
    model.params['mlp_num_layers'] = 1
    model.params['mlp_num_units'] = 10
    model.params['mlp_num_fan_out'] = 1
    model.params['mlp_activation_func'] = 'tanh'
    model.params['optimizer'] = 'adadelta'

    return train_processed, preprocessor, model


def train(topic_number, embedding, model_type='drmm'):

    task = mz.tasks.Ranking()
    train_raw = train_data(topic_number)

    if model_type == 'dense':
        train_processed, model = dense_preprocess(train_raw, task)
        if model.params.completed():
            model.build()
            model.compile()
            x, y = train_processed.unpack()
            model.fit(x, y, batch_size=32, epochs=5)
            if not os.path.exists(os.path.join(MODEL_DUMP, MODEL_TYPE)):
                os.makedirs(os.path.join(MODEL_DUMP, MODEL_TYPE))
            model.save(os.path.join(MODEL_DUMP, MODEL_TYPE, str(topic_number)))

    if model_type == 'drmm':
        # glove_embedding = mz.datasets.embeddings.load_glove_embedding(dimension=300)
        train_processed, preprocessor, model = drmm_preprocess(train_raw, task, embed_out_dim=embedding.output_dim)

        if model.params.completed():
            model.build()
            model.compile()
            embedding_matrix = embedding.build_matrix(preprocessor.context['vocab_unit'].state['term_index'])
            # normalize the word embedding for fast histogram generating.
            l2_norm = np.sqrt((embedding_matrix * embedding_matrix).sum(axis=1))
            embedding_matrix = embedding_matrix / l2_norm[:, np.newaxis]
            model.load_embedding_matrix(embedding_matrix)
            hist_callback = mz.data_generator.callbacks.Histogram(embedding_matrix,
                                                                  bin_size=30,
                                                                  hist_mode='LCH')
            train_generator = mz.DataGenerator(train_processed,
                                               mode='point',
                                               num_dup=5,
                                               num_neg=10,
                                               batch_size=20,
                                               callbacks=[hist_callback])
            history = model.fit_generator(train_generator,
                                          epochs=30,
                                          workers=30,
                                          use_multiprocessing=True)

            if not os.path.exists(os.path.join(MODEL_DUMP, MODEL_TYPE)):
                os.makedirs(os.path.join(MODEL_DUMP, MODEL_TYPE))
            model.save(os.path.join(MODEL_DUMP, MODEL_TYPE, str(topic_number)))


def get_model_and_data(topic_number, d_pack_test, model_type, embedding):

    if model_type == 'dense':
        # load model
        model = mz.load_model(os.path.join(MODEL_DUMP, MODEL_TYPE, str(topic_number)))

        # prepare preprocessor
        train_raw = train_data(topic_number)
        preprocessor = mz.preprocessors.BasicPreprocessor()
        preprocessor.fit(train_raw)

        # transform document data
        test_processed = preprocessor.transform(d_pack_test)
        test_x, test_y = test_processed.unpack()

    if model_type == 'drmm':
        # load model
        model = mz.load_model(os.path.join(MODEL_DUMP, MODEL_TYPE, str(topic_number)))
        task = mz.tasks.Ranking()
        train_raw = train_data(topic_number)
        preprocessor = mz.preprocessors.BasicPreprocessor(fixed_length_left=10,
                                                          fixed_length_right=100,
                                                          remove_stop_words=False)
        preprocessor.fit(train_raw)

        test_processed = preprocessor.transform(d_pack_test)
        embedding_matrix = embedding.build_matrix(preprocessor.context['vocab_unit'].state['term_index'])
        # normalize the word embedding for fast histogram generating.
        l2_norm = np.sqrt((embedding_matrix * embedding_matrix).sum(axis=1))
        embedding_matrix = embedding_matrix / l2_norm[:, np.newaxis]
        model.load_embedding_matrix(embedding_matrix)
        hist_callback = mz.data_generator.callbacks.Histogram(embedding_matrix,
                                                              bin_size=30,
                                                              hist_mode='LCH')
        test_generator = mz.DataGenerator(data_pack=test_processed, mode='point',
                                          callbacks=[hist_callback])
        test_x, test_y = test_generator[:]

    return model, test_x


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