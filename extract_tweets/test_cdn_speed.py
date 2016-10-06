import os
import time
from unittest import TestCase

from config.config import TWEETS_HOMEDIR, LOCAL_DIR
from extract_tweets.convert_tweet import convert_tweets


class TestCdnSpeed(TestCase):
    def test_speedtest(self):
        self.speedtest(TWEETS_HOMEDIR, LOCAL_DIR)

    def speedtest(self, TWEETS_HOMEDIR, LOCAL_DIR):
        N = 30
        i = 0
        start = time.time()
        for tweetfilename in os.listdir(TWEETS_HOMEDIR):
            tweets = convert_tweets(os.path.join(TWEETS_HOMEDIR, tweetfilename))
            if i == N:
                break
            i += 1
        end = time.time()
        print("%s files from Service: %.2f sec per file" % (i, (end - start) / i))

        i = 0
        start = time.time()
        for tweetfilename in os.listdir(LOCAL_DIR):
            tweets = convert_tweets(os.path.join(LOCAL_DIR, tweetfilename))
            if i == N:
                break
            i += 1
        end = time.time()
        print("%s files from Local service: %.2f sec per file" % (i, (end - start) / i))
