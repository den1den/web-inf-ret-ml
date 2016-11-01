import csv
import json
import operator
import os
import time
from unittest import TestCase

from matplotlib import pyplot as plt
from scipy.sparse.csgraph import reverse_cuthill_mckee

from config.config import PROJECT_DIR, DROPBOX
from features.similarity import similarity_strings, similarity_tf
from features.term_frequency import get_idf_tweets, get_idf_articles
from inputoutput.imaging import plot_and_show_matrix
from inputoutput.input import get_tweets, get_articles


class TestCaseAfterExam(TestCase):
    def test_tf_idf_articles(self):
        articles = get_articles()
        idf = get_idf_articles()

        writer = csv.writer(open(os.path.join(PROJECT_DIR, 'tf_idf_articles.csv'), 'w+', encoding='utf8', newline='\n'),
                            delimiter=';')
        writer.writerow(['article', 'article_id', 'term', 'tf_idf'])

        for a in articles:
            # print(tweet)
            f = a.get_keyword_frequencies()
            for (term, tf) in f.items():
                try:
                    tf_idf = tf * idf[term]
                    # print("(%d):\t%.3f\t%s" % (tweet.id, tf_idf, term))
                    writer.writerow([str(a), a.id, term, str(tf_idf).replace('.', ',')])
                except KeyError as e:
                    raise e


    def test_tf_idf_tweets(self):
        N = 20000
        tweets = get_tweets(N)
        idf = get_idf_tweets()

        writer = csv.writer(open(os.path.join(PROJECT_DIR, 'tf_idf.csv'), 'w+', encoding='utf8', newline='\n'), delimiter=';')
        writer.writerow(['tweet_text', 'tweet_id', 'term', 'tf_idf'])

        for tweet in tweets:
            # print(tweet)
            f = tweet.get_keyword_frequencies()
            for (term, tf) in f.items():
                tf_idf = tf * idf[term]
                # print("(%d):\t%.3f\t%s" % (tweet.id, tf_idf, term))
                writer.writerow([str(tweet), tweet.id, term, str(tf_idf).replace('.', ',')])


    def test_count_duplicate_keyword(self):
        N = 10000
        tweets = get_tweets(N)
        MAX = 0
        c = 0
        c_1 = 0
        c_2 = 0
        c_3 = 0
        c_4 = 0
        uqc = 0

        duplicate_words = set()

        for tweet in tweets:
            F = tweet.get_keyword_frequencies()
            t_MAX = 0
            t_c = False
            t_c_1 = 0
            t_c_2 = 0
            t_c_3 = 0
            t_c_4 = 0
            for (word, freq) in F.items():
                if freq > t_MAX:
                    t_MAX = freq
                if freq > 1:
                    t_c = True
                    if len(word) > 3:
                        duplicate_words.add(word)
                if freq == 1:
                    t_c_1 += 1
                elif freq == 2:
                    t_c_2 += 1
                elif freq == 3:
                    t_c_3 += 1
                elif freq >= 4:
                    t_c_4 += 1
            if t_c:
                c += 1
            c_1 += t_c_1
            c_2 += t_c_2
            c_3 += t_c_3
            c_4 += t_c_4
            MAX += t_MAX

            uqc += tweet.get_unique_word_count()

        print("all %d found duplicates:\n%s" % (len(duplicate_words), duplicate_words))
        print("%.3f%% of tweets have one or more duplicate words" % (c / N * 100))
        print("On average each tweet has %.1f words with frequency == 1" % (c_1 / N))
        print("On average each tweet has %.2f words with frequency == 2" % (c_2 / N))
        print("On average each tweet has %.2f words with frequency == 3" % (c_3 / N))
        print("On average each tweet has %.3f words with frequency >= 4" % (c_4 / N))
        print("On average each tweet has %.1f unique words" % (uqc / N))
        print("On average the frequency of the most common word per tweet is %.1f" % (MAX / N))


