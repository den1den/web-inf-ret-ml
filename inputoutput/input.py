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


def get_tweets(tweets_n=None, file_n=None, file_offset=0, dir_path=TWEETS_DIR, filename_prefix=''):
    """
    Read in tweets from files
    see input.read_json_array_from_files()
    :rtype [Tweet]
    """
    r = Reader(to_tweet, dir_path, tweets_n, 0, file_n, file_offset, filename_prefix)
    return r.read()


def to_tweet(preprocessed_data):
    """"This actually creates the Tweet objects"""
    return Tweet(preprocessed_data)


def get_tusers(users_n=None, file_n=None, file_offset=0, dir_path=TWEET_USERS_DIR, filename_prefix=''):
    """
    Read in twitter user accounts from files
    see input.read_json_array_from_files()
    """
    r = Reader(to_tuser, dir_path, users_n, 0, file_n, file_offset, filename_prefix)
    return r.read()


def to_tuser(preprocessed_data):
    """"This actually creates the TUser objects"""
    return TUser(preprocessed_data)


def get_articles(articles_n=None, file_n=None, file_offset=0, dir_path=ARTICLES_DIR, filename_prefix=''):
    """
    Read in twitter user accounts from files
    see input.read_json_array_from_files()
    """
    # filename_prefix = '2016100'
    r = Reader(to_article, dir_path, articles_n, 0, file_n, file_offset, filename_prefix)
    return r.read()


def to_article(preprocessed_data):
    """"This actually creates the Article objects"""
    return Article(preprocessed_data)


#
# Generic IO util functions
#

def as_id_dict(data):
    return {d.id: d for d in data}


class Reader():
    """
    Loads in json arrays from a directory recursively
    :param d2o: function from dict -> object to sto
    :param dir_path: abs path to directory to read from
    :param self.item_count: number of items to read in total
    :param self.item_offset: number of object to skip in total
    :param self.file_count: number of files to read
    :param self.file_offset: starting index of the file to read
    :param filename_prefix: filter on the filenames
    :param self.filename_postfix: filter on the filenames
    :param self.dir_name_prefix:
    :param file_alternation:
    :param file_alternation_index:
    :param give_filename_to_d2o: provide extra argument `filename` to d2o function
    """
    supply_reader = False

    def __init__(self, dict_to_obj, dir_path, item_count=None, item_offset=0, file_count=None, file_offset=0,
                 filename_prefix='', filename_postfix='.json',
                 dir_name_prefix='', file_alternation=1, file_alternation_index=0):
        self.dict_to_obj = dict_to_obj
        self.dir_path = dir_path
        self.item_count = item_count
        self.item_offset = item_offset
        self.file_count = file_count
        self.file_offset = file_offset
        self.filename_prefix = filename_prefix
        self.filename_postfix = filename_postfix
        self.dir_name_prefix = dir_name_prefix
        self.file_alternation = file_alternation
        self.file_alternation_index = file_alternation_index

    def read(self):
        self.filecounter = 0
        self.items = []

        print(
            "Input: Start reading %s entries (with entry offset %d) from %s `%s*%s` files (with file offset %d) from `%s`" %
            (self.item_count or 'all', self.item_offset, self.file_count or 'all', self.filename_prefix,
             self.filename_postfix, self.file_offset,
             self.dir_path,))

        # Start walking the filesystem
        t0 = time.time()
        for self.dir_path, dn, fn in os.walk(self.dir_path):
            lowercase_dir_name = os.path.basename(self.dir_path)
            if not lowercase_dir_name.startswith(self.dir_name_prefix):
                continue
            for filename in fn:
                # Check if file should be read
                lowercase_filename = filename.lower()
                if not lowercase_filename.endswith(self.filename_postfix)\
                        or not lowercase_filename.startswith(self.filename_prefix):
                    continue
                self.filecounter += 1
                if self.filecounter < self.file_offset:
                    continue
                if self.file_count is not None and self.filecounter - self.file_offset == self.file_count:
                    break

                # Read file
                self.current_file = os.path.join(self.dir_path, filename)
                if not self._proccess_file():
                    break

            if len(self.items) == self.item_count:
                break
            if self.filecounter is not None and self.filecounter - self.file_offset == self.file_count:
                break
        t1 = time.time()

        if self.item_count is not None and len(self.items) != self.item_count:
            raise AssertionError(
                "Input error: Could only read %d of %d entries" % (len(self.items), self.item_count))

        if self.filecounter == 0:
            raise IOError("Input error: No files read!")

        duration = t1 - t0
        print("Input ok: %d entries read from %d files (%.2f sec per file, %.0f seconds in total)\n" % (
            len(self.items), self.filecounter, duration / self.filecounter, duration))
        return self.items

    def _proccess_file(self):
        """"Reads from filepath to an array of tweets"""
        assert self.item_count != 0

        try:
            with open(self.current_file, encoding='utf8') as data_file:
                plain_objects = json.load(data_file)
            print("Input file read: %s" % self.current_file)
        except Exception as e:
            print("Could not json.load file %s" % self.current_file)
            raise e
        if self.item_offset > len(plain_objects):
            print("Warning: read in file of %d objects while offset of %d is bigger then entry count" % (
                len(plain_objects), self.item_offset))
            self.item_offset -= plain_objects
            return True

        self.i = 0
        end_index = len(plain_objects) if self.item_count is None else self.item_offset + self.item_count
        for plain_object in plain_objects[self.item_offset:end_index]:
            try:
                if self.supply_reader:
                    obj = self.dict_to_obj(plain_object, self)
                else:
                    obj = self.dict_to_obj(plain_object)
            except Exception as e:
                if 'text' in plain_object:
                    print(plain_object['text'])
                if 'id' in plain_object:
                    print("id = %s" % plain_object['id'])
                raise ValueError(self.current_file, plain_object, e)
            if obj is not None:
                self.items.append(obj)
                self.i += 1
                if self.item_count is not None and len(self.items) >= self.item_count:
                    return False
        return True

    def __str__(self, *args, **kwargs):
        return "file: %s at entry %d" % (self.current_file, self.i)


def read_json_array_from_files(*args, **kwargs):
    r = Reader(*args, **kwargs)
    return r.read()


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
        writer = csv.writer(fp, delimiter=';', dialect='excel')
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
