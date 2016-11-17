import json
import os
import time

from config.config import TWEETS_HOMEDIR
from models.article import Article
from models.tuser import TUser
from models.tweet import Tweet
from preprocessing import preprocess as pp


def get_tweets(tweets_n=None, file_n=None, file_offset=0, dir='PreprocessingTweet', filename_prefix=''):
    """
    Read in tweets from files
    see input.read_json_array_from_files()
    :rtype [Tweet]
    """
    return read_json_array_from_files(to_tweet, os.path.join(TWEETS_HOMEDIR, dir), tweets_n, 0, file_n, file_offset,
                                      filename_prefix)


def to_tweet(plain_data):
    """"This actually creates the Tweet objects"""
    return Tweet(pp.preprocess_tweet(plain_data))


def get_tusers(users_n=None, file_n=None, file_offset=0, dir='PreprocessingUser', filename_prefix=''):
    """
    Read in twitter user accounts from files
    see input.read_json_array_from_files()
    """
    return read_json_array_from_files(to_tuser, os.path.join(TWEETS_HOMEDIR, dir), users_n, 0, file_n, file_offset,
                                      filename_prefix)


def to_tuser(plain_data):
    """"This actually creates the TUser objects"""
    plain_data['id'] = plain_data.pop('userid')
    return TUser(plain_data)


def get_articles(articles_n=None, file_n=None, file_offset=0, dir='PreprocessingRSS', filename_prefix=''):
    """
    Read in twitter user accounts from files
    see input.read_json_array_from_files()
    """
    #filename_prefix = '2016100'
    return read_json_array_from_files(to_article, os.path.join(TWEETS_HOMEDIR, dir), articles_n, 0, file_n, file_offset,
                                      filename_prefix)


def to_article(plain_data):
    """"This actually creates the Article objects"""
    return Article(pp.preprocess_article(plain_data))

#
# Default IO util functions
#


def as_id_dict(data):
    return {d.id: d for d in data}


def read_json_array_from_files(dict_to_obj, dirpath, item_count=None, item_offset=0, file_count=None, file_offset=0,
                               filename_prefix=''):
    """
    :param dict_to_obj: function from dict -> object to sto
    :param dirpath: abs path to directory to read from
    :param item_offset: number of object to read in total
    :param item_count: number of items to read
    :param file_offset: starting index of the file to read
    :param file_count: number of files to read
    :param filename_prefix: filter on the filenames
    :return: obj[]
    """
    filecounter = 0
    items = []

    if filename_prefix is None: filename_prefix = ''

    if filename_prefix == '':
        print("Input: Start reading %s, with offset %d, from %s `%s*` files, with offset %d in `%s`" %
              (item_count or 'all', item_offset, file_count or 'all', filename_prefix, file_offset, dirpath,))
    else:
        print("Input: Start reading %s, with offset %d, from %s files, with offset %d in `%s`" %
              (item_count or 'all', item_offset, file_count or 'all', file_offset, dirpath,))

    # Start walking the filesystem
    t0 = time.time()
    for dirpath, dn, fn in os.walk(dirpath):
        for filename in fn:
            if filename.endswith('.rar'):
                print("Skipping ,rar file: %s" % filename)
                continue
            if filename[0:len(filename_prefix)] == filename_prefix:
                # File matches
                filecounter += 1
                if filecounter < file_offset:
                    continue
                filepath = os.path.join(dirpath, filename)
                file_items = _proccess_file(dict_to_obj, filepath)
                if item_offset > len(file_items):
                    raise IOError(
                        "Cannot have an offset of %d in a file with %d entries" % (item_offset, len(file_items)))

                items += file_items[item_offset:item_offset + item_count - len(items)]

                # Offset is applied, so reset it
                item_offset = 0
    t1 = time.time()

    if len(items) != item_count:
        raise AssertionError(
            "Input error: Could only read %d of %d %s" % (len(items), item_count, verbosity_subject_plural))

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
