from unittest import TestCase
from extract_tweets.convert_tweet import get_tweets



class TestPreprocessing(TestCase):

    def test_unique_id(self):
        N = 5000
        tweets = get_tweets()[0:N]
        unique_IDs = []
        for tweet in tweets:
            if tweet.id in unique_IDs:
                print(str(tweet))
                raise Exception("Multiple tweets with id %i" % tweet.id)
            else:
                unique_IDs.append(tweet.id)

    def test_keywords(self):
        N = 10
        tweets = get_tweets()[0:N]
        for tweet in tweets:
            print(tweet.keywords)

    def test_striptext(self):
        N = 10
        tweets = get_tweets()[0:N]
        for tweet in tweets:
            print(tweet)