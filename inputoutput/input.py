import csv
import json
import os
import time

from config import config
from models.article import Article
from models.tuser import TUser
from models.tweet import Tweet

TWEETS_DIR = os.path.join(config.PCLOUD_DIR, 'tweets')
TWEET_USERS_DIR = os.path.join(config.PCLOUD_DIR, 'users')
ARTICLES_DIR = os.path.join(config.PCLOUD_DIR, 'articles')


def get_tweets(tweets_n=None, file_offset=0, dir_path=TWEETS_DIR, filename_prefix=''):
    """
    Read in tweets from files
    see input.read_json_array_from_files()
    :rtype [Tweet]
    """
    from preprocessing.tweet_preprocessor import TweetPreprocessor
    r = CSVInputReader(dir_path, TweetPreprocessor.TWEET_COLUMNS, file_offset=file_offset, filename_prefix=filename_prefix)
    return r.read_all(to_tweet, tweets_n)


def to_tweet(preprocessed_data):
    """"This actually creates the Tweet objects"""
    return Tweet(preprocessed_data)


def get_tusers(users_n=None, file_offset=0, dir_path=TWEET_USERS_DIR, filename_prefix=''):
    """
    Read in twitter user accounts from files
    see input.read_json_array_from_files()
    """
    r = InputReader(dir_path, file_offset=file_offset, filename_prefix=filename_prefix)
    return r.read_all(users_n, to_tuser)


def to_tuser(preprocessed_data):
    """"This actually creates the TUser objects"""
    return TUser(preprocessed_data)


def get_articles(articles_n=None, file_offset=0, dir_path=ARTICLES_DIR, filename_prefix=''):
    """
    Read in twitter user accounts from files
    see input.read_json_array_from_files()
    """

    from preprocessing.article_preprocessor import ArticlePreprocessor
    r = CSVInputReader(dir_path, ArticlePreprocessor.ARTICLE_COLUMNS, file_offset=file_offset,
                       filename_prefix=filename_prefix)

    #r = InputReader(dir_path, file_offset=file_offset, filename_prefix=filename_prefix)
    return r.read_all(articles_n, to_article)


def to_article(preprocessed_data):
    """"This actually creates the Article objects"""
    return Article(preprocessed_data)


#
# Generic IO util functions
#

def as_id_dict(data):
    return {d.id: d for d in data}


class InputReader:
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

    def __init__(self, dir_path, item_offset=0, file_offset=0,
                 filename_prefix='', filename_postfix='.json',
                 dir_name_prefix='',
                 file_alternation=1, file_alternation_index=0):
        self.item_offset = item_offset
        self.file_offset = file_offset
        self.filename_prefix = filename_prefix
        self.filename_postfix = filename_postfix
        self.dir_name_prefix = dir_name_prefix
        self.file_alternation = file_alternation
        self.file_alternation_index = file_alternation_index
        self.dir_path = dir_path
        self.os_walk_iter = iter(os.walk(dir_path))

        self.filecounter = 0  # File counter of files read
        self.nxt_index = 0  # Index of next item to be returned in the raw_items array
        self.raw_items = []  # Last read items
        self.i = 0  # Number of items read so far

    def read_next_file(self):
        """
        Reads in the next file, or returns False when end is reached
        """
        while True:
            filename = self._next_file()
            if filename is None:
                break

            lowercase_filename = filename.lower()
            if not lowercase_filename.endswith(self.filename_postfix):
                # skip non matching files
                continue
            if not lowercase_filename.startswith(self.filename_prefix):
                # skip non matching files
                continue

            # file matches
            self.filecounter += 1
            if self.filecounter < self.file_offset:
                # skip file
                continue

            # Read file
            self.current_file = os.path.join(self.dir_path, filename)
            try:
                self.raw_items = self.read_file()
                self.nxt_index = 0
                return True
            except Exception as e:
                print("Error: could not json.load file %s %s" % (self.current_file, e))
                continue
        return False

    def read_file(self):
        """
        Process the current file
        """
        with open(self.current_file, encoding='utf8') as data_file:
            raw_data = json.load(data_file)
        print("Info: Input file read: %s" % self.current_file)
        return raw_data

    def __iter__(self):
        return self

    def __next__(self):
        while self.nxt_index == len(self.raw_items):
            if self.read_next_file():
                pass
            else:
                raise StopIteration()
        nxt = self.raw_items[self.nxt_index]
        self.nxt_index += 1
        self.i += 1
        return nxt

    def read_all(self, function=lambda x:x, item_count=None):
        print(
            "Info: read all entries (with entry offset %d) from all `%s*%s` files (with file offset %d) from `%s`" %
            (self.item_offset, self.filename_prefix, self.filename_postfix, self.file_offset, self.dir_path)
        )

        t0 = time.time()
        self.items = []
        for item in self:
            try:
                fi = function(item)
                self.items.append(fi)
            except Exception as e:
                print("Error: could not apply function to file %s:%d %s" % (self.current_file, self.i, e))
                pass
            if item_count is not None and len(self.items) >= item_count:
                break
        t1 = time.time()
        duration = t1 - t0

        if item_count is not None and len(self.items) != item_count:
            raise AssertionError("Error: could only read %d of %d entries" % (len(self.items), item_count))

        print(
            "Info: read %d entries read from %d files (%.2f sec per file, %.0f seconds in total)"
            % (len(self.items), self.filecounter, duration / self.filecounter, duration)
        )
        return self.items

    def __str__(self, *args, **kwargs):
        return "file: %s at entry %d" % (self.current_file, self.i)

    fn_iter = None
    def _next_file(self):
        if self.fn_iter is not None:
            try:
                return next(self.fn_iter)
            except StopIteration:
                pass
        try:
            self.dir_path, dn, fn = next(self.os_walk_iter)
            lowercase_dir_name = os.path.basename(self.dir_path)
            if not lowercase_dir_name.startswith(self.dir_name_prefix):
                # skip non matching dirs
                return self._next_file()
            self.fn_iter = iter(fn)
            return self._next_file()
        except StopIteration:
            return None


