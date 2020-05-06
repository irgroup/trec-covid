DOCS = {'comm': './data/comm_use_subset/',
        'noncomm': './data/noncomm_use_subset/',
        'biorxiv': './data/biorxiv_medrxiv/',
        'custom': './data/custom_license/'}
TOPIC = './topics/topics-rnd1.xml'
IMAGE_TAG = 'elasticsearch:7.4.2'
CONTAINER_NAME = 'elasticsearch'
BULK = True
SINGLE_IDX = 'trec-covid'
BASELINE = 'trec-covid'
# SINGLE_IDX = None
DATA = './data'
META = './download/metadata.csv'
VALID_ID = './download/docids-rnd1.txt'
ESEARCH = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&sort=relevance&term='
ESEARCH_PMC = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&sort=relevance&term='
EFETCH = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id='
EFETCH_PMC = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id='
RETMODE = '&retmode=xml'
PUBMED_FETCH = './artifact/pubmed/'
PUBMED_DUMP_DATE = '2020-04-20'
MODEL_DUMP = './artifact/model/'
MODEL_TYPE = 'drmm'  # 'dense', 'drmm'
RUN_DIR = './artifact/runs/'
RERANKED_RUN = 'reranked_drmm'
RUN_TAG = 'irc_pubmed'  # 'irc_pubmed', 'irc_pmc', 'irc_entrez'

PUBMED_SCRAPE = False
PUBMED_FRONT = 'https://pubmed.ncbi.nlm.nih.gov/?term='
RESULT_SIZE = 20

FULLTEXT_PMC = False

RERANK_WEIGHT = 0.5

EMBEDDING = 'biowordvec'  # 'glove', 'biowordvec'
EMBED_DIR = './embedding/'
BIOWORDVEC = 'bio_embedding_intrinsic.txt'

ROUND = 2
QRELS_RND1 = '../qrels/qrels-rnd1.txt'