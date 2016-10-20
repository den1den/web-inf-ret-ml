import time
from unittest import TestCase

import matplotlib.pyplot as plt
import numpy as np
from scipy.cluster.hierarchy import linkage, dendrogram
from sklearn.feature_extraction.text import TfidfVectorizer

from extract_tweets.convert_tweet import get_tweets
from features.similarity import get_word_set


class TestHierarchicalClustering(TestCase):
    def do_hc_tf(self, tweets):
        N = len(tweets)
        total_word_set = get_word_set(tweets)
        total_word_list = list(total_word_set)
        print("Word list of %d created of %d tweets" % (len(total_word_set), N))

        # Set the input array
        tweet_present_data_type = 'b1'
        # For integer presence tweet_present_data_type = 'i2'
        X = np.zeros(shape=(N, len(total_word_list)),
                     dtype=tweet_present_data_type)  # Could also use `np.array` to not first fill with 0
        i = 0
        for tweet in tweets:
            tweet_word_list = tweet.get_keywords()
            X[i] = np.array([word in tweet_word_list for word in total_word_list])
            i += 1

        t0 = time.time()
        print("starting on calculation of linkage")
        Z = linkage(X, method='ward')
        print("linkage took %.1f seconds" % (time.time() - t0))
        tweets_is = set()
        for z in Z:
            if 0.01 < z[2] < 3:
                if z[0] <= N:
                    tweets_is.add(z[0])
                if z[1] <= N:
                    tweets_is.add(z[1])

        X_labels = [str(tweet.get_real_text()) for tweet in tweets]
        self.plot_z(X_labels, Z)

        i = 0
        tweets2 = []
        for tweet in tweets:
            if i in tweets_is:
                tweets2.append(tweet)
            i += 1
        return tweets2

    def test_hc_tf(self):
        """Test hierarchical clustering by term frequency"""
        N = 450  # takes ~40 seconds for N = 3000
        plt.ion()
        tweets = get_tweets(N)
        tweets = self.do_hc_tf(tweets)
        plt.ioff()
        tweets = self.do_hc_tf(tweets)


    def test_hc_tfid(self):
        """Test hierarchical clustering by tfid vectorized (very slow)"""
        tweets = get_tweets(100)
        tweet_idmap = {tweet.id: str(tweet) for tweet in tweets}

        def metric(a, b):
            tweet_a = tweet_idmap[a[0]]
            tweet_b = tweet_idmap[b[0]]
            # By length (quick): return abs(len(tweet_a) - len(tweet_b))
            sim_matrix = TfidfVectorizer().fit_transform([tweet_a, tweet_b])
            similarity = 1 - sim_matrix[0, 0]
            return similarity

        X = [[tweet_id, ] for tweet_id in tweet_idmap.keys()]
        X_labels = [str(tweet_idmap[x[0]]) for x in X]
        t0 = time.time()
        print("starting on calculation of linkage")
        Z = linkage(X, metric=metric)
        print("linkage took %.1f seconds" % (time.time() - t0))
        self.plot_z(X_labels, Z)

    def plot_z(self, X_vals, Z):
        """Plot a dendrogram"""
        plt.figure()  # figsize=(25, 10))
        plt.title('Hierarchical Clustering Dendrogram')
        plt.xlabel('sample index')
        plt.ylabel('distance')
        dendrogram(
            Z,
            leaf_rotation=90.,  # rotates the x axis labels
            leaf_font_size=8.,  # font size for the x axis labels
            labels=X_vals
        )
        plt.show()

    def test_linkage_1d(self):
        # generate two clusters: a with 100 points, b with 50:
        np.random.seed(4711)  # for repeatability of this tutorial
        a = 2 * np.random.randn(100) + 10
        b = 3 * np.random.randn(50) - 5
        X = np.concatenate((a, b), )
        X = np.array([np.array((el,)) for el in X])
        # print(X.shape)  # 150 samples with 1 dimensions
        # plt.scatter(X[:], [1 for x in range(0, len(X))])

        # plt.show()
        # generate the linkage matrix
        Z = linkage(X, 'ward')
        self.plot_z(["%.2f" % x for x in X], Z)

    def test_linkage_2d(self):
        # generate two clusters: a with 100 points, b with 50:
        np.random.seed(4711)  # for repeatability of this tutorial
        a = np.random.multivariate_normal([10, 0], [[3, 1], [1, 4]], size=[3, ])
        b = np.random.multivariate_normal([0, 20], [[3, 1], [1, 4]], size=[5, ])
        X = np.concatenate((a, b), )
        print(X.shape)  # 150 samples with 2 dimensions, thus returns 150, 2
        plt.scatter(X[:, 0], X[:, 1])

        # plt.show()
        # generate the linkage matrix
        Z = linkage(X)

        print(Z)

        self.plot_z(X, Z)
