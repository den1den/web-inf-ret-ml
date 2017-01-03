import os
from datetime import date, timedelta

from config import config
from inputoutput.readers import CSVInputReader, InputReader
from models.article import Article
from models.tuser import TUser
from models.tweet import Tweet

TWEETS_DIR = os.path.join(config.PCLOUD_DIR, 'tweets')
TWEET_USERS_DIR = os.path.join(config.PCLOUD_DIR, 'users')
ARTICLES_DIR = os.path.join(config.PCLOUD_DIR, 'articles')


def get_tweets_by_date(start_date: date, end_date: date):
    tweets = []
    d = start_date
    while d <= end_date:
        tweets += get_tweets(filename_prefix=d.strftime('tweets_%Y_%m_%d'))
        d += timedelta(days=1)
    return tweets


def get_tweets(tweets_n=None, file_offset=0, dir_path=TWEETS_DIR, filename_prefix=''):
    """
    Read in tweets from files
    see input.read_json_array_from_files()
    :rtype [Tweet]
    """
    from preprocessing.tweet_preprocessor import TweetPreprocessor
    r = CSVInputReader(dir_path, TweetPreprocessor.TWEET_COLUMNS, file_offset=file_offset,
                       filename_prefix=filename_prefix)
    return r.read_all(to_tweet, item_count=tweets_n)


def to_tweet(preprocessed_data):
    """"This actually creates the Tweet objects"""
    return Tweet(preprocessed_data)


def get_tusers(users_n=None, file_offset=0, dir_path=TWEET_USERS_DIR, filename_prefix=''):
    """
    Read in twitter user accounts from files
    see input.read_json_array_from_files()
    """
    r = InputReader(dir_path, file_offset=file_offset, filename_prefix=filename_prefix)
    return r.read_all(to_tuser, item_count=users_n)


def to_tuser(preprocessed_data):
    """"This actually creates the TUser objects"""
    return TUser(preprocessed_data)


def get_articles(articles_n=None, file_offset=0, dir_path=ARTICLES_DIR, filename_prefix='articles_'):
    """
    Read in twitter user accounts from files
    see input.read_json_array_from_files()
    """
    from preprocessing.article_preprocessor import ArticlePreprocessor
    r = CSVInputReader(dir_path, ArticlePreprocessor.ARTICLE_COLUMNS, file_offset=file_offset)
    return r.read_all(to_article, item_count=articles_n)


def to_article(preprocessed_data):
    """"This actually creates the Article objects"""
    return Article(preprocessed_data)
