import os
import math
import pandas as pd
from tqdm import tqdm
from config.config import (META, MODEL_DUMP, MODEL_TYPE,
                           RERANKED_RUN, DATA, RUN_DIR,
                           BASELINE, RERANK_WEIGHT, TOPIC,
                           RUN_TAG, EMBEDDING, EMBED_DIR, BIOWORDVEC,
                           ROUND, ALTMETRIC)
from core.util import query_dict, map_sha_path, merge_rankings


if __name__ == '__main__':

    if ROUND == 1:
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

    if ROUND == 2:
        # get baseline ranking from run file
        df_baseline = pd.read_csv(os.path.join(RUN_DIR, BASELINE),
                                  sep=' ',
                                  names=['topic', 'Q0', 'cord_uid', 'rank', 'score', 'team'],
                                  index_col=False)

        print('load altmetrics')
        df_altmetric = pd.read_excel(ALTMETRIC)

        for topic_number, query in query_dict(TOPIC).items():
            df_topic = df_baseline[df_baseline['topic'] == int(topic_number)]

            print('Add attention score for topic with number', topic_number)
            with tqdm(total=len(df_topic)) as pbar:
                for index, row in df_topic.iterrows():
                    attention_score = df_altmetric[df_altmetric['CORD_UID'] == row['cord_uid']]['ATTENTION_SCORE']
                    if attention_score.empty:
                        pbar.update(1)
                        continue
                    up = df_topic[df_topic['cord_uid'] == row['cord_uid']]['score'] + math.log(
                        1 + attention_score.values[0])
                    df_topic.update(up)
                    pbar.update(1)

            df_topic_sorted = df_topic.sort_values('score', ascending=False)

            count = 1
            with open(os.path.join(RUN_DIR, RUN_TAG), 'a') as run:
                for index, row in df_topic_sorted.iterrows():
                    line = topic_number + ' Q0 ' + row['cord_uid'] + ' ' + str(count) + ' ' + str(
                        row['score']) + ' ' + RUN_TAG + '\n'
                    run.write(line)
                    count += 1