from bs4 import BeautifulSoup

def query_dict(topic_file):
    queries = {}
    with open(topic_file, 'r') as topic:
        soup = BeautifulSoup(topic.read(), 'lxml')
        for top in soup.find_all('topic'):
            num = top.attrs.get('number')
            query = top.query.text
            question = top.question.text
            narrative = top.narrative.text

            queries[num] = query

    return queries