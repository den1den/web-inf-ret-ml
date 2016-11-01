from unittest import TestCase

from features.term_frequency import write_idf_articles, write_idf_tweets, get_idf_tweets, get_idf_articles


class TestWriteTfToFile(TestCase):
    def test_idf_articles(self):
        write_idf_articles()
        idf = get_idf_articles()

    def test_write_tf_to_file(self):
        write_idf_tweets()
        idf = get_idf_tweets()
