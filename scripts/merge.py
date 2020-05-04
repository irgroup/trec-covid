import os
import pandas as pd
from config.config import (META, MODEL_DUMP, MODEL_TYPE,
                           RERANKED_RUN, DATA, RUN_DIR,
                           BASELINE, RERANK_WEIGHT, TOPIC,
                           RUN_TAG, EMBEDDING, EMBED_DIR, BIOWORDVEC)
from core.util import query_dict, map_sha_path, test_data, train_data, merge_rankings


if __name__ == '__main__':

    # get baseline ranking from run file
    df_baseline = pd.read_csv(os.path.join(RUN_DIR, BASELINE),
                              sep=' ',
                              names=['topic', 'Q0', 'cord_uid', 'rank', 'score', 'team'],
                              index_col=False)

    # get reranking from run file
    df_rerank = pd.read_csv(os.path.join(RUN_DIR, RERANKED_RUN),
                              sep=' ',
                              names=['topic', 'Q0', 'cord_uid', 'rank', 'score', 'team'],
                              index_col=False)

    # merge rankings
    rank_merge = merge_rankings(df_baseline, df_rerank, RERANK_WEIGHT)

    # write output
    for topic_number, query in query_dict(TOPIC).items():
        count = 1
        with open(os.path.join(RUN_DIR, RUN_TAG), 'a') as run:
            for index, row in rank_merge.iterrows():
                line = topic_number + ' Q0 ' + row['cord_uid'] + ' ' + str(count) + ' ' + str(row['weighted_score']) + ' ' + RUN_TAG + '\n'
                run.write(line)
                count += 1
