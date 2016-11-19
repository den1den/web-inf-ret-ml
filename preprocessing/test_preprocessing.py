import os
from unittest import TestCase

from config import config
from inputoutput.input import get_tweets, get_articles, read_json_array_from_files, csv_write
from preprocessing.preprocess import Preprocessor, re_unicode_decimal, re_spaces


class TestPreprocessing(TestCase):
    def test_unicode_regex(self):
        m = re_unicode_decimal.search('66&#0000;66')
        assert (m.group(1) or m.group(2)) == '0000'
        m = re_unicode_decimal.search('&#8230;')
        assert (m.group(1) or m.group(2)) == '8230'
        m = re_unicode_decimal.search('Qatar&#8217;s')
        assert (m.group(1) or m.group(2)) == '8217'
        m = re_unicode_decimal.search('&mdash;')
        assert (m.group(1) or m.group(2)) == 'mdash'
        m = re_unicode_decimal.search('&amp;')
        assert (m.group(1) or m.group(2)) == 'amp'
        m = re_unicode_decimal.search('Agents&#8221;><')
        assert (m.group(1) or m.group(2)) == '8221'

    def test_ws_regex(self):
        assert re_spaces.sub(' ', '  ') == ' '
        assert re_spaces.sub(' ', '  a') == ' a'
        assert re_spaces.sub(' ', '\n\t  <') == ' <'
        assert re_spaces.sub(' ', '\n\t  A\n\t	') == ' A '


class TestPreprocessedData(TestCase):

    def test_unique_id(self):
        """ Tests if the IDs are all unique

        :return:
        """
        N = 5000
        tweets = get_tweets(N)
        unique_IDs = []
        for tweet in tweets:
            if tweet.id in unique_IDs:
                print(str(tweet))
                raise Exception("Multiple tweets with id %i" % tweet.id)
            else:
                unique_IDs.append(tweet.id)

    def test_strip_text(self):
        """ Test example for stripping text

        :return:
        """
        N = 100
        tweets = get_tweets(N)
        for tweet in tweets:
            print(tweet.get_real_text())
            print(str(tweet))

    def test_keywords(self):
        """ Test example for the keywords

        :return:
        """
        N = 10
        tweets = get_tweets(10)
        for tweet in tweets:
            print(str(tweet))
            print(tweet.get_keywords())

    def test_article_preprocessing(self):
        """ Tests if the articles are correctly pre-processed

        ":return: Returns whether the test worked or not
        """

        N = 10
        articles = get_articles(10)
        for article in articles:
            print(article['Description'])
            print(article['real_Description'])
