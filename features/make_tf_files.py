import os

from config.config import PROJECT_DIR
from features.term_frequency import write_tf_idf
from inputoutput.input import get_tweets, CSVInputReader, to_tweet

tweet_idf_json_filename = os.path.join(PROJECT_DIR, 'idf_tweet2.json')
tweet_idf_csv_filename = os.path.join(PROJECT_DIR, 'idf_tweet2.csv')

from preprocessing.tweet_preprocessor import TweetPreprocessor
r = CSVInputReader('G:\p-tweets-09-28-till-10-31', TweetPreprocessor.TWEET_COLUMNS, file_offset=0, filename_prefix='')
tweets = r.read_all(to_tweet, None, item_offset=30*20000)
write_tf_idf(tweets, tweet_idf_json_filename, tweet_idf_csv_filename)
