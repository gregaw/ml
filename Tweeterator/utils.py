import gzip
import pickle

def data_path(filename):
    return '../data/tweeterator/{}'.format(filename)

sentence_joiner = unichr(0x00A7)

def create_learning_data(path, texts):
    with gzip.open(path, 'wb') as f:
        pickle.dump(texts, f)

def load_learning_data(path):
    with gzip.open(path, 'rb') as f:
        texts = pickle.load(f)
        return texts

def get_tweets_text(path):
    return sentence_joiner.join(load_learning_data(path))

