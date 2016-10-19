from unittest import TestCase
from extract_tweets.convert_tweet import get_tweets



class TestPreprocessing(TestCase):

    def test_preprocessing_tweet(self):
        N = 5000
        tweets = get_tweets()[0:N]
        unique_IDs = []
        for tweet in tweets:
            if tweet.id in unique_IDs:
                print(str(tweet))
                raise Exception("Multiple tweets with id %i" % tweet.id)
            else:
                unique_IDs.append(tweet.id)