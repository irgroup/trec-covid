import os
import numpy as np
import matchzoo as mz
from util import train_data, query_dict
from config import MODEL_DUMP, MODEL_TYPE, TOPIC


if __name__ == '__main__':

    for topic_number, query in query_dict(TOPIC).items():

        if MODEL_TYPE == 'dense':
            task = mz.tasks.Ranking()
            train_raw = train_data(topic_number)
            preprocessor = mz.preprocessors.BasicPreprocessor()
            preprocessor.fit(train_raw)
            train_processed = preprocessor.transform(train_raw)

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

        if MODEL_TYPE == 'drmm':
            task = mz.tasks.Ranking()
            train_raw = train_data(topic_number)
            preprocessor = mz.preprocessors.BasicPreprocessor(fixed_length_left=10,
                                                              fixed_length_right=100,
                                                              remove_stop_words=False)
            preprocessor.fit(train_raw)
            train_processed = preprocessor.transform(train_raw)
            glove_embedding = mz.datasets.embeddings.load_glove_embedding(dimension=300)
            bin_size = 30
            model = mz.models.DRMM()
            model.params.update(preprocessor.context)
            model.params['input_shapes'] = [[10, ], [10, bin_size, ]]
            model.params['task'] = task
            model.params['mask_value'] = 0
            model.params['embedding_output_dim'] = glove_embedding.output_dim
            model.params['mlp_num_layers'] = 1
            model.params['mlp_num_units'] = 10
            model.params['mlp_num_fan_out'] = 1
            model.params['mlp_activation_func'] = 'tanh'
            model.params['optimizer'] = 'adadelta'

            if model.params.completed():
                model.build()
                model.compile()
                embedding_matrix = glove_embedding.build_matrix(preprocessor.context['vocab_unit'].state['term_index'])
                # normalize the word embedding for fast histogram generating.
                l2_norm = np.sqrt((embedding_matrix * embedding_matrix).sum(axis=1))
                embedding_matrix = embedding_matrix / l2_norm[:, np.newaxis]
                model.load_embedding_matrix(embedding_matrix)
                hist_callback = mz.data_generator.callbacks.Histogram(embedding_matrix,
                                                                      bin_size=30,
                                                                      hist_mode='LCH')
                train_generator = mz.DataGenerator(train_processed,
                                                   mode='point',
                                                   num_dup=5,
                                                   num_neg=10,
                                                   batch_size=20,
                                                   callbacks=[hist_callback])
                history = model.fit_generator(train_generator,
                                              epochs=30,
                                              workers=30,
                                              use_multiprocessing=True)

                if not os.path.exists(os.path.join(MODEL_DUMP, MODEL_TYPE)):
                    os.makedirs(os.path.join(MODEL_DUMP, MODEL_TYPE))
                model.save(os.path.join(MODEL_DUMP, MODEL_TYPE, str(topic_number)))
