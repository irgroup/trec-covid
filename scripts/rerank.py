import os
import pandas as pd
import matchzoo as mz
from config.config import (META, MODEL_DUMP, MODEL_TYPE,
                           RERANKED_RUN, DATA, RUN_DIR,
                           BASELINE, RERANK_WEIGHT, TOPIC,
                           RUN_TAG, EMBEDDING, EMBED_DIR, BIOWORDVEC)
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

    if EMBEDDING == 'glove':
        embedding = mz.datasets.embeddings.load_glove_embedding(dimension=300)
    if EMBEDDING == 'biowordvec':
        embedding = mz.embedding.embedding.load_from_file(os.path.join(EMBED_DIR, BIOWORDVEC), mode='word2vec')

    for topic_number, query in query_dict(TOPIC).items():
        topic_df = df_baseline[df_baseline['topic'] == int(topic_number)]
        cord_uids = topic_df['cord_uid']

        # make datapack
        d_pack_test = test_data(topic_number, cord_uids, query, meta, msp)

        # get model and transformed data
        model, pred_x = get_model_and_data(topic_number, d_pack_test, model_type=MODEL_TYPE, embedding=embedding)

        # predict score for each doc
        scores = model.predict(pred_x)

        # dict with score docid mapping
        id_score = {}
        for i in range(0, 1000):
            id_score[pred_x['id_right'][i]] = scores[i].item()

        # sort by descending score (rerank)
        id_score_sort = {k: v for k, v in sorted(id_score.items(), key=lambda item: item[1], reverse=True)}

        # write output
        count = 1
        with open(os.path.join(RUN_DIR, RERANKED_RUN), 'a') as run:
            for cord_uid, score in id_score_sort.items():
                line = topic_number + ' Q0 ' + cord_uid + ' ' + str(count) + ' ' + str(score) + ' ' + RUN_TAG + '\n'
                run.write(line)
                count += 1
