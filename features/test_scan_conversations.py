import csv
from unittest import TestCase

from config.config import DROPBOX
from extract_tweets.convert_tweet import get_tweets
from features import simple, similarity


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

    def test_unique_ids_with_printing(self, print_tweets=False):
        """This also prints every tweet twice"""
        # 55 a
        # 55 b
        # 55 b
        # 67 c
        # 67 c
        # 67 c
        # 99 g

        tweets = get_tweets(34974)

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

            if i % (1 << 10) == 0:
                print("%s / %s" % (i, len(tweets)))

        print("duplicate_indices: %s, same_index_diff_text: %s, tweets: %s"
              % (duplicate_indices,
                 same_index_diff_text,
                 len(tweets))
              )
