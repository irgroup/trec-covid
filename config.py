docs = {
    'comm': './data/comm_use_subset/',
    'noncomm': './data/noncomm_use_subset/',
    'biorxiv': './data/biorxiv_medrxiv/',
    'custom': './data/custom_license/'
}
topic = './topics/topics-rnd1.xml'
BULK = True
SINGLE_IDX = 'trec-covid'
# SINGLE_IDX = None
META = './download/metadata.csv'
VALID_ID = './docids-rnd1.txt'
ESEARCH = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term='
EFETCH = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id='
RETMODE = '&retmode=xml'
PUBMED_FETCH = './artifact/pubmed/'