import csv
import json
import math
import os
from collections import OrderedDict

from config.config import PROJECT_DIR
from inputoutput.input import get_tweets, get_articles

df_tweet_filename = os.path.join(PROJECT_DIR, 'df_tweet_t.json')
idf_tweet_filename = os.path.join(PROJECT_DIR, 'idf_tweet.json')
idf_tweet_csv_filename = os.path.join(PROJECT_DIR, 'idf_tweet.csv')

idf_article_filename = os.path.join(PROJECT_DIR, 'idf_article.json')


def write_idf_articles():
    write_tf(get_articles, 'get_keywords', None, idf_article_filename, None)


def write_idf_tweets():
    write_tf(get_tweets, 'get_keywords', df_tweet_filename, idf_tweet_filename, idf_tweet_csv_filename)


def write_tf(data_getter, keywords_function_name: str, df_filename, idf_filename, idf_csv_filename):
    documents = data_getter()
    df = {}
    for doc in documents:
        keywords_function = getattr(doc, keywords_function_name)
        for word in set(keywords_function()):
            if word in df:
                df[word] += 1
            else:
                df[word] = 1

    if df_filename is not None:
        # Print df
        sorted_df = OrderedDict(sorted(df.items()))
        json.dump(sorted_df, open(df_filename, '+w'), indent=1)

    idf = {term: math.log(len(documents) / df_t) for (term, df_t) in df.items()}
    sorted_idf = OrderedDict(sorted(idf.items()))
    if idf_filename is not None:
        # Print idf
        json.dump(sorted_idf, open(idf_filename, '+w'), indent=1)

    if idf_csv_filename is not None:
        # Print idf to csv
        with open(idf_csv_filename, '+w', encoding='utf8', newline='\n') as fp:
            writer = csv.writer(fp, delimiter=';')
            writer.writerow(['term', 'idf_t'])
            for (term, idf_t) in sorted_idf.items():
                writer.writerow((term, str(idf_t).replace('.', ','),))


def get_idf_tweets():
    with open(idf_tweet_filename, 'r') as fp:
        d = json.load(fp)
    return d


def get_idf_articles():
    with open(idf_article_filename, 'r') as fp:
        d = json.load(fp)
    return d
