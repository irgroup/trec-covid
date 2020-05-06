# data collections
# DOCS = {'comm': './data/comm_use_subset/',
#         'noncomm': './data/noncomm_use_subset/',
#         'biorxiv': './data/biorxiv_medrxiv/',
#         'custom': './data/custom_license/'}
DOCS = {'arxiv': './data/round02/arxiv',
        'comm': './data/round02/comm_use_subset/',
        'noncomm': './data/round02/noncomm_use_subset/',
        'biorxiv': './data/round02/biorxiv_medrxiv/',
        'custom': './data/round02/custom_license/'}

# elastic baseline
IMAGE_TAG = 'elasticsearch:7.4.2'
CONTAINER_NAME = 'elasticsearch'
BULK = True
SINGLE_IDX = 'trec-covid'
# SINGLE_IDX = None
BASELINE = 'trec-covid'

#
ROUND = 2
QRELS_RND1 = '../qrels/qrels-rnd1.txt'
ALTMETRIC = '../data/trec_covid_final.xlsx'
# TOPIC = './topics/topics-rnd1.xml'
TOPIC = './topics/topics-rnd2.xml'
# DATA = './data'
DATA = './data/round2'
# META = './download/metadata-rnd1.csv'
META = './download/metadata-rnd2.csv'
# VALID_ID = './download/docids-rnd1.txt'
VALID_ID = './download/docids-rnd2.txt'

# run dir
RUN_DIR = './artifact/runs/'
RERANKED_RUN = 'irc_bm25_altmetric'
RUN_TAG = 'irc_bm25_altmetric'  # 'irc_pubmed', 'irc_pmc', 'irc_entrez'

# pubmed
PUBMED_SCRAPE = False
FULLTEXT_PMC = False
PUBMED_FRONT = 'https://pubmed.ncbi.nlm.nih.gov/?term='
RESULT_SIZE = 20
ESEARCH = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&sort=relevance&term='
ESEARCH_PMC = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&sort=relevance&term='
EFETCH = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id='
EFETCH_PMC = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id='
RETMODE = '&retmode=xml'
PUBMED_FETCH = './artifact/pubmed/'
PUBMED_DUMP_DATE = '2020-04-20'

# drmm and embeddings
MODEL_DUMP = './artifact/model/'
MODEL_TYPE = 'drmm'  # 'dense', 'drmm'
EMBEDDING = 'biowordvec'  # 'glove', 'biowordvec'
EMBED_DIR = './embedding/'
BIOWORDVEC = 'bio_embedding_intrinsic.txt'
RERANK_WEIGHT = 0.5

