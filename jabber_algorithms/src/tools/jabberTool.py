import os
#import redis
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
import gensim
from gensim.models import word2vec
from sklearn.externals import joblib
import jieba
from basic_module import *

basePath = os.path.dirname(os.path.realpath(__file__))

# this part we set the default param
# @max_len: control the max length of the sentence
# @embedding_dim: control the dim of the word embedding
max_len = 20
embedding_dim = 64
use_redis = False
default_embedding = np.array([0.] * embedding_dim, dtype=np.float32)
n_right = 14
n_left = 14

gbdt_model_path = os.path.join(basePath,'../../data/base/model/jabber_model.model')
jabber_model = joblib.load(gbdt_model_path)

class jabberClassifier(object):
    def __init__(self, embedding_path='./', gbdt_model_path=None):
        if not use_redis:
            self.model = gensim.models.KeyedVectors.load_word2vec_format(
                embedding_path, binary=True)
        if gbdt_model_path is None:
            self.gbdt_model = jabber_model
        else:
            self.gbdt_model = joblib.load(gbdt_model_path)

    def init_cache(self):
        self.sentence_2_word = {}
        self.w2v = {}

    def set_dict(self, text_list):
        cut_words = []
        for sentence in text_list:
            if sentence in self.sentence_2_word:
                words = self.sentence_2_word[sentence]
            else:
                words = jieba.lcut(sentence)[:max_len]
                self.sentence_2_word[sentence] = words
            cut_words.extend(words)
        cut_words = list(set(cut_words))
        embedding_result = [
            get_word_vector(x, embedding_dim) for x in cut_words
        ]
        for word, embedding in zip(cut_words, embedding_result):
            if embedding != [0.] * embedding_dim:
                self.w2v[word] = embedding

    def init_course(self, course_text):
        data = json.loads(course_text)
        text_list = data["text_default"]
        text_list = [s["text"] for s in text_list]
        self.set_dict(text_list)

    def get_w2v(self, word):
        embedding = []
        if use_redis:
            if word in self.w2v:
                embedding = self.w2v[word]
        else:
            if word in self.model.vocab:
                embedding = np.array(list(self.model[word]), dtype=object)
        return embedding

    def get_sentence_embedding(self, sentence):
        if sentence in self.sentence_2_word:
            words = self.sentence_2_word[sentence]
        else:
            words = list(jieba.cut(sentence))[:max_len]
            self.sentence_2_word[sentence] = words
        embedding_list = []
        for word in words:
            embedding = self.get_w2v(word)
            if len(embedding) != 0:
                embedding_list.append(embedding)
        if len(embedding_list) == 0:
            return default_embedding
        else:
            return np.array(embedding_list).mean(axis=0)

    def get_one_sample_embedding(self, one_sample, sentence2vec):
        sample_feature = []
        for sentence in one_sample:
            sample_feature.append(sentence2vec[sentence])
        return np.array(sample_feature).mean(axis=0)

    def predict_paragraph(self, sentence_list):
        sample_feature = []
        for sentence in sentence_list:
            sample_feature.append(self.get_sentence_embedding(sentence))
        feature = np.array(sample_feature).mean(axis=0).reshape(1, -1)
        result = self.gbdt_model.predict(feature)
        return result

    def predict_one_course(self, course_text):
        self.init_cache()
        self.init_course(course_text)
        features = []
        data = json.loads(course_text)
        text_list = data["text_default"]
        text_list = [s["text"] for s in text_list]

        # get sentence2vec
        sentence2vec = {}
        for sentence in text_list:
            if sentence in sentence2vec:
                continue
            sentence2vec[sentence] = self.get_sentence_embedding(sentence)

        # get feature
        len_text = len(text_list)
        for i in range(len_text):
            if i < n_left:
                one_sample = text_list[:i + 1]
            elif i > (len_text - n_right - 1):
                one_sample = text_list[i:]
            else:
                 one_sample = text_list[i - n_left:i + n_right + 1]

            one_feature = self.get_one_sample_embedding(
                one_sample, sentence2vec)
            features.append(one_feature)
        label_predict = self.gbdt_model.predict(features)
        label = list(label_predict)
        return label
if __name__ == '__main__':
    pass
