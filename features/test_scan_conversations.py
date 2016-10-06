import csv
import os
import time
from unittest import TestCase

from config.config import TWEETS_HOMEDIR, DROPBOX
from extract_tweets.convert_tweet import convert_tweet
from features import simple


class TestScanConversations(TestCase):
    def test_scan_conversations(self):
        tweets_dir = TWEETS_HOMEDIR + 'elections-28-09-raw'
        t0 = time.time()
        i = 0
        n = 0
        cons = {}
        cons_n = 0
        for tweetfilename in os.listdir(tweets_dir):
            i += 1
            tweets = convert_tweet(os.path.join(tweets_dir, tweetfilename))
            if tweets is None:
                continue
            n += len(tweets)
            (cons, cons_n) = simple.scan_conversations(cons, cons_n, tweets)
            print("Conversations per tweet: %0.3f" % (cons_n / n,))
            if time.time() - t0 > 120:
                print("Out of time! %s / %s files processed" % (i, len(os.listdir(TWEETS_HOMEDIR)),))
                break

        with open(DROPBOX + 'tmp/conversations_test.csv', 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            for (tweet, con_id) in cons.items():
                csvwriter.writerow([tweet, con_id])
        print("done")
