import json
import os
import time

from config.config import TWEETS_HOMEDIR
from extract_tweets.models import Tweet


def get_tweets(tweets_n=None, file_n=None, file_offset=0, dir='PreprocessingTweet', filename_start='xa'):
    """
    TODO; to be determined what data set later on
    :param tweets_n: number of tweets in total limit
    :param offset: Starting file index
    :param file_n: Ending file index
    :param dir:
    :return: Tweet[]
    """
    i = 0  # Filecounter
    start = time.time()
    tweets = []
    abs_dir = os.path.join(TWEETS_HOMEDIR, dir)

    for dp, dn, fn in os.walk(abs_dir):
        for tweet_filename in fn:
            if tweet_filename[0:len(filename_start)] == filename_start:
                if i < file_offset:
                    continue
                filename = os.path.join(dp, tweet_filename)
                print("Reading in from %s" % filename)
                file_tweets = convert_tweets(filename)
                if tweets_n is not None and len(tweets) + len(file_tweets) > tweets_n:
                    tweets += file_tweets[0:tweets_n - len(tweets)]
                    break
                tweets += file_tweets
                if file_n is not None and i == file_n:
                    break
                i += 1
    end = time.time()
    if i == 0:
        print("\nNo files found!")
    else:
        print("%s tweet files read: %.2f sec per file (total %.0f seconds)" % (i, (end - start) / i, end - start))
    return tweets


def convert_tweets(filename):
    try:
        with open(filename, encoding='utf8') as data_file:
            plain_objects = json.load(data_file)  # Depr: object_hook=lambda d: Tweet(**d)
            return [Tweet(plain_object) for plain_object in plain_objects]
    except Exception as e:
        print("Could not parse tweet %s %s" % (filename, e))
    return None


if __name__ == "__main__":
    tweets = convert_tweets('xaa.valid.json')

    [print("<>" + str(tweets[i]) + "</>") or print() for i in range(0, 9)]
