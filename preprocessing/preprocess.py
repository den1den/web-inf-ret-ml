import os

from config import config
from config.config import PCLOUD_DIR

from inputoutput.readers import CSVInputReader, InputReader, JSONInputReader
from inputoutput.writers import CSVWriter
from preprocessing.article_preprocessor import ArticlePreprocessor, ArticlePreprocessorSander
from preprocessing.tweet_preprocessor import TweetPreprocessor


#
# Execution functions
#
def pp_tweets():
    # Read and process all tweets from config.TWEETS_RAW_HOMEDIR
    inputdir = os.path.join(config.PCLOUD_BUFFER_DIR, '')
    inputdir = r'T:\FILEZILLA PUBLIC FOLDER\WebInfRet\newoutput\tweets_valid_20161003_20161115'
    outputdir_tweets = os.path.join(os.path.dirname(inputdir), 'preprocessed_tweets')
    outputdir_tusers = os.path.join(os.path.dirname(inputdir), 'preprocessed_tusers')

    pre_processor = TweetPreprocessor(
        InputReader(inputdir),
        CSVWriter(outputdir_tweets, 'tweets', clear_output_dir=True, columns=TweetPreprocessor.TWEET_COLUMNS),
        CSVWriter(outputdir_tusers, 'tusers', clear_output_dir=True, columns=TweetPreprocessor.TUSER_COLUMNS)
    )
    pre_processor()


def pp_articles_adrian():
    # Read and process all tweets from config.TWEETS_RAW_HOMEDIR
    inputdir = ''.join([PCLOUD_DIR, '\crawler results'])

    outputdir_articles = os.path.join(os.path.dirname(inputdir), 'preprocessed_articles\\adrian_results')
    outputdir_authors = os.path.join(os.path.dirname(inputdir), 'preprocessed_authors\\adrian_results')

    pre_processor = ArticlePreprocessor(
        InputReader(inputdir),
        CSVWriter(outputdir_articles, 'articles', clear_output_dir=True, columns=ArticlePreprocessor.ARTICLE_COLUMNS),
        CSVWriter(outputdir_authors, 'authors', clear_output_dir=True, columns=ArticlePreprocessor.AUTHOR_COLUMNS)
    )
    pre_processor()


def pp_articles_sander():
    # Read and process all tweets from config.TWEETS_RAW_HOMEDIR
    inputdir = ''.join([PCLOUD_DIR, '\JSON results'])

    outputdir_articles = os.path.join(os.path.dirname(inputdir), 'preprocessed_articles\\sander_results')
    outputdir_authors = os.path.join(os.path.dirname(inputdir), 'preprocessed_authors\\sander_results')

    pre_processor = ArticlePreprocessorSander(
        JSONInputReader(inputdir),
        CSVWriter(outputdir_articles, 'articles', clear_output_dir=True, columns=ArticlePreprocessor.ARTICLE_COLUMNS),
        CSVWriter(outputdir_authors, 'authors', clear_output_dir=True, columns=ArticlePreprocessor.AUTHOR_COLUMNS)
    )
    pre_processor()


if __name__ == '__main__':
    pp_articles_sander()
