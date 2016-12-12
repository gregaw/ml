"""
    based on keras LSTM example 'to generate text from Nietzsche's writings.'
    - applied a few changes from: https://gist.github.com/karpathy/d4dee566867f8291f086
    - adjusted with: https://github.com/karpathy/char-rnn

"""
import os
import random

from keras.callbacks import Callback
from keras.models import Sequential, save_model, load_model
from keras.layers import Dense, Activation, Dropout
from keras.layers import LSTM
from keras.optimizers import RMSprop
import numpy as np
import sys

from utils import data_path, get_tweets_text, sentence_joiner

class LossHistory(Callback):
    def __init__(self, prefix, model, epoch_count):
        super(LossHistory, self).__init__()
        self.prefix = prefix
        self.model = model
        self.epoch_count = epoch_count

    def on_train_begin(self, logs={}):
        self.losses = []

    def on_batch_end(self, batch, logs={}):
        self.losses.append(logs.get('loss'))

    def on_epoch_end(self, epoch, logs={}):
        self.epoch_count += 1
        save_model(
            self.model,
            data_path("{}_{}_{:.2f}.hdf5".format(self.prefix, self.epoch_count, logs.get('loss'))))


class Brain():
    def __init__(self, maxlen, lstm_size, dropout, training_text=None):

        print('loading training text from "{}"...'.format(training_text))
        self._text = get_tweets_text(training_text).lower()
        print('corpus length:', len(self._text))

        print('retrieving chars...')
        self._chars = sorted(list(set(self._text)))
        print('total chars:', len(self._chars))
        self._char_indices = dict((c, i) for i, c in enumerate(self._chars))
        self._indices_char = dict((i, c) for i, c in enumerate(self._chars))

        # cut the text in semi-redundant sequences of maxlen characters
        self._maxlen = maxlen
        self._lstm_size = lstm_size
        self._dropout = dropout

    @property
    def text(self):
        return self._text

    def sample(self, preds, temperature=1.0):
        # helper function to sample an index from a probability array
        preds = np.asarray(preds).astype('float64')
        preds = np.log(preds) / temperature
        exp_preds = np.exp(preds)
        preds = exp_preds / np.sum(exp_preds)
        probas = np.random.multinomial(1, preds, 1)
        return np.argmax(probas)

    def build_model(self):
        print('Build model...')

        model = Sequential()
        model.add(LSTM(self._lstm_size, input_shape=(self._maxlen, len(self._chars))))
        model.add(Dropout(self._dropout))
        model.add(Dense(len(self._chars)))
        model.add(Activation('softmax'))

        optimizer = RMSprop(lr=0.01)
        model.compile(loss='categorical_crossentropy', optimizer=optimizer)
        return model

    def find_last_model(self, runid):
        saves = [x for x in os.listdir(data_path("")) if x.startswith(runid) and x.endswith('.hdf5')]
        if saves:
            print saves
            return sorted(map(lambda x: (int(x[len(runid) + 1:].split('_')[0]), x), saves), reverse=True)[0]
        else:
            return 0, None

    def generate(self, model, seed_sentence, n, diversity):
        generated = ''
        for i in range(n):
            x = np.zeros((1, self._maxlen, len(self._chars)))
            for t, char in enumerate(seed_sentence):
                x[0, t, self._char_indices[char]] = 1.

            preds = model.predict(x, verbose=0)[0]
            next_index = self.sample(preds, diversity)
            next_char = self._indices_char[next_index]

            generated += next_char
            seed_sentence = seed_sentence[1:] + next_char

        return generated

    def generate_full(self, model, seed_sentence, n, diversity):
        generated = ''
        sentence_joiner_count = 0
        tries_left = 400
        while tries_left > 0 and sentence_joiner_count < 2:
            x = np.zeros((1, self._maxlen, len(self._chars)))
            for t, char in enumerate(seed_sentence):
                x[0, t, self._char_indices[char]] = 1.

            preds = model.predict(x, verbose=0)[0]
            next_index = self.sample(preds, diversity)
            next_char = self._indices_char[next_index]

            if next_char == sentence_joiner:
                sentence_joiner_count += 1

            generated += next_char
            seed_sentence = seed_sentence[1:] + next_char
            tries_left -= 1

        return generated.split(sentence_joiner)[1] if sentence_joiner in generated else generated

    def output_prefix(self, runid, step):
        return "{}-{}-{}-{}-{}".format(runid, self._maxlen, step, self._lstm_size, self._dropout)

    def train(self, runid, iterations, step):
        if '-' in runid or '_' in runid:
            raise Exception("runid can't contain '-', nor '_'")

        epoch, last_run = self.find_last_model(self.output_prefix(runid, step))
        if last_run:
            print 'starting with: {} on epoch: {}'.format(last_run, epoch)
            model = load_model(data_path(last_run))
        else:
            print 'starting with a newly built model'
            model = self.build_model()

        sentences = []
        next_chars = []
        for i in range(0, len(self._text) - self._maxlen, step):
            sentences.append(self._text[i: i + self._maxlen])
            next_chars.append(self._text[i + self._maxlen])
        print('nb sentences:', len(sentences))

        print('Vectorization...')
        X = np.zeros((len(sentences), self._maxlen, len(self._chars)), dtype=np.bool)
        y = np.zeros((len(sentences), len(self._chars)), dtype=np.bool)
        for i, sentence in enumerate(sentences):
            for t, char in enumerate(sentence):
                X[i, t, self._char_indices[char]] = 1
            y[i, self._char_indices[next_chars[i]]] = 1

        # train the model, output generated text after each iteration
        history = LossHistory(self.output_prefix(runid, step), model, epoch)

        for iteration in range(epoch + 1, iterations):
            print()
            print('-' * 50)
            print('Iteration', iteration)

            model.fit(X, y, batch_size=128, nb_epoch=1, callbacks=[history], validation_split=0.1)

            self.generate_show(model, 140, [0.1, 0.4], self.random_seed_sentence())

    def load_model_with_prefix(self, model_prefix):
        model_files = [x for x in os.listdir(data_path('')) if x.startswith(model_prefix) and x.endswith(".hdf5")]
        if len(model_files) > 1:
            raise Exception(
                "There's more than one model file with the prefix '{}': {}".format(model_prefix, model_files))
        elif not model_files:
            raise Exception("Didn't find anything with prefix: {} in folder {}".format(model_prefix, data_path('')))
        else:
            model = load_model(data_path(model_files[0]))

        return model

    def random_seed_sentence(self, start_with_tweet=True):

        start_index = random.randint(0, len(self._text) - self._maxlen - 1)

        if start_with_tweet:
            while start_index > 0 and self._text[start_index - 1] != sentence_joiner:
                start_index -= 1

        end_index = start_index + self._maxlen

        return self._text[start_index: end_index]

    def generate_show(self, model, length, diversities, seed_sentence):
        for diversity in diversities:
            print u"\n---- generating diversity: [{}], seed: [{}]...\n".format(diversity, seed_sentence)
            generated = self.generate_full(
                model=model,
                n=length,
                diversity=diversity,
                seed_sentence=seed_sentence)
            print generated + '\n'

    def random_seed(self, seed):
        random.seed(seed)
