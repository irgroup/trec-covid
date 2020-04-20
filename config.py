DOCS = {'comm': './data/comm_use_subset/',
        'noncomm': './data/noncomm_use_subset/',
        'biorxiv': './data/biorxiv_medrxiv/',
        'custom': './data/custom_license/'}
TOPIC = './topics/topics-rnd1.xml'
BULK = True
SINGLE_IDX = 'trec-covid'
BASELINE = 'trec-covid'
# SINGLE_IDX = None
DATA = './data'
META = './download/metadata.csv'
VALID_ID = './download/docids-rnd1.txt'
ESEARCH = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&sort=relevance&term='
EFETCH = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id='
RETMODE = '&retmode=xml'
PUBMED_FETCH = './artifact/pubmed/'
PUBMED_DUMP_DATE = '2020-04-19'
MODEL_DUMP = './artifact/model/'
MODEL_TYPE = 'drmm'  # 'dense', 'drmm'
RUN_DIR = './artifact/runs/'
RERANKED_RUN = 'reranked_drmm'

PUBMED_SCRAPE = True
PUBMED_FRONT = 'https://pubmed.ncbi.nlm.nih.gov/?term='
RESULT_SIZE = 20

RERANK_WEIGHT = 0.5
