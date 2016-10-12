import json
import os
import time

from config.config import TWEETS_HOMEDIR
from extract_tweets.models import Tweet


def get_tweets(n=None, offset=0, dir='elections-29-09-raw', filestart='xa'):
    """
    TODO; to be determined what data set later on
    :param n: Ending file
    :param offset: Starting file
    :param dir:
    :return: Tweet
    """
    i = 0  # Filecounter
    start = time.time()
    tweets = []
    abs_dir = os.path.join(TWEETS_HOMEDIR, dir)
    for tweetfilename in os.listdir(abs_dir):
        if tweetfilename[0:len(filestart)] == filestart:
            if i < offset:
                continue
            file_tweets = convert_tweets(os.path.join(abs_dir, tweetfilename))
            tweets += file_tweets
            if n is not None and i == n:
                break
            i += 1
    end = time.time()
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
