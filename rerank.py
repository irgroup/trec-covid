import os
import pandas as pd
import numpy as np
import matchzoo as mz
from config.config import META, MODEL_DUMP, MODEL_TYPE, RERANKED_RUN, DATA, RUN_DIR, BASELINE, RERANK_WEIGHT, TOPIC, RUN_TAG
from core.clf import get_model_and_data
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

        # get model and transformed data
        model, pred_x = get_model_and_data(topic_number, d_pack_test, model_type=MODEL_TYPE, embedding=glove_embedding)

        # predict score for each doc
        scores = model.predict(pred_x)

        # dict with score docid mapping
        id_score = {}
        for i in range(0, 1000):
            id_score[pred_x['id_right'][i]] = scores[i].item()

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
            id_score_normalized[pred_x['id_right'][i]] = sorted_scores_normalized[i].item()

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