class TestCase2(TestCase):
    def test_sim(self):
        N = 50000-39601
        tweets = get_tweets(N)
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
        pairs3 = set()
        word_set_arr = list(word_set)
        for word1 in word_set_arr:
            i = word_set_arr.index(word1)
            for word2 in word_set_arr[i+1:len(word_set_arr)]:
                pairs.add((word1, word2))
                pair_freq_key = word1 + '__' + word2
                j = word_set_arr.index(word2)
                word_freqs[pair_freq_key] = 0
                for word3 in word_set_arr[j + 1:len(word_set_arr)]:
                    pairs3.add((word1, word2, word3))
                    pair_freq_key = word1 + '__' + word2 + '__' + word3
                    word_freqs[pair_freq_key] = 0
        print("Initialized %d word pairs" % len(pairs))

        for tweet in tweets:
            words = tweet.get_words()
            for pair in pairs:
                if pair[0] in words and pair[1] in words:
                    pair_freq_key = pair[0] + '__' + pair[1]
                    word_freqs[pair_freq_key] += 1
            for pair in pairs3:
                if pair[0] in words and pair[1] in words and pair[2] in words:
                    pair_freq_key = pair[0] + '__' + pair[1] + '__' + pair[2]
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

    def test_cuthill(self):
        tweets = get_tweets(450)

        matrix = similarity_tf([tweet.get_txt() for tweet in tweets])
        # matrix[matrix > 0.33] = 0

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
        # rev_perm = cuthill_mckee_perm[cuthill_mckee_perm]
        plot_and_show_matrix(matrix.toarray())


class GeneralTestCase(TestCase):
    def test_similarity_strings(self):
        assert similarity_strings("", "") == 1
        assert similarity_strings("test1", "test1") == 1
        assert similarity_strings("300", "-20") == 0


class TestCase1(TestCase):
    def setUp(self):
        with open(PROJECT_DIR + "test_news/tc1.json", encoding="utf8") as fp:
            self.data = json.load(fp)
        with open(PROJECT_DIR + "test_tweets/100-elections.json") as fp:
            self.data2 = json.load(fp)

    def test_similarity_news(self):
        titles = [article['title'] for article in self.data]
        bodies = [article['body'] for article in self.data]
        assert similarity_strings(self.data[0]['title'], self.data[1]['title']) == 0
        title_sa = similarity_tf(titles).toarray()
        assert title_sa[0][1] > title_sa[0][2]  # Article 1 is more similar to 2 then to 3
        assert title_sa[0][1] > title_sa[1][2]  # Article 2 is more similar to 1 then to 3
        assert title_sa[0][2] <= 0.1  # Article 3 is not very similar to 1
        assert title_sa[1][2] <= 0.1  # Article 3 is not very similar to 2
        assert title_sa[0][1] >= 0.1  # Article 1 and 2 are quite similar

        body_sa = similarity_tf(bodies).toarray()
        assert body_sa[0][1] > body_sa[0][2]  # Article 1 is more similar to 2 then to 3
        assert body_sa[0][1] > body_sa[1][2]  # Article 2 is more similar to 1 then to 3

        body_title_sa = similarity_tf(titles + bodies).toarray()
        # Title article X is more similar to body article X then bodies of diff articles
        assert body_title_sa[0][3] > body_title_sa[0][4] and body_title_sa[0][3] > body_title_sa[0][5]
        assert body_title_sa[2][5] > body_title_sa[2][3] and body_title_sa[2][5] > body_title_sa[2][4]
        # Except for article 2, that is more similar to body of article 1 then body of article 2

    def test_100_tweets(self):
        texts = [tweet['text'] for tweet in self.data2]
        tweets_sim = similarity_tf(texts)
        minbandwidth_perm = reverse_cuthill_mckee(tweets_sim, True)
        # Could use more efficient matricx prepresenation
        tweets_sim_cuthillmckee = [[(0 if x == y else tweets_sim[x, y]) for y in minbandwidth_perm] for x in
                                   minbandwidth_perm]
        plot_and_show_matrix(tweets_sim_cuthillmckee, 1)
