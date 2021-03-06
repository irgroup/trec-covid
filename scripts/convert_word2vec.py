import os
import gensim
from core.util import mkdir
from config.config import EMBED_DIR


if __name__ == '__main__':
    model = gensim.models.KeyedVectors.load_word2vec_format('./download/12551759', binary=True)
    mkdir(EMBED_DIR)
    model.save_word2vec_format(os.path.join(EMBED_DIR, 'bio_embedding_intrinsic.txt'), binary=False)
    os.system("gzip -k bio_embedding_intrinsic.txt")
    os.system("python -m spacy init-model en ./embedding/spacy.bioemb.model --vectors-loc ./embedding/bio_embedding_intrinsic.txt.gz")