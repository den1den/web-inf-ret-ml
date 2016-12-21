from unittest import TestCase

from features.term_frequency import write_idf_articles, write_idf_tweets, get_idf_tweets, get_idf_articles, get_idf, \
    get_df
from inputoutput.input import get_tweets, get_articles


class TestWriteTfToFile(TestCase):

    def test_get_idf(self):
        tweets = get_tweets()
        dft = get_df(tweets)
        print(dft)

    def write_idf_articles(self):
        write_idf_articles()

    def write_idf_tweets(self):
        write_idf_tweets()

