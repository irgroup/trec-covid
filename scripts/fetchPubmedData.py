from config.config import TOPIC, PUBMED_FETCH
from core.util import query_dict, mkdir, date_str
from core.pubmed import fetch


if __name__ == '__main__':
    queries = query_dict(TOPIC)
    today_str = date_str()
    mkdir(PUBMED_FETCH + today_str)
    fetch(queries, today_str)
