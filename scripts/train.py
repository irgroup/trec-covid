import os
import matchzoo as mz
from core.util import query_dict
from core.clf_mz import train
from config.config import TOPIC, EMBEDDING, EMBED_DIR, BIOWORDVEC


if __name__ == '__main__':

    if EMBEDDING == 'glove':
        embedding = mz.datasets.embeddings.load_glove_embedding(dimension=300)
    if EMBEDDING == 'biowordvec':
        embedding = mz.embedding.embedding.load_from_file(os.path.join(EMBED_DIR, BIOWORDVEC), mode='word2vec')

    for topic_number, query in query_dict(TOPIC).items():

        train(topic_number, embedding, model_type='drmm')
