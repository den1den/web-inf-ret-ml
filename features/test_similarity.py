import csv
import json
import operator
import time
from unittest import TestCase
from scipy.sparse.csgraph import reverse_cuthill_mckee
from features.similarity import similarity_strings, similarity_tf
from config.config import PROJECT_DIR, DROPBOX
from extract_tweets.convert_tweet import get_tweets
from extract_tweets.imaging import plot_and_show_matrix
from matplotlib import pyplot as plt

with open(PROJECT_DIR + "test_news/tc1.json", encoding="utf8") as fp:
    data = json.load(fp)

with open(PROJECT_DIR + "test_tweets/100-elections.json") as fp:
    data2 = json.load(fp)


class TestCase2(TestCase):
    def test_sim(self):
        N = 50000-39601
        tweets = get_tweets()[0:N]
        n_tweets = len(tweets)
        if n_tweets < N:
            raise Exception("To few files selected, missing %d" % (N - n_tweets))
        print("Tweets: %d" % n_tweets)

        word_set = set()
        word_freqs = dict()
        for tweet in tweets:
            for w in tweet.get_words():
                word_set.add(w)
                word_freqs[w] = 0
        print("Found %s words over all tweets" % len(word_set))

        for tweet in tweets:
            words = tweet.get_words()
            for word in word_set:
                if word in words:
                    word_freqs[word] += 1
        print("Computed F for single words")

        word_freqs2 = word_freqs.copy()
        for (word, freq) in word_freqs2.items():
            if \
                freq <= 0.02 * n_tweets\
                or freq >= 0.25 * n_tweets\
                or len(word) <= 4\
                    :
                word_set.discard(word)
                word_freqs.pop(word)
        print("Filtered out %d words" % len(word_set))

        # Make pairs from `word_set`
        pairs = set()
        word_set_arr = list(word_set)
        for word1 in word_set_arr:
            i = word_set_arr.index(word1)
            for word2 in word_set_arr[i+1:len(word_set_arr)]:
                pairs.add((word1, word2))
                pair_freq_key = word1 + '__' + word2
                word_freqs[pair_freq_key] = 0
        print("Initialized %d word pairs" % len(pairs))

        for tweet in tweets:
            words = tweet.get_words()
            for pair in pairs:
                if pair[0] in words and pair[1] in words:
                    pair_freq_key = pair[0] + '__' + pair[1]
                    word_freqs[pair_freq_key] += 1
        print("Set F for all pairs")

        sorted_word_freqs = sorted(word_freqs.items(), key=operator.itemgetter(1))

        # n_tweets_with_zero = 0
        # tweet_data_rows = []
        # for tweet in tweets:
        #     words = tweet.get_words()
        #     r = [tweet.id, ]
        #     hits = 0
        #     for (word, freq) in sorted_word_freqs:
        #         if "__" in word:
        #
        #
        #     for word in word_set:
        #         if word in words:
        #             r.append(1)
        #             hits += 1
        #         else:
        #             r.append(0)
        #     for pair in pairs:
        #         if pair[0] in words and pair[1] in words:
        #             r.append(1)
        #             pair_freq_key = pair[0] + '__' + pair[1]
        #             word_freqs[pair_freq_key] += 1
        #         else:
        #             r.append(0)
        #     if hits != 0:
        #         tweet_data_rows.append(r)
        #     else:
        #         n_tweets_with_zero += 1
        # print("Discarded %d tweets because freq on our selection is 0" % n_tweets_with_zero)

        # Show graph
        fig, ax = plt.subplots()
        xss = [i for i in range(1, len(sorted_word_freqs)+1)]
        rects = ax.bar(
            xss,
            [freq / n_tweets for (word, freq) in sorted_word_freqs]
        )
        ax.set_xticks([xs + 0.8 for xs in xss])
        ax.set_xticklabels([word for (word, freq) in sorted_word_freqs], rotation=80)
        plt.show()

        # Print to dropbox
        data = []
        data.append([''] + [key for (key, freq) in sorted_word_freqs])
        data.append([''] + [str(freq / n_tweets).replace('.', ',') for (key, freq) in sorted_word_freqs])
        # for tweet_row in tweet_data_rows:
        #     data.append(tweet_row)

        with open(DROPBOX + 'tmp/word_freq2.csv', 'w') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=";")
            for row in data:
                csvwriter.writerow(row)
        print("done")
        return

        matrix = similarity_tf([tweet.get_txt() for tweet in tweets])
        matrix[matrix > 0.33] = 0

        print("Starting on McKee")
        t0 = time.time()
        cuthill_mckee_perm = reverse_cuthill_mckee(matrix, True)
        print(cuthill_mckee_perm)
        t1 = time.time()
        print("Starting on McKee-conversion")
        matrix = matrix[:, cuthill_mckee_perm]
        matrix = matrix[cuthill_mckee_perm, :]
        t2 = time.time()
        print("Cuthill mckee permutation in %.2f seconds, conversion %.2f seconds" % (t1 - t0, t2 - t1))
        # for i in cuthill_mckee_perm[range(674, 734)]:
        # for i in cuthill_mckee_perm[range(701, 733)]:
        for i in cuthill_mckee_perm[range(1660, 1822)]:
            print(str(tweets[i]))
        return
        # rev_perm = cuthill_mckee_perm[cuthill_mckee_perm]
        plot_and_show_matrix(matrix)


class GeneralTestCase(TestCase):
    def test_similarity_strings(self):
        assert similarity_strings("", "") == 1
        assert similarity_strings("test1", "test1") == 1
        assert similarity_strings("300", "-20") == 0


class TestCase1(TestCase):
    def test_similarity_news(self):
        titles = [article['title'] for article in data]
        bodies = [article['body'] for article in data]
        assert similarity_strings(data[0]['title'], data[1]['title']) == 0
        title_sa = similarity_tf(*titles).toarray()
        assert title_sa[0][1] > title_sa[0][2]  # Article 1 is more similar to 2 then to 3
        assert title_sa[0][1] > title_sa[1][2]  # Article 2 is more similar to 1 then to 3
        assert title_sa[0][2] <= 0.1  # Article 3 is not very similar to 1
        assert title_sa[1][2] <= 0.1  # Article 3 is not very similar to 2
        assert title_sa[0][1] >= 0.1  # Article 1 and 2 are quite similar

        body_sa = similarity_tf(*bodies).toarray()
        assert body_sa[0][1] > body_sa[0][2]  # Article 1 is more similar to 2 then to 3
        assert body_sa[0][1] > body_sa[1][2]  # Article 2 is more similar to 1 then to 3

        body_title_sa = similarity_tf(*(titles + bodies)).toarray()
        # Title article X is more similar to body article X then bodies of diff articles
        assert body_title_sa[0][3] > body_title_sa[0][4] and body_title_sa[0][3] > body_title_sa[0][5]
        assert body_title_sa[2][5] > body_title_sa[2][3] and body_title_sa[2][5] > body_title_sa[2][4]
        # Except for article 2, that is more similar to body of article 1 then body of article 2


class TestCaseTweets(TestCase):
    def test_100_tweets(self):
        texts = [tweet['text'] for tweet in data2]
        tweets_sim = similarity_tf(*texts)
        minbandwidth_perm = reverse_cuthill_mckee(tweets_sim, True)
        # Could use more efficient matricx prepresenation
        tweets_sim_cuthillmckee = [[(0 if x == y else tweets_sim[x, y]) for y in minbandwidth_perm] for x in
                                   minbandwidth_perm]
        plot_and_show_matrix(tweets_sim_cuthillmckee, 1)
