from sklearn.feature_extraction.text import TfidfVectorizer

verbosity = 2


def similarity_strings(string1, string2):
    if string1 == string2:
        return 1
    return 0


def similarity_tf(*strings):
    tfidf = TfidfVectorizer().fit_transform(strings)
    # no need to normalize, since Vectorizer will return normalized tf-idf
    pairwise_similarity = tfidf * tfidf.T
    if verbosity >= 2:
        print("similarity_tf: \n%s" % pairwise_similarity.toarray())
    return pairwise_similarity
