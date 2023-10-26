import redis
import numpy as np
import jieba
import pickle


class RedisEmbeddingFeature():
    def __init__(self, host, port, password, db, embedding_dim):
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.embedding_dim = embedding_dim
        self.default_embedding = np.array(
            [0.] * embedding_dim, dtype=np.float32)
        self.db_redis = self.db_connect()
        self.init_cache()

    def init_cache(self):
        self.sentence_2_word = {}
        self.w2v = {}

    def clear_cache(self):
        self.init_cache()

    def db_connect(self):
        return redis.Redis(host=self.host, port=self.port, db=self.db, password=self.password)

    def get_word_vector(self, word_vec, embedding_dim):
        if word_vec == None:
            word_embedding = [0.] * embedding_dim
        else:
            word_embedding = list(np.fromstring(word_vec, dtype=np.float32))
        return word_embedding

    def get_w2v(self, word):
        embedding = self.w2v.get(word, [])
        return embedding

    def set_dict(self, text_list, max_len):
        cut_words = []
        for sentence in text_list:
            if sentence in self.sentence_2_word:
                words = self.sentence_2_word[sentence]
            else:
                words = jieba.lcut(sentence)[:max_len]
                self.sentence_2_word[sentence] = words
                cut_words.extend(words)
        cut_words = list(set(cut_words))

        if len(cut_words) != 0:
            redis_query_status, embedding_result = self.get_redis_result(
                cut_words)
            for word, embedding in zip(cut_words, embedding_result):
                if embedding != [0.] * self.embedding_dim:
                    self.w2v[word] = embedding

    def get_redis_result(self, key):
        redis_query_status = True
        if not self.db_redis.ping():
            self.db_redis = self.db_connect()
        try:
            query_result = self.db_redis.mget(key)
        except:
            query_result = [None] * len(key)
            redis_query_status = False
        embedding_result = [
            self.get_word_vector(x, self.embedding_dim) for x in query_result
        ]
        return redis_query_status, embedding_result

    def get_sentence_embedding_mean(self, sentence, max_len):
        self.set_dict([sentence], max_len)

        words = self.sentence_2_word[sentence]

        embedding_list = []
        for word in words:
            embedding = self.get_w2v(word)
            if len(embedding) != 0:
                embedding_list.append(embedding)
        if len(embedding_list) == 0:
            return self.default_embedding
        else:
            return np.array(embedding_list).mean(axis=0)

    def get_sentence_list_embedding_mean(self, text_list, max_len, clear_cache=True):
        if len(text_list) == 0:
            raise Exception("text_list is empty")
        self.set_dict(text_list, max_len)
        embedding_list = []
        sentence2vec = {}
        for sentence in text_list:
            if not sentence in sentence2vec:
                sentence2vec[sentence] = self.get_sentence_embedding_mean(
                    sentence, max_len)
            embedding_list.append(sentence2vec[sentence])
        if clear_cache:
            self.clear_cache()
        return np.array(embedding_list).reshape(len(embedding_list), self.embedding_dim)


class EmbeddingFeature():
    def __init__(self, embedding_path, embedding_dim):
        self.embedding_dim = embedding_dim
        self.default_embedding = np.array(
            [0.] * embedding_dim, dtype=np.float32)
        self.w2v = pickle.load(open(embedding_path, 'rb'))

    def get_w2v(self, word):
        embedding = self.w2v.get(word, [])
        return embedding

    def get_sentence_embedding_mean(self, sentence, max_len):
        words = jieba.lcut(sentence)[:max_len]
        embedding_list = []
        for word in words:
            embedding = self.get_w2v(word)
            if len(embedding) != 0:
                embedding_list.append(embedding)
        if len(embedding_list) == 0:
            return self.default_embedding
        else:
            return np.array(embedding_list).mean(axis=0)

    def get_sentence_list_embedding_mean(self, text_list, max_len):
        if len(text_list) == 0:
            raise Exception("text_list is empty")
        s2w = {}
        for sentence in set(text_list):
            s2w[sentence] = self.get_sentence_embedding_mean(sentence, max_len)
        embedding_list = []
        for sentence in text_list:
            embedding_list.append(s2w[sentence])
        return np.array(embedding_list).reshape(len(embedding_list), self.embedding_dim)
