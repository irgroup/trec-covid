import os
import gensim
from core.util import mkdir
from config.config import EMBED_DIR


if __name__ == '__main__':
    model = gensim.models.KeyedVectors.load_word2vec_format('./download/bio_embedding_intrinsic', binary=True)
    mkdir(EMBED_DIR)
    model.save_word2vec_format(os.path.join(EMBED_DIR, 'bio_embedding_intrinsic.txt'), binary=False)