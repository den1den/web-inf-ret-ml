import numpy
import scipy
from sklearn.feature_extraction.text import TfidfVectorizer


def get_word_set(tweets):
    word_set = set()
    for tweet in tweets:
        word_set = word_set.union(tweet.get_keywords())
    return word_set


def get_word_freqs(tweets, word_set=None, normalized=False):
    word_set = get_word_set(tweets) if word_set is None else word_set
    word_freqs = {word: 0 for word in word_set}
    for tweet in tweets:
        for word in tweet.get_keywords():
            word_freqs[word] += 1
    if normalized:
        max = max(word_freqs.values())
        for word in word_freqs:
            word_freqs[word] /= max
    # Sorting: sorted_word_freqs = sorted(word_freqs.items(), key=operator.itemgetter(1))
    return word_freqs


def similarity_strings(string1, string2):
    if string1 == string2:
        return 1
    return 0


def sp_permute(A, perm_r, perm_c):
    """
    permute rows and columns of A
    From https://github.com/JonnyRed/IPython-Notebooks/blob/e96686b94ade97750008536d1335c9b2ef032676/Numerical-Python/code-listing-py/ch10-code-listing.py
    """
    M, N = A.shape
    # row permumation matrix
    Pr = scipy.sparse.coo_matrix((numpy.ones(M), (perm_r, numpy.arange(N)))).tocsr()
    # column permutation matrix
    Pc = scipy.sparse.coo_matrix((numpy.ones(M), (numpy.arange(M), perm_c))).tocsr()
    return Pr.T * A * Pc.T


def similarity_tf_(*strings):
    return similarity_tf(strings)


def similarity_tf(string_array):
    """
    :param numpy.array strings: of all the string that needs to be compared
    :rtype: scipy.sparse.csr.csr_matrix
    """
    tfidf = TfidfVectorizer().fit_transform(string_array)
    # no need to normalize, since Vectorizer will return normalized tf-idf
    pairwise_similarity = tfidf * tfidf.T
    return pairwise_similarity
