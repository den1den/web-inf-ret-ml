import os
import re
from datetime import datetime

from config import config
from inputoutput.readers import csv_read, CSVInputReader
from inputoutput.writers import CSVWriter
from preprocessing.article_preprocessor import ArticlePreprocessor
from preprocessing.tweet_preprocessor import TweetPreprocessor


def tweet_to_date(raw_data_element):
    timestamp = int(raw_data_element['timestamp']) / 1000
    dt = datetime.fromtimestamp(timestamp)
    return dt.date().isoformat().replace('-', '_')


def article_to_date(raw_data_element):
    if 'published_date' not in raw_data_element:
        print('Missing date: %s' % 'published_date')
        return None
    dt = datetime.strptime(raw_data_element['published_date'].split(' ')[0], '%Y-%m-%d')
    return dt.date().isoformat().replace('-', '_')


def µ_tweets():
    sorted_output_dir = 'H:\TWEETS\sorted'
    base_filename = 'tweets'
    columns = TweetPreprocessor.TWEET_COLUMNS
    inputdir = os.path.join(config.PCLOUD_DIR, base_filename, '20161003_20161115')
    µ(sorted_output_dir, base_filename, columns, inputdir, tweet_to_date)


def µ_articles():
    inputdir = r'H:\TWEETS\POST_DL\PRE\articles_sander_results'
    sorted_output_dir = r'H:\TWEETS\POST_DL\PRE\articles_sorted_sander_results'

    base_filename = 'articles'

    columns = ArticlePreprocessor.ARTICLE_COLUMNS

    µ(sorted_output_dir, base_filename, columns, inputdir, article_to_date)


def µ(sorted_output_dir, base_filename, columns, inputdir, tweet_to_date):
    if not os.path.exists(sorted_output_dir):
        os.makedirs(sorted_output_dir)
    # Read and process all tweets from config.TWEETS_RAW_HOMEDIR
    input_index = 0
    for filename in os.listdir(inputdir):
        contents = csv_read(os.path.join(inputdir, filename))
        input_index += 1

        buffer = {}
        for raw_data_element in contents[1:]:
            date_str = tweet_to_date(raw_data_element)
            if date_str is None:
                continue
            if date_str in buffer:
                buffer[date_str].append(raw_data_element)
            else:
                buffer[date_str] = [raw_data_element, ]
        write_buffer(sorted_output_dir, ('%s_%d' % (base_filename, input_index)), buffer, columns)

    # then merge them
    for (dirpath, dirnames, filenames) in os.walk(sorted_output_dir):
        m = re.match('\d{4}_\d{2}_\d{2}', os.path.basename(dirpath))
        if m:
            r = CSVInputReader(dirpath, None)
            w = CSVWriter(sorted_output_dir, '%s_%s_' % (base_filename, m.group(0)), columns)
            for x in r:
                w.write(x)
            w.close()


def write_buffer(outputdir, basefilename, buffer, columns):
    for date, items in buffer.items():
        writer = CSVWriter(os.path.join(outputdir, date), basefilename, columns)
        for item in items:
            writer.write(item)
        writer.close()

µ_articles()
