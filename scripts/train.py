from core.util import query_dict
from core.clf import train
from config.config import TOPIC


if __name__ == '__main__':

    for topic_number, query in query_dict(TOPIC).items():

        train(topic_number, model_type='drmm')
