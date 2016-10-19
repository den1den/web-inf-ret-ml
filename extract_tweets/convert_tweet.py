import json
import os
import time

from config.config import TWEETS_HOMEDIR
from extract_tweets.models import Tweet
from preprocessing import preprocess as pp


def get_tweets(tweets_n=None, file_n=None, file_offset=0, dir='PreprocessingTweet', filename_start='xa'):
    """
    TODO; to be determined what data set later on
    :param tweets_n: number of tweets in total limit
    :param file_offset: Starting file index
    :param file_n: Ending file index
    :param dir:
    :return: Tweet[]
    """
    filecounter = 0  # Filecounter
    tweets = []
    abs_dir = os.path.join(TWEETS_HOMEDIR, dir)

    # Start walking the filesystem
    t0 = time.time()
    for dp, dn, fn in os.walk(abs_dir):
        for tweet_filename in fn:
            if tweet_filename[0:len(filename_start)] == filename_start:
                if filecounter < file_offset:
                    continue
                filename = os.path.join(dp, tweet_filename)
                file_tweets = convert_tweets(filename)
                filecounter += 1
                if tweets_n is not None and len(tweets) + len(file_tweets) > tweets_n:
                    tweets += file_tweets[0:tweets_n - len(tweets)]
                    break
                tweets += file_tweets
                if file_n is not None and filecounter == file_n:
                    break
    t1 = time.time()

    # Gives the tweets unique IDs
    pp.give_unique_ids(tweets)

    if tweets_n is not None and len(tweets) != tweets_n:
        raise AssertionError("Input error: Could only read %d of %d tweets" % (len(tweets) or 0, tweets_n))

    if filecounter == 0:
        raise IOError("Input error: No files read!")

    duration = t1 - t0
    print("Input ok: %d tweets read from %d files (%.2f sec per file, %.0f seconds in total)\n" % (len(tweets), filecounter, duration / filecounter, duration))
    return tweets


def get_tweets_dict(tweets):
    return {tweet.id: tweet for tweet in tweets}


def to_tweet(plain_data):
    return Tweet(pp.preprocess_tweet(plain_data))


def convert_tweets(filename):
    """"Reads from filename to an array of tweets"""
    tweets = []
    with open(filename, encoding='utf8') as data_file:
        plain_objects = json.load(data_file)  # Depr: object_hook=lambda d: Tweet(**d)
    print("Input file JSON parsed: %s" % filename)
    for plain_object in plain_objects:
        try:
            tweets.append(Tweet(pp.preprocess_tweet(plain_object)))
        except Exception as e:
            print("Could not parse tweet from file: %s" % (filename))
            print("Plain tweet data: %s" % (plain_object))
            raise e
    return tweets


if __name__ == "__main__":
    tweets = convert_tweets('xaa.valid.json')

    [print("<>" + str(tweets[i]) + "</>") or print() for i in range(0, 9)]
