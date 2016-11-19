import csv
import json
import os
import time

from config import config
from models.article import Article
from models.tuser import TUser
from models.tweet import Tweet

TWEETS_DIR = os.path.join(config.PCLOUD_DIR, 'PreprocessingTweet')
TWEET_USERS_DIR = os.path.join(config.PCLOUD_DIR, 'PreprocessingUser')
ARTICLES_DIR = os.path.join(config.PCLOUD_DIR, 'PreprocessingRSS')


def get_tweets(tweets_n=None, file_n=None, file_offset=0, dir=TWEETS_DIR, filename_prefix=''):
    """
    Read in tweets from files
    see input.read_json_array_from_files()
    :rtype [Tweet]
    """
    return read_json_array_from_files(to_tweet, dir, tweets_n, 0, file_n, file_offset,
                                      filename_prefix)


def to_tweet(preprocessed_data):
    """"This actually creates the Tweet objects"""
    return Tweet(preprocessed_data)


def get_tusers(users_n=None, file_n=None, file_offset=0, dir=TWEET_USERS_DIR, filename_prefix=''):
    """
    Read in twitter user accounts from files
    see input.read_json_array_from_files()
    """
    return read_json_array_from_files(to_tuser, dir, users_n, 0, file_n, file_offset,
                                      filename_prefix)


def to_tuser(preprocessed_data):
    """"This actually creates the TUser objects"""
    return TUser(preprocessed_data)


def get_articles(articles_n=None, file_n=None, file_offset=0, dir=ARTICLES_DIR, filename_prefix=''):
    """
    Read in twitter user accounts from files
    see input.read_json_array_from_files()
    """
    # filename_prefix = '2016100'
    return read_json_array_from_files(to_article, dir, articles_n, 0, file_n, file_offset,
                                      filename_prefix)


def to_article(preprocessed_data):
    """"This actually creates the Article objects"""
    return Article(preprocessed_data)


#
# Generic IO util functions
#

def as_id_dict(data):
    return {d.id: d for d in data}


def read_json_array_from_files(dict_to_obj, dirpath, item_count=None, item_offset=0, file_count=None, file_offset=0,
                               filename_prefix='', filename_postfix='.json', dirname_prefix='', file_alternation=1, file_alternation_index=0):
    """
    Loads in json arrays from a directory recursively
    :param dict_to_obj: function from dict -> object to sto
    :param dirpath: abs path to directory to read from
    :param item_offset: number of object to skip in total
    :param item_count: number of items to read in total
    :param file_offset: starting index of the file to read
    :param file_count: number of files to read
    :param filename_prefix: filter on the filenames
    :param filename_postfix: filter on the filenames
    :return: obj[]
    """
    filecounter = 0
    items = []

    print("Input: Start reading %s entries (with entry offset %d) from %s `%s*%s` files (with file offset %d) from `%s`" %
          (item_count or 'all', item_offset, file_count or 'all', filename_prefix, filename_postfix, file_offset,
           dirpath,))

    # Start walking the filesystem
    t0 = time.time()
    for dirpath, dn, fn in os.walk(dirpath):
        lowercase_dirname = os.path.basename(dirpath)
        if not lowercase_dirname.startswith(dirname_prefix):
            continue
        for filename in fn:
            # Check if file should be read
            lowercase_filename = filename.lower()
            if not lowercase_filename.endswith(filename_postfix) or not lowercase_filename.startswith(filename_prefix):
                continue
            filecounter += 1
            if filecounter < file_offset:
                continue
            if file_count is not None and filecounter - file_offset == file_count:
                break

            # Read file
            filepath = os.path.join(dirpath, filename)
            items_to_read = None if item_count is None else item_count - len(items)
            applied_offset, file_items = _proccess_file(dict_to_obj, filepath, item_offset, items_to_read)
            items += file_items
            if len(items) == item_count:
                break
            item_offset -= applied_offset

        if len(items) == item_count:
            break
        if filecounter is not None and filecounter - file_offset == file_count:
            break
    t1 = time.time()

    if item_count is not None and len(items) != item_count:
        raise AssertionError(
            "Input error: Could only read %d of %d entries" % (len(items), item_count))

    if filecounter == 0:
        raise IOError("Input error: No files read!")

    duration = t1 - t0
    print("Input ok: %d entries read from %d files (%.2f sec per file, %.0f seconds in total)\n" % (
        len(items), filecounter, duration / filecounter, duration))
    return items


def _proccess_file(dict_to_obj, filepath, item_offset, item_count):
    """"Reads from filepath to an array of tweets"""
    assert item_count != 0

    try:
        with open(filepath, encoding='utf8') as data_file:
            plain_objects = json.load(data_file)  # Depr: object_hook=lambda d: Tweet(**d)
        print("Input file read: %s" % filepath)
    except Exception as e:
        print("Could not read file %s, not a valid JSON file" % filepath)
        raise e
    if item_offset > len(plain_objects):
        print("Warning: read in file of %d objects while offset of %d is bigger then entry count" % (len(plain_objects), item_offset))
        return len(plain_objects), []

    end_index = len(plain_objects) if item_count is None else item_offset + item_count
    items = []
    for plain_object in plain_objects[item_offset:end_index]:
        try:
            obj = dict_to_obj(plain_object)
        except Exception as e:
            raise ValueError(filepath, plain_object, e)
        if obj is not None:
            items.append(obj)
            if item_count is not None and len(items) >= item_count:
                break
    return 0, items


def csv_write(filepath, items, columns=None):
    if len(items) == 0:
        print("Warning: there are no items to write to %s" % filepath)
        return
    if columns is None:
        columns = [col for col in items[0].keys()]
        print("Info: writing csv with columns %s" % columns)
    if not filepath.endswith('.csv'):
        print("Warning: writing csv to file without .csv extension")
    written_items = []
    with open(filepath, 'w+', encoding='utf8', newline='\n') as fp:
        writer = csv.writer(fp, delimiter=';')
        writer.writerow(columns)
        for item in items:
            out_item = {key: (item[key] if (key in item and item[key] is not None) else '') for key in columns}
            writer.writerow([out_item[col] for col in columns])
            written_items.append(out_item)
    print("Info: %d items written to %s" % (len(items), filepath))
    return written_items


def csv_read(filepath, column=None):
    """
    Warning: will not read correct data type
    """
    if not filepath.endswith('.csv'):
        print("Warning: writing csv to file without .csv extension")
    items = []
    if not os.path.exists(filepath):
        print("Warning: file not found, could not read from %s" % filepath)
        return items
    with open(filepath, 'r', encoding='utf8', newline='\n') as fp:
        data = csv.reader(fp, delimiter=';')
        if column is None:
            header = [column for column in next(data)]
        else:
            header = [column for column in next(data) if column in column]
        for line, item in enumerate(data):
            items.append({header[i]: value for i, value in enumerate(item)})
    print("Info: %d items read from %s" % (len(items), filepath))
    return items
