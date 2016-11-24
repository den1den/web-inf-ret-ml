import os

from config import config
from inputoutput.input import InputReader, CSVWriter
from preprocessing.article_preprocessor import ArticlePreprocessor
from preprocessing.tweet_preprocessor import TweetPreprocessor

REPORT_DUPLICATE = False


#
# Execution functions
#

def pp_tweets():
    # Read and process all tweets from config.TWEETS_RAW_HOMEDIR
    inputdir = os.path.join(config.PCLOUD_BUFFER_DIR, 'raw-tweets')
    outputdir_tweets = os.path.join(config.PCLOUD_BUFFER_DIR, 'preprocessed-tweets')
    outputdir_tusers = os.path.join(config.PCLOUD_BUFFER_DIR, 'preprocessed-tusers')

    pre_processor = TweetPreprocessor(
        InputReader(inputdir),
        CSVWriter(outputdir_tweets, 'tweets', clear_output_dir=True, columns=TweetPreprocessor.TWEET_COLUMNS),
        CSVWriter(outputdir_tusers, 'tusers', clear_output_dir=True, columns=TweetPreprocessor.TUSER_COLUMNS)
    )
    pre_processor()


def pp_articles():
    # Read and process all tweets from config.TWEETS_RAW_HOMEDIR
    inputdir = os.path.join(config.PCLOUD_BUFFER_DIR, 'raw-articles')
    outputdir_articles = os.path.join(config.PCLOUD_BUFFER_DIR, 'preprocessed-articles')
    outputdir_authors = os.path.join(config.PCLOUD_BUFFER_DIR, 'preprocessed-authors')

    pre_processor = ArticlePreprocessor(
        InputReader(inputdir),
        CSVWriter(outputdir_articles, 'articles', clear_output_dir=True, columns=ArticlePreprocessor.ARTICLE_COLUMNS),
        CSVWriter(outputdir_authors, 'authors', clear_output_dir=True, columns=ArticlePreprocessor.AUTHOR_COLUMNS)
    )
    pre_processor()


if __name__ == '__main__':
    pp_articles()
