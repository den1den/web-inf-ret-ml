import numpy
import scipy
from sklearn.feature_extraction.text import TfidfVectorizer

verbosity = 2


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


def similarity_tf(strings):
    """
    :param strings: array of all the string that needs top be compared
    :return:
    """
    # onestirng = ""
    # for s in strings:
    #     onestirng += str(s) + "\n"
    # print(onestirng, file=open(PROJECT_DIR+'tmp.txt', mode='w'))
    tfidf = TfidfVectorizer().fit_transform(strings)
    # no need to normalize, since Vectorizer will return normalized tf-idf
    pairwise_similarity = tfidf * tfidf.T
    return pairwise_similarity
