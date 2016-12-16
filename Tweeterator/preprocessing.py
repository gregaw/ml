from sklearn.feature_extraction.text import CountVectorizer
import numpy as np


def find_significant_terms(corpus):
    """
    find words that are more common in one document than in the whole corpus

    # {(word, count)} per list -> and per corpus
    # {(word, freq)} per list = count.list / count.corpus

    :param corpus: [clinton_text, trump_text]
    :return:
    """

    vectorizer = CountVectorizer(min_df=1)

    list_counts = np.array(vectorizer.fit_transform(corpus).toarray())
    # print list_counts
    corpus_counts = np.sum(x for x in list_counts)
    # print corpus_counts
    list_freq = [1.0 * x / corpus_counts for x in list_counts]
    # print map(lambda x: x.tolist(), list_freq)

    sorted_by_freq = [list(reversed(sorted(zip(x.tolist(), vectorizer.get_feature_names())))) for x in list_freq]
    sorted_by_count = [list(reversed(sorted(zip(x.tolist(), vectorizer.get_feature_names())))) for x in list_counts]

    return sorted_by_freq, sorted_by_count

# print find_significant_terms(['ala ma kota', 'ala ma psa'])