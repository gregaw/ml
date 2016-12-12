import os
import sys
from brain import Brain
from utils import data_path

datasets = {
    'pis': '../data/trainset-pistradamus1.pkl.gz',
    'po': '../data/trainset-restradamus1.pkl.gz',
    'trump': '../data/trainset-trumpstradamus.pkl.gz',
    'clinton': '../data/trainset-clintonstradamus.pkl.gz',
    'italian': '../data/trainset-italianstradamus.pkl.gz',
}

def train(maxlens, steps, dropouts, dataset):
    for code, text_file in dataset:
        for maxlen in maxlens:
            for step in steps:
                for dropout in dropouts:
                    print '=========== TRAINING on: maxlen={}, step={}, lstm_size=128, dropout={}, text={}'.format(
                        maxlen,
                        step,
                        dropout,
                        text_file)
                    brain = Brain(maxlen=maxlen, lstm_size=128, dropout=dropout,
                                  training_text=text_file)
                    brain.train(runid='11,{},tweets'.format(code), iterations=7, step=step)

def compare_iteration(model_prefix, iterations, diversities, training_text, seed_sentence=None):
    result = {}
    index = 0
    for requested_iteration in iterations:
        for file_name in [x for x in os.listdir(data_path('')) if x.startswith(model_prefix)]:
            try:
                (runid, maxlen, step, lstm_size, rest) = file_name.split('-')
                (dropout, iteration, rest) = rest.split('_')
                if str(iteration) != str(requested_iteration):
                    continue
                (maxlen, step, lstm_size, dropout) = (int(maxlen), int(step), int(lstm_size), float(dropout))
                brain = Brain(maxlen=maxlen, lstm_size=lstm_size, dropout=dropout,
                              training_text=training_text)
                seed_sentence = seed_sentence or brain.random_seed_sentence()
                print 'sentence: ' + seed_sentence
                print '---- loading model: ' + file_name
                model = brain.load_model_with_prefix(file_name)

                length = 340

                for diversity in diversities:
                    generated = brain.generate_full(
                        model=model,
                        n=length,
                        diversity=diversity,
                        seed_sentence=seed_sentence)
                    result[(index, file_name, diversity)] = generated
                    index += 1
                    print generated
            except:
                print "Unexpected error with {}: {}".format(file_name, sys.exc_info()[1])
                raise

        for (ix, name, div), generated in sorted(result.iteritems()):
            print "ix={}, model={}, div={}| {}".format(ix, name, div, generated.encode('utf-8'))

# train(maxlens=[40], steps=[4], dropouts=[0.1], dataset=filter(lambda x: x[0]=='italian', datasets.iteritems()))
compare_iteration('11,trump,tweets-40-2-128-0.1_', iterations=[5], diversities=[0.4]*2, training_text=datasets['trump'])
# compare_iteration('11,pis,tweets-60-8-128-0.1_', iterations=[9], diversities=[0.4]*30, training_text=datasets['pis'])

