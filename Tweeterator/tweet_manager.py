import json
from random import shuffle
import re
import sqlite3
import itertools

import pandas as pd
import tweepy
from tweepy import OAuthHandler

# https://marcobonzanini.com/2015/03/02/mining-twitter-data-with-python-part-1/
from preprocessing import find_significant_terms
from twitter_config import *
from utils import create_learning_data, load_learning_data

PISTRADAMUS = ["DoRzeczy_pl", "niezaleznapl", "fronda_pl"]
RESTRADAMUS = ["gazeta_wyborcza", "NewsweekPolska", "Polityka_pl"]
TRUMP = ["realDonaldTrump", "TeamTrump"]
CLINTON = ["HillaryClinton", "TheBriefing2016"]
ITALIAN = ["LaRepubblica_it", "Corriere", "LaStampa"]

conn = sqlite3.connect('../data/tweeterator1234.db')
c = conn.cursor()


def download_tweets(tweeter_id, latest=True):
    id_str = ""
    try:
        # get all ids
        stored_tweets = set(itertools.imap(lambda tw: tw[0], query_tweets("tweeter_id = '{}'".format(tweeter_id))))
        ignored = 0
        inserted = 0
        for ix, status in enumerate(tweepy.Cursor(api.user_timeline, id=tweeter_id).items()):
            if ix % 100 == 0:
                print "{}.{}: {}".format(tweeter_id, ix, status._json['created_at'])

            id_str = status._json['id_str']
            if id_str in stored_tweets:
                if latest:
                    break
                ignored += 1
            else:
                inserted += 1
                c.execute(""
                          "INSERT INTO tweets (tweet_id_str, tweeter_id, json, text) VALUES (?,?,?,?)",
                          (id_str,
                           tweeter_id,
                           '',  # json.dumps(status._json)
                           status.text
                           ))

            conn.commit()

        print "{}: ignored = {}, inserted = {}, indb = {}".format(tweeter_id, ignored, inserted,
                                                                  count_tweets("tweeter_id = '{}'".format(tweeter_id)))
    except:
        print 'failed on processing: {}'.format(id_str)
        raise
    finally:
        conn.rollback()


def recreate_db():
    # c.execute('''DROP TABLE tweets''')
    c.execute('''CREATE TABLE tweets
                 (tweet_id_str text PRIMARY KEY, tweeter_id text, json text, text text)''')

    c.execute('''CREATE TABLE deps
                 (tweeter_id text PRIMARY KEY, parent_id text)''')

    conn.commit()


def query_tweets(where='1=1', select='*'):
    query = 'SELECT {} FROM tweets WHERE {} ORDER BY tweeter_id'.format(
        select,
        where
    )
    # print query
    for row in c.execute(query):
        yield row


def query(query):
    # print query
    for row in c.execute(query):
        yield row


def count_tweets(where='1=1'):
    query = 'SELECT count(*) FROM tweets WHERE {}'.format(
        where
    )
    # print query
    for row in c.execute(query):
        return row[0]


def find_retweets(tweeter_id):
    pattern = re.compile(u".*RT @(.*?):")
    for ix, tw in enumerate(query_tweets("tweeter_id = '{}'".format(tweeter_id))):
        text = tw[3]
        m = pattern.match(text)
        if m:
            yield m.group(1)


def most_common_retweeters(tweeter_id, max_n):
    df = pd.Series(list(find_retweets(tweeter_id)))
    value_counts = df.value_counts()
    for ix, count in zip(range(max_n), value_counts):
        if count < ix:
            return
        yield value_counts.index[ix]


def download_with_retweeters(names, latest=True):
    """
        Downloads to the db all the available tweets in 'names' and also the most common accounts retweeted by those in 'names'
    """
    for name in names:
        download_tweets(name, latest)
        for retweeter in most_common_retweeters(name, 3):
            c.execute(""
                      "INSERT INTO deps (tweeter_id, parent_id) "
                      "SELECT ?, ? "
                      "WHERE NOT EXISTS(SELECT 1 FROM deps WHERE tweeter_id = ?)",
                      (retweeter, name, retweeter))

            conn.commit()

            download_tweets(retweeter, latest)


def run(query):
    for row in c.execute(query):
        print row


def get_texts_for_training(names):
    df = pd.DataFrame(
        query(
            "select COALESCE(d.parent_id, t.tweeter_id), t.text from tweets t left outer join deps d on t.tweeter_id = d.tweeter_id"),
        columns=['id', 'text']
    )
    filtered_text = df[df.id.isin(names)].text
    text_to_save = [x for x in filtered_text]
    shuffle(text_to_save)
    return text_to_save


def create_trainingset(names, out_path):
    create_learning_data(out_path, get_texts_for_training(names))
    print len(load_learning_data(out_path))

def create_trainingset_most_significant(names_path_list):
    """
        selects just the tweets containing top N most significant words for a given option: 'names'
    """

    texts_per_name = [ get_texts_for_training(names) for names, path in names_path_list ]
    concatenated_texts_per_name = [ ' '.join(name_texts) for name_texts in texts_per_name ]
    freqs, counts = find_significant_terms(concatenated_texts_per_name)

    def texts_with_significant_words(texts, freqs, n):
        return filter(lambda text: any(w in text for freq, w in freqs[:n]), texts)

    print 'all tweets: ', list(map(lambda x: len(x), texts_per_name))
    for i in [400]:
        selected_texts_per_name = [ texts_with_significant_words(texts, freqs, i) for texts, freqs in zip(texts_per_name, freqs) ]
        print 'tweets for freq#: ', i, list(map(lambda x: len(x), selected_texts_per_name))

    for (names, out_path), texts in zip(names_path_list, selected_texts_per_name):
        create_learning_data(out_path, texts)
        print 'length of {} = {}'.format(out_path, len(load_learning_data(out_path)))


auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth)


def adhoc():
    # recreate_db()
    # download_tweets('realDonaldTrump', latest=False)
    # run("SELECT tweeter_id, substr(tweeter_id, 2), text from tweets where substr(tweeter_id, 1, 1) = 'P' LIMIT 3")

    # run("select * from tweets where tweet_id_str = '806797590985486336'")

    # run("UPDATE tweets set tweeter_id = substr(tweeter_id, 2) where substr(tweeter_id, 1, 1) = '@'")
    # conn.commit()
    pass


"""
-----------------------------------------------------
"""
try:

    adhoc()

    # download_with_retweeters(PISTRADAMUS, latest=True)

    # download_with_retweeters(RESTRADAMUS, latest=True)
    # create_trainingset(RESTRADAMUS, '../data/trainset-restradamus1.pkl.gz')
    create_trainingset_most_significant([(RESTRADAMUS, '../data/trainset-restradamus-MS.pkl.gz'),
                                         (PISTRADAMUS, '../data/trainset-pistradamus-MS.pkl.gz'),
                                         ])

    # download_with_retweeters(TRUMP, latest=True)
    # create_trainingset(TRUMP, '../data/trainset-trumpstradamus.pkl.gz')

    # download_with_retweeters(ITALIAN, latest=True)
    # create_trainingset(ITALIAN, '../data/trainset-italianstradamus.pkl.gz')

    # download_with_retweeters(CLINTON, latest=True)
    # create_trainingset(CLINTON, '../data/trainset-clintonstradamus.pkl.gz')

    # run('SELECT tweeter_id, count(*) from tweets group by tweeter_id order by count(*) desc')
    # run('SELECT count(*) from tweets')
    # run("select * from deps")


finally:

    conn.close()
