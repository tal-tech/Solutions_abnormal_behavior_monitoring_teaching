
import joblib
import numpy as np
import os
import re
import sys
import logging
import pickle
import tensorflow as tf

base_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base_path, 'tools'))
from embeddingTool import RedisEmbeddingFeature,EmbeddingFeature
sys.path.append(os.path.join(base_path, '../../config/'))
model_jabber_bilstm_path = os.path.join(
    base_path, '../../data/base/model/jabber_bi_lism.model')
model_jabber_bilstm = pickle.load(open(model_jabber_bilstm_path,'rb'))
embedding_path = os.path.join(
    base_path, '../../data/base/model/jabberEmbedding_small.plk')
# config
max_timesteps = 3000
max_len = 20
embedding_dim = 64
threshold = 0.85
embedding_dim = 64
feature_dim = embedding_dim

normal_emb = EmbeddingFeature(embedding_path,embedding_dim)
graph = tf.get_default_graph()

def predict_jabber_sentence_list(course_text,clear_cache=True):
    text_list = course_text.text.tolist()
    # get feature
    feature_list = normal_emb.get_sentence_list_embedding_mean(text_list,max_len)
    feature_size = feature_list.shape[0]
    X = np.zeros((1,max_timesteps,feature_dim)) - 1
    # cut off feature_list
    X[0,:feature_size,:] = feature_list[:max_timesteps,:]
    logging.info('Start use bilstm to predict')
    with graph.as_default():
        label = [int(x) for x in model_jabber_bilstm.predict(X)[0,:feature_size]>threshold]
    logging.info('Precit finish!')
#     check feature size
    if feature_size>max_timesteps:
        label = label+[0]*(feature_size - max_timesteps)
    logging.info('Mean label:{}'.format(np.array(label).mean()))
    return label