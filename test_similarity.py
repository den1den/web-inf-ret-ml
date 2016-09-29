import json
from unittest import TestCase
import numpy
from scipy.sparse.csgraph import reverse_cuthill_mckee
from PIL.Image import fromarray

from similarity import similarity_strings, similarity_tf

with open("test_news/tc1.json", encoding="utf8") as fp:
    data = json.load(fp)

with open("test_tweets/100-elections.json") as fp:
    data2 = json.load(fp)


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
        print("Length %s, Permutation: %s" % (tweets_sim.shape[0], minbandwidth_perm, ))
        # Could use more efficient matricx prepresenation
        tweets_sim_cuthillmckee = [[tweets_sim[x, y] for y in minbandwidth_perm] for x in minbandwidth_perm]
        rgbss = numpy.array([numpy.array([numpy.array((el, 0, 0, )) for el in row]) for row in tweets_sim_cuthillmckee])
        img = fromarray(rgbss, 'RGB')
        img.save('my.png')
