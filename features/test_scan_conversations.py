import csv
import os
import time
from unittest import TestCase

from config.config import TWEETS_HOMEDIR, DROPBOX
from extract_tweets.convert_tweet import convert_tweets, get_tweets
from features import simple, similarity


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
            tweets = convert_tweets(os.path.join(tweets_dir, tweetfilename))
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

    def test_unique_ids_with_printing(self, print_tweets=True):
        """This also prints every tweet twice"""
        # 55 a
        # 55 b
        # 55 b
        # 67 c
        # 67 c
        # 67 c
        # 99 g

        tweets = get_tweets()

        ids = set()
        id_printed = set()

        duplicate_indices = 0
        same_index_diff_text = 0
        for i in range(0, len(tweets)):
            ID = tweets[i].id
            if ID in ids:
                # Duplicate found
                if ID not in id_printed:
                    # Print it

                    # Find first time of ID:
                    for j in range(0, i - 1):
                        if tweets[j].id == ID:
                            original = tweets[j]
                            if print_tweets:
                                print("  original tweet.id = %d: %s" % (tweets[j].id, tweets[j]))
                    duplicate_indices += 1

                    same_text_found = False

                    for j in range(i, len(tweets)):
                        if original.id == tweets[j].id:
                            if print_tweets:
                                print("Also found tweet.id = %d: %s" % (tweets[j].id, tweets[j]))
                            duplicate_indices += 1
                            if similarity.similarity_strings(str(original), str(tweets[j])) == 0:
                                same_index_diff_text += 1
                                if same_text_found is False:
                                    same_index_diff_text += 1
                                same_text_found = True
                    if print_tweets:
                        print("\n----------------------------------------------------------\n")
                    id_printed.add(ID)
            else:
                ids.add(tweets[i].id)

            if i % 1000 == 0:
                print("%s / %s" % (i, len(tweets)))

        print("duplicate_indices: %s, same_index_diff_text: %s, tweets: %s"
              % (duplicate_indices,
                 same_index_diff_text,
                 len(tweets))
              )
