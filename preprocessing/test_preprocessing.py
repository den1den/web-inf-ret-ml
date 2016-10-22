from unittest import TestCase

from inputoutput.input import get_tweets
from preprocessing.preprocess import strip_text


class TestPreprocessing(TestCase):

    def test_unique_id(self):
        """ Tests if the IDs are all unique

        :return:
        """
        N = 5000
        tweets = get_tweets(N)
        unique_IDs = []
        for tweet in tweets:
            if tweet.id in unique_IDs:
                print(str(tweet))
                raise Exception("Multiple tweets with id %i" % tweet.id)
            else:
                unique_IDs.append(tweet.id)

    def test_strip_text(self):
        """ Test example for stripping text

        :return:
        """
        N = 100
        tweets = get_tweets(N)
        for tweet in tweets:
            print(tweet.get_real_text())
            print(str(tweet))

    def test_keywords(self):
        """ Test example for the keywords

        :return:
        """
        N = 10
        tweets = get_tweets(10)
        for tweet in tweets:
            print(str(tweet))
            print(tweet.get_keywords())

