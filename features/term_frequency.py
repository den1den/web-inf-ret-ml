import csv
import json
import math
import os
from collections import OrderedDict

from config.config import PROJECT_DIR
from inputoutput.input import get_tweets, get_articles

tweet_df_filename = os.path.join(PROJECT_DIR, 'df_tweet_t.json')
tweet_idf_json_filename = os.path.join(PROJECT_DIR, 'idf_tweet.json')
tweet_idf_csv_filename = os.path.join(PROJECT_DIR, 'idf_tweet.csv')

df_article_filename = os.path.join(PROJECT_DIR, 'df_article.json')
article_idf_json_filename = os.path.join(PROJECT_DIR, 'idf_article.json')
article_idf_csv_filename = os.path.join(PROJECT_DIR, 'idf_article.csv')


def write_idf_articles():
    articles = get_articles()
    write_tf_idf(articles, df_article_filename, article_idf_json_filename, article_idf_csv_filename)


def write_idf_tweets():
    tweets = get_tweets()
    write_tf_idf(tweets, tweet_df_filename, tweet_idf_json_filename, tweet_idf_csv_filename)


def write_tf_idf(documents, df_filename=None, idf_json_filename=None, idf_csv_filename=None, keywords_function_name='get_keywords'):
    df = get_df(documents, keywords_function_name)

    if df_filename is not None:
        # Print df
        sorted_df = OrderedDict(sorted(df.items()))
        json.dump(sorted_df, open(df_filename, '+w'), indent=1)

    idf = get_idf(df, documents)
    if idf_json_filename is not None:
        # Print idf
        json.dump(idf, open(idf_json_filename, '+w'), indent=1)

    if idf_csv_filename is not None:
        # Print idf to csv
        with open(idf_csv_filename, '+w', encoding='utf8', newline='\n') as fp:
            writer = csv.writer(fp, delimiter=';')
            writer.writerow(['term', 'idf_t'])
            for (term, idf_t) in idf.items():
                writer.writerow((term, str(idf_t).replace('.', ','),))


def get_idf(df, documents):
    idf = {term: math.log(len(documents) / df_t) for (term, df_t) in df.items()}
    idf = OrderedDict(sorted(idf.items()))
    return idf


def get_df(documents, keywords_function_name='get_keywords'):
    df = {}
    for doc in documents:
        keywords_function = getattr(doc, keywords_function_name)
        keywords = keywords_function()
        if keywords is None:
            print("No keywords found for get_df")
            continue
        for word in set(keywords):
            if word in df:
                df[word] += 1
            else:
                df[word] = 1
    return df


def get_idf_tweets():
    with open(tweet_idf_json_filename, 'r') as fp:
        d = json.load(fp)
    return d


def get_idf_articles():
    with open(article_idf_json_filename, 'r') as fp:
        d = json.load(fp)
    return d
