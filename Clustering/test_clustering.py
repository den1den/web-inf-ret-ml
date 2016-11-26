from Clustering.clustering import find_tweets_with_keywords, cluster_tweets_by_time, make_list_of_string
from inputoutput.input import get_tweets, get_articles
from unittest import TestCase


class TestClustering(TestCase):
    def test_find_keywords_in_tweets(self):
        """ Testing the usage of keywords

        :return:
        """

        article = get_articles(100)

        tweets = get_tweets(17000)

        print(article[1])


        keywords = make_list_of_string(tweets[2978]['keywords'])
        combination = 3

        clustered_tweets = find_tweets_with_keywords(tweets, keywords, combination)
        for tweet in clustered_tweets:
            print(tweet)
        print("Found %i tweets that have %i of the keywords '%s' in it" % (len(clustered_tweets), combination, keywords_tweet0))

    def test_cluster_tweets_by_time(self):
        tweets = get_tweets(100)

        clusters = cluster_tweets_by_time(tweets, 3600)
        for tweet in clusters[0]:
            print(tweet['n_unicode'])

    def test_make_list_of_string(self):
        string_list = '[check, up, if, this, works]'
        print(make_list_of_string(string_list))

    def dummy_tester(self):
        list = ['check', 'up', 'if', 'this', 'works']
        if 'check' in list:
            print('score!')
        else:
            print('wtf')