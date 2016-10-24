import json
import os
import time

from config.config import TWEETS_HOMEDIR
from models.tuser import TUser
from models.tweet import Tweet
from preprocessing import preprocess as pp


def get_tweets(tweets_n=None, file_n=None, file_offset=0, dir='PreprocessingTweet', filename_prefix='xa'):
    """
    Read in tweets from files
    see input.read_json_array_from_files()
    """
    return read_json_array_from_files(to_tweet, "tweets", tweets_n, file_n, file_offset, dir, filename_prefix)


def to_tweet(plain_data):
    return Tweet(pp.preprocess_tweet(plain_data))


def get_tusers(users_n=None, file_n=None, file_offset=0, dir='PreprocessUser', filename_prefix='xa'):
    """
    Read in twitter user accounts from files
    see input.read_json_array_from_files()
    """
    return read_json_array_from_files(to_tuser, "tusers", users_n, file_n, file_offset, dir, filename_prefix)


def to_tuser(plain_data):
    return TUser(plain_data)


#
# Default IO util functions
#


def as_id_dict(data):
    return {d.id: d for d in data}


def read_json_array_from_files(dict_to_obj, verbosity_subject_plural='?', N=None, file_n=None, file_offset=0, dir='',
                               filename_prefix=''):
    """
    :param dict_to_obj: function from dict -> object to store
    :param verbosity_subject_plural
    :param N: number of object to read in total
    :param file_n: number of files to read
    :param file_offset: starting index of the file to read
    :param dir: directory to read from
    :param filename_prefix: filter on the filenames
    :return: Tweet[]
    """
    filecounter = 0  # Filecounter
    items = []
    abs_dir = os.path.join(TWEETS_HOMEDIR, dir)

    if filename_prefix is None: filename_prefix = ''

    if filename_prefix == '':
        print("Input: Start reading from all files recursivly in `%s`, limit = %s" % (abs_dir, N, ))
    else:
        print("Input: Start reading from all `%s*` files recursivly in `%s`, limit = %s" % (filename_prefix, abs_dir, N, ))

    # Start walking the filesystem
    t0 = time.time()
    for dp, dn, fn in os.walk(abs_dir):
        for tweet_filename in fn:
            if tweet_filename[0:len(filename_prefix)] == filename_prefix:
                if filecounter < file_offset:
                    continue
                filename = os.path.join(dp, tweet_filename)
                file_tweets = _proccess_file(dict_to_obj, filename)
                filecounter += 1
                if N is not None and len(items) + len(file_tweets) > N:
                    items += file_tweets[0:N - len(items)]
                    break
                items += file_tweets
                if file_n is not None and filecounter == file_n:
                    break
    t1 = time.time()

    if N is not None and len(items) != N:
        raise AssertionError(
            "Input error: Could only read %d of %d %s" % (len(items) or 0, N, verbosity_subject_plural))

    if filecounter == 0:
        raise IOError("Input error: No files read!")

    duration = t1 - t0
    print("Input ok: %d %s read from %d files (%.2f sec per file, %.0f seconds in total)\n" % (
        len(items), verbosity_subject_plural, filecounter, duration / filecounter, duration))
    return items


def _proccess_file(dict_to_obj, filename):
    """"Reads from filename to an array of tweets"""
    items = []
    try:
        with open(filename, encoding='utf8') as data_file:
            plain_objects = json.load(data_file)  # Depr: object_hook=lambda d: Tweet(**d)
    except Exception as e:
        print("Could not read file %s, not a valid JSON file" % filename)
        raise e
    print("Input file parsed: %s" % filename)
    for plain_object in plain_objects:
        try:
            items.append(dict_to_obj(plain_object))
        except Exception as e:
            print("Error while parsing: %s\nOriginal: %s" % (filename, plain_objects))
            raise e
    return items
