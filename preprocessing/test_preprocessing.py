import os
from unittest import TestCase

from config import config
from inputoutput.input import get_tweets, get_articles, read_json_array_from_files, csv_write
from preprocessing.preprocess import Preprocessor, re_unicode_decimal, re_whitespace, re_currency, re_currency_matches, \
    remove_unicode, replace_whitespaces, replace_nonalpha_in_string


class TestPreprocessing(TestCase):
    def test_replace_nonalpha_in_string(self):
        assert replace_nonalpha_in_string('', '') == ''
        assert replace_nonalpha_in_string('a', '') == 'a'
        assert replace_nonalpha_in_string('!', '') == ''
        assert replace_nonalpha_in_string('0', '') == '0'
        assert replace_nonalpha_in_string('h0l', '') == 'h0l'
        assert replace_nonalpha_in_string('h/l', '') == 'hl'

    def test_unicode(self):
        assert remove_unicode('') == ('', 0)
        assert remove_unicode('a') == ('a', 0)
        assert remove_unicode(r'') == ('', 0)
        assert remove_unicode('\u4F11') == ('', 1)

    def test_replace_whitespaces(self):
        assert replace_whitespaces('') == ''
        assert replace_whitespaces('a') == 'a'
        assert replace_whitespaces(' a') == 'a'
        assert replace_whitespaces('\na') == 'a'
        assert replace_whitespaces('a ') == 'a'
        assert replace_whitespaces(' a ') == 'a'
        assert replace_whitespaces('\na\n') == 'a'
        assert replace_whitespaces('a a') == 'a a'
        assert replace_whitespaces('a  a') == 'a a'
        assert replace_whitespaces('a\na') == 'a a'
        assert replace_whitespaces('\\') == '\\'
        assert replace_whitespaces(' \\ ') == '\\'
        assert replace_whitespaces('\n\ta\nn\t\n           g-') == 'a n g-'

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
        assert re_whitespace.sub(' ', '  ') == ' '
        assert re_whitespace.sub(' ', '  a') == ' a'
        assert re_whitespace.sub(' ', '\n\t  <') == ' <'
        assert re_whitespace.sub(' ', '\n\t  A\n\t	') == ' A '

    def test_currency_regex(self):
        assert re_currency_matches('a$1bounty') == [1]
        assert re_currency_matches('a $1 bounty') == [1]
        assert re_currency_matches('$1') == [1]
        assert re_currency_matches('$1.2') == [1.2]
        assert re_currency_matches('$1,000') == [1000]
        assert re_currency_matches('$1,000.2') == [1000.2]
        assert re_currency_matches('$1,2,3') == [123]
        assert re_currency_matches('$1,2.3') == [12.3]
        assert re_currency_matches('received $41,165 from prominent') == [41165]
        assert re_currency_matches('another $300-$400 million') == [300000000, 400000000]
        assert re_currency_matches('$1 $2') == [1, 2]
        assert re_currency_matches('$5or$6') == [5, 6]
        assert re_currency_matches(' #Clinton $12,000,000.00 t… ') == [12000000]
        assert re_currency_matches(' #Clinton $12,000,000.00 t... ') == [12000000]
        assert re_currency_matches(' #Clinton $12.00 t ') == [12000000000000]
        assert re_currency_matches(' #Clinton $12 t ') == [12000000000000]
        assert re_currency_matches('take $12M from') == [12000000]
        assert re_currency_matches('Her $10,000 For') == [10000]
        assert re_currency_matches('ISIS $400 million') == [400000000]
        assert re_currency_matches('Pardon-$5mill Removal from terror list-$3mill Drone strike-$10mill Sp') == [5000000, 3000000, 10000000]
        assert re_currency_matches('receives $10s of millions') == [10]

    def test_currency_regex_no_number(self):
        #FIXME
        assert re_currency_matches('loses $1 in the first place?" ') == [1]
        assert re_currency_matches('loses 1 dollar in the first place?" ') == [1]
        assert re_currency_matches('loses a dollar in the first place?" ') == [1]
        assert re_currency_matches('loses one dollar in the first place?" ') == [1]
        assert re_currency_matches('loses a thousand dollars in the first place?" ') == [1000]
        assert re_currency_matches('loses a million dollars in the first place?" ') == [1000000]
        assert re_currency_matches('loses a billion dollars in the first place?" ') == [1000000000]
        assert re_currency_matches('loses a trillion dollars in the first place?" ') == [1000000000000]


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
