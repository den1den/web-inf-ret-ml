import os
import time
from unittest import TestCase

from extract_tweets.convert_tweet import convert_tweet


class TestCdnSpeed(TestCase):
    def test_speedtest(self):
        TWEETS_HOMEDIR = '/home/dennis/pCloudDrive/tweets/elections-28-09-raw'
        LOCAL_DIR = '/home/dennis/repos/web-inf-ret-ml/test_tweets/local'
        self.speedtest(TWEETS_HOMEDIR, LOCAL_DIR)

    def speedtest(self, TWEETS_HOMEDIR, LOCAL_DIR):
        N = 30
        i = 0
        start = time.time()
        for tweetfilename in os.listdir(TWEETS_HOMEDIR):
            tweets = convert_tweet(os.path.join(TWEETS_HOMEDIR, tweetfilename))
            if i == N:
                break
            i += 1
        end = time.time()
        print("%s files from Service: %.2f sec per file" % (i, (end - start) / i))

        i = 0
        start = time.time()
        for tweetfilename in os.listdir(LOCAL_DIR):
            tweets = convert_tweet(os.path.join(LOCAL_DIR, tweetfilename))
            if i == N:
                break
            i += 1
        end = time.time()
        print("%s files from Local service: %.2f sec per file" % (i, (end - start) / i))