class CSVInputReader(InputReader):
    def __init__(self, dir_path, columns, item_offset=0, file_offset=0, filename_prefix='', filename_postfix='.csv',
                 dir_name_prefix='', file_alternation=1, file_alternation_index=0):
        super().__init__(dir_path, item_offset, file_offset, filename_prefix, filename_postfix, dir_name_prefix,
                         file_alternation, file_alternation_index)
        self.columns = columns

    def read_file(self):
        raw_data = csv_read(self.current_file, self.columns)
        print("Info: Input file read: %s" % self.current_file)
        return raw_data


class Writer:
    def __init__(self, dir_path, base_filename, write_every=10000, clear_output_dir=False):
        self.dir_path = dir_path
        self.base_filename = base_filename
        self.write_every = write_every
        self.item_buffer = []
        self.filecount = 0
        if clear_output_dir:
            clean_output_dir(self.dir_path)

    def write(self, item):
        self.item_buffer.append(item)
        if len(self.item_buffer) >= self.write_every:
            try:
                self.write_to_file()
            except Exception as e:
                print("Error: could not write to %s %s" % (self.get_file_path(), e))
                pass

    def write_to_file(self):
        filename = self.get_file_path()
        json.dump(self.item_buffer, open(filename, 'w+', encoding='utf8'))
        print("Info: written %d items to %s" % (len(self.item_buffer), filename))
        self.filecount += 1
        self.item_buffer = []

    def get_file_path(self):
        return os.path.join(self.dir_path, '%s_%s.json' % (self.base_filename, self.filecount))

    def close(self):
        self.write_to_file()


class CSVWriter(Writer):
    def __init__(self, dir_path, base_filename, columns, write_every=20000, clear_output_dir=False):
        super().__init__(dir_path, base_filename, write_every, clear_output_dir)
        self.columns = columns

    def write_to_file(self):
        filename = self.get_file_path()
        csv_write(filename, self.item_buffer, self.columns)
        self.filecount += 1
        self.item_buffer = []

    def get_file_path(self):
        return os.path.join(self.dir_path, '%s_%s.csv' % (self.base_filename, self.filecount))


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


def clean_output_dir(dir, filename_postfix=''):
    # Delete previous
    if not os.path.exists(dir):
        os.makedirs(dir)
        return
    for f in os.listdir(dir):
        if f.endswith(filename_postfix):
            old_filepath = os.path.join(dir, f)
            print("removing %s" % old_filepath)
            os.remove(old_filepath)
