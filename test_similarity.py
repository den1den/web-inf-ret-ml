import json
from unittest import TestCase

from similarity import similarity_strings, similarity_tf

with open("test_news/tc1.json") as fp:
    data = json.load(fp)


class GeneralTestCase(TestCase):
    def test_similarity_strings(self):
        assert similarity_strings("", "") == 1
        assert similarity_strings("test1", "test1") == 1
        assert similarity_strings("300", "-20") == 0


class TestCase1(TestCase):
    def test_similarity_news(self):
        assert similarity_strings(data[0]['title'], data[1]['title']) == 0
        pws = similarity_tf(*[article['title'] for article in data]).toarray()
        assert pws[0][1] > pws[0][2]  # Article 1 is more similar to 2 then to 3
        assert pws[0][1] > pws[1][2]  # Article 2 is more similar to 1 then to 3
        assert pws[0][2] <= 0.1  # Article 3 is not very similar to 1
        assert pws[1][2] <= 0.1  # Article 3 is not very similar to 2
        assert pws[0][1] >= 0.1  # Article 1 and 2 are quite similar
