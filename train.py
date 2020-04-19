import os
import matchzoo as mz
from util import train_data, query_dict
from config import MODEL_DUMP, MODEL_TYPE, topic


if __name__ == '__main__':

    for topic_number, query in query_dict(topic).items():
        task = mz.tasks.Ranking()
        train_raw = train_data(topic_number)
        preprocessor = mz.preprocessors.BasicPreprocessor()
        preprocessor.fit(train_raw)
        train_processed = preprocessor.transform(train_raw)
        train_processed.left.head()

        model = mz.models.DenseBaseline()
        model.params['task'] = task
        model.params.update(preprocessor.context)
        model.guess_and_fill_missing_params(verbose=0)
        model.params['mlp_num_fan_out'] = 30

        if model.params.completed():
            model.build()
            model.compile()
            x, y = train_processed.unpack()
            model.fit(x, y, batch_size=32, epochs=5)
            if not os.path.exists(os.path.join(MODEL_DUMP, MODEL_TYPE)):
                os.makedirs(os.path.join(MODEL_DUMP, MODEL_TYPE))
            model.save(os.path.join(MODEL_DUMP, MODEL_TYPE, str(topic_number)))
