import csv
from unittest import TestCase

from config.config import DROPBOX
from features import simple
from inputoutput.input import get_tweets


class TestScanConversations(TestCase):
    def test_scan_conversations(self):
        tweets = get_tweets()
        tweets_n = len(tweets)

        tweet_to_conv = {}
        conv_i = 0
        (tweet_to_conv, conv_i) = simple.scan_conversations(tweet_to_conv, conv_i, tweets)
        conv_ids = set(tweet_to_conv.values())
        conv_n = len(conv_ids)

        conv_to_tweet = {}
        for (tweet_id, con_id) in tweet_to_conv.items():
            if con_id not in conv_to_tweet:
                conv_to_tweet[con_id] = {tweet_id}
            elif tweet_id in conv_to_tweet[con_id]:
                raise AssertionError("tweet_id is double")
            else:
                conv_to_tweet[con_id].add(tweet_id)

        conv_sizes = [len(tweet_set) for (con, tweet_set) in conv_to_tweet.items()]
        avg_size = sum(conv_sizes) / len(conv_sizes)
        print("%d conversations found, with avg size of %0.3f" % (conv_n, avg_size))
        print("%.2f%% unique tweets?" % (100 * (conv_n * avg_size / tweets_n),))

        with open(DROPBOX + 'tmp/conversations_test.csv', 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            for (tweet, con_id) in tweet_to_conv.items():
                csvwriter.writerow([tweet, con_id])
        print("done")
