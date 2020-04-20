import os
import pandas as pd
import numpy as np
import matchzoo as mz
from config import META, MODEL_DUMP, MODEL_TYPE, RERANKED_RUN, DATA, RUN_DIR, BASELINE, topic
from util import query_dict, map_sha_path, test_data, train_data


if __name__ == '__main__':
    msp = map_sha_path(DATA)
    meta = pd.read_csv(META)
    meta = meta[meta['sha'].notna()]  # there are duplicates in metadata.csv, some without sha

    # get baseline ranking from run
    df_baseline = pd.read_csv(os.path.join(RUN_DIR, BASELINE),
                              sep=' ',
                              names=['topic', 'Q0', 'cord_uid', 'rank', 'score', 'team'],
                              index_col=False)

    glove_embedding = mz.datasets.embeddings.load_glove_embedding(dimension=300)

    with open(os.path.join(RUN_DIR, RERANKED_RUN), 'w') as run:
        for topic_number, query in query_dict(topic).items():
            topic_df = df_baseline[df_baseline['topic'] == int(topic_number)]
            cord_uids = topic_df['cord_uid']

            # make datapack
            d_pack_test = test_data(topic_number, cord_uids, query, meta, msp)

            if MODEL_TYPE == 'dense':
                # load model
                model = mz.load_model(os.path.join(MODEL_DUMP, MODEL_TYPE, str(topic_number)))

                # prepare preprocessor
                train_raw = train_data(topic_number)
                preprocessor = mz.preprocessors.BasicPreprocessor()
                preprocessor.fit(train_raw)

                # transform document data
                test_processed = preprocessor.transform(d_pack_test)
                test_x, test_y = test_processed.unpack()

            if MODEL_TYPE == 'drmm':
                # load model
                model = mz.load_model(os.path.join(MODEL_DUMP, MODEL_TYPE, str(topic_number)))
                task = mz.tasks.Ranking()
                train_raw = train_data(topic_number)
                preprocessor = mz.preprocessors.BasicPreprocessor(fixed_length_left=10,
                                                                  fixed_length_right=100,
                                                                  remove_stop_words=False)
                preprocessor.fit(train_raw)

                test_processed = preprocessor.transform(d_pack_test)
                embedding_matrix = glove_embedding.build_matrix(preprocessor.context['vocab_unit'].state['term_index'])
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

            # predict score for each doc
            scores = model.predict(test_x)

            # dict with score docid mapping
            id_score = {}
            for i in range(0, 1000):
                id_score[test_x['id_right'][i]] = scores[i].item()

            # sort by descending score (rerank)
            id_score_sort = {k: v for k, v in sorted(id_score.items(), key=lambda item: item[1], reverse=True)}

            # write output
            count = 1
            for cord_uid, score in id_score_sort.items():
                line = topic_number + ' Q0 ' + cord_uid + ' ' + str(count) + ' ' + str(score) + ' IRC ' + '\n'
                run.write(line)
                count += 1
