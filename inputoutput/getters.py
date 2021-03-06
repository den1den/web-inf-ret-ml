import os
from datetime import date, timedelta

from config import config
from inputoutput.readers import CSVInputReader, InputReader, Input2000Reader
from models.article import Article
from models.tuser import TUser
from models.tweet import Tweet

TWEETS_DIR = os.path.join(config.PCLOUD_DIR, 'tweets')
TWEET_USERS_DIR = os.path.join(config.PCLOUD_DIR, 'users')
ARTICLES_DIR = os.path.join(config.PCLOUD_DIR, 'preprocessed_articles', 'sander_results')
ARTICLES_DIR_BY_DATE = os.path.join(config.PCLOUD_DIR, 'preprocessed_articles', 'sander_results_bydate')


def update_tweets_cache(start_date: date, end_date: date, tweets_cache: dict):
    date_strs = []
    d = start_date
    while d <= end_date:
        date_strs.append(d.strftime('tweets_%Y_%m_%d'))
        d += timedelta(days=1)
    # remove from cache whats not in this range
    remove_keys = []
    for (k, v) in tweets_cache.items():
        if k not in date_strs:
            remove_keys.append(k)
    for k in remove_keys:
        del tweets_cache[k]
    # Add elements that were not in the cache
    i = 0
    for k in date_strs:
        if k not in tweets_cache:
            tweets = get_tweets(filename_prefix=k)
            if len(tweets) > 0:
                tweets_cache[k] = tweets
                i += 1
    print("update_tweets_cache(removed=%d, added=%d, size=%d)" % (len(remove_keys), i, len(tweets_cache)))


def get_tweets_count_by_date(start_date: date, end_date: date):
    n = 0
    d = start_date
    while d <= end_date:
        n += get_tweet_count(filename_prefix=d.strftime('tweets_%Y_%m_%d'))
        d += timedelta(days=1)
    return n


def get_tweets_by_date(start_date: date, end_date: date):
    tweets = []
    d = start_date
    while d <= end_date:
        tweets += get_tweets(filename_prefix=d.strftime('tweets_%Y_%m_%d'))
        d += timedelta(days=1)
    return tweets


def get_tweet_count(file_offset=0, dir_path=TWEETS_DIR, filename_prefix=''):
    """
    Read in tweets from files
    see input.read_json_array_from_files()
    :rtype [Tweet]
    """
    from preprocessing.tweet_preprocessor import TweetPreprocessor
    r = Input2000Reader(dir_path, TweetPreprocessor.TWEET_COLUMNS, file_offset=file_offset,
                       filename_prefix=filename_prefix)
    all = r.count_all(to_tweet)
    if all == 0:
        return 0
    all -= 20000 - 1
    # really read the last
    # next_file = "%s%d%s" % (r.current_file[:-5], int(r.current_file[-5]) + 1,  r.current_file[-4:])
    r = CSVInputReader(dir_path, TweetPreprocessor.TWEET_COLUMNS, filename_prefix=os.path.basename(r.current_file))
    all += len(r.read_all(to_tweet))
    return all


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


def get_articles(articles_n=None, file_offset=0, dir_path=ARTICLES_DIR, filename_prefix=''):
    """
    Read in twitter user accounts from files
    see input.read_json_array_from_files()
    """
    from preprocessing.article_preprocessor import ArticlePreprocessor
    r = CSVInputReader(dir_path, ArticlePreprocessor.ARTICLE_COLUMNS, file_offset=file_offset, filename_prefix=filename_prefix)
    return r.read_all(to_article, item_count=articles_n)


def get_articles_by_date(articles_n=None, file_offset=0, dir_path=ARTICLES_DIR_BY_DATE, filename_prefix=''):
    return get_articles(articles_n=articles_n, file_offset=file_offset, dir_path=dir_path, filename_prefix=filename_prefix)


def to_article(preprocessed_data):
    """"This actually creates the Article objects"""
    return Article(preprocessed_data)
