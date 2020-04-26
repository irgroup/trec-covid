import os
import pandas as pd
import numpy as np
import matchzoo as mz
from config.config import META, MODEL_DUMP, MODEL_TYPE, RERANKED_RUN, DATA, RUN_DIR, BASELINE, RERANK_WEIGHT, TOPIC, RUN_TAG
from core.util import query_dict, map_sha_path, test_data, train_data


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


    for topic_number, query in query_dict(TOPIC).items():
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


        # normalize baseline scores
        baseline_score_normalized = (topic_df['score'] - topic_df['score'].min()) / (
                    topic_df['score'].max() - topic_df['score'].min())

        # normalize rerank scores
        sorted_scores = np.fromiter(id_score_sort.values(), dtype=float)
        sorted_scores_normalized = (sorted_scores - sorted_scores.min()) / (
                    sorted_scores.max() - sorted_scores.min())

        # merge scores and ids into one data frame
        df_scores = pd.DataFrame({'cord_uid': cord_uids,
                                  'base_score': baseline_score_normalized,
                                  'rerank_score': baseline_score_normalized})

        id_score_normalized = {}
        for i in range(0, 1000):
            id_score_normalized[test_x['id_right'][i]] = sorted_scores_normalized[i].item()

        for cord_uid, score in id_score_normalized.items():
            df_scores.at[df_scores[df_scores['cord_uid'] == cord_uid].index, 'rerank_score'] = score

        weighted = ((1 - RERANK_WEIGHT) * df_scores['base_score'] + RERANK_WEIGHT * df_scores['rerank_score'])

        final_score = pd.DataFrame({'cord_uid': df_scores['cord_uid'], 'weighted_score': weighted})
        final_score_sorted = final_score.sort_values(by=['weighted_score'], ascending=False)

        # write output
        count = 1
        with open(os.path.join(RUN_DIR, RERANKED_RUN), 'a') as run:
            for index, row in final_score_sorted.iterrows():
                line = topic_number + ' Q0 ' + row['cord_uid'] + ' ' + str(count) + ' ' + str(row['weighted_score']) + ' ' + RUN_TAG + '\n'
                run.write(line)
                count += 1
