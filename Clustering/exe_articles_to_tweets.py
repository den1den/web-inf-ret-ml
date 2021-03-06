import json

import nltk.sentiment.util
import os
import random
from _operator import itemgetter
from datetime import timedelta
from nltk.sentiment import SentimentIntensityAnalyzer
from Clustering.clustering import find_tweets_with_keywords_idf
from config.config import PROJECT_DIR, PCLOUD_DIR
from inputoutput.cli import query_yes_no
from inputoutput.getters import get_articles, update_tweets_cache, get_articles_by_date

# output
article_clusters = {}  # article_id -> tweet_id
article_clusters_filepath = os.path.join(PROJECT_DIR, 'article_clusters_PD_after_2016_11_07.json')

# the idf baseline to use
idf_file = os.path.join(PCLOUD_DIR, 'idf', 'idf_tweet_PD_ALL.json')

# treshold to make sure only words that are unique are searched for
TRESHOLD = 15

def exe(article_clusters, article_clusters_filepath, TRESHOLD):
    tweets_cache = {}

    # if os.path.exists(article_clusters_filepath):
    #     if not query_yes_no("Are you sure you want to overwrite %s" % article_clusters_filepath, default='no'):
    #         exit()

    # get idf values
    with open(idf_file) as fp:
        idf = json.load(fp)

    # For all articles after 2016_11_06
    articles = []
    for m in [11, 12]:
        if m == 11:
            for d in range(7, 32):
                articles += get_articles_by_date(filename_prefix='articles_2016_%d_%02d' % (m, d))
        else:
            for d in range(1, 32):
                articles += get_articles_by_date(filename_prefix='articles_2016_%d_%02d' % (m, d))
    articles += get_articles_by_date(filename_prefix='articles_2017')

    i = 1
    last_start_date = None

    for a in articles:
        try:
            if a.id[0] != 'r':
                raise Exception("Non article is get_articles! %s" % a)
            kwds = a.get_preproc_title()
            if a.get_date() != last_start_date:
                last_start_date = a.get_date()
                update_tweets_cache(last_start_date - timedelta(days=0), last_start_date + timedelta(days=10), tweets_cache)

            all_tweets = []
            for tweets in tweets_cache.values():
                all_tweets += tweets
            ts = find_tweets_with_keywords_idf(all_tweets, kwds, idf, TRESHOLD)
            if len(ts) > 0:
                ts.sort(reverse=True, key=itemgetter(0))
                article_clusters[a.id] = process_cluster(a, ts)
                i += 1
            else:
                # Do not add to output
                pass
        except Exception as err:
            try:
                print("Writing to %s" % article_clusters_filepath)
                json.dump(article_clusters, open(article_clusters_filepath, 'w+', encoding='utf-8'), indent=1)
            except Exception as e:
                print(article_clusters)
                raise e
            print("Error: Could not cluster with article %s\n%s" % (a, err))
        if i % 200 == 0:
            print("Writing to %s" % article_clusters_filepath)
            json.dump(article_clusters, open(article_clusters_filepath, 'w+', encoding='utf-8'), indent=1)

    print("Writing to %s" % article_clusters_filepath)
    json.dump(article_clusters, open(article_clusters_filepath, 'w+', encoding='utf-8'), indent=1)

vader_analyzer = SentimentIntensityAnalyzer()
####
#### DO THIS
####
def process_cluster(article, idf_and_tweets):
    article_max_hit = idf_and_tweets[0][0]
    rumor_value = 0

    tweets_output = []

    for idf, tweet in idf_and_tweets:

        quotation_marks = int(tweet['n_quationmarks']) / len(tweet['keywords']) * 0.5
        abbreviations = - int( tweet['n_abbriviations']) / len(tweet['keywords']) * 1
        question_marks = - (0.5 if tweet['questionmark'] else 0)
        media = -len(tweet['media']) * 0.3
        source = 0.2 if tweet['source_type'] == 'web_client' else -0.1

        polarity_scores = vader_analyzer.polarity_scores(tweet['full_text'])
        sentiment = polarity_scores['neu'] - 0.5

        tweet_rumor_value = quotation_marks + abbreviations + question_marks + media + source + sentiment
        tweet_output = {
            'id': tweet.id_str(),
            'idf_sum': idf,
            'quotation_marks': quotation_marks,
            'abbreviations': abbreviations,
            'question_marks': question_marks,
            'media': media,
            'source': source,
            'sentiment': sentiment,
            'tweet_rumor_value': tweet_rumor_value,
        }
        # print("tweets_output:\n%s\n%s\n" % (tweet, tweet_output))
        rumor_value += tweet_rumor_value

        tweets_output.append(tweet_output)

    rumor_value /= len(idf_and_tweets)

    return {
        'article_max_hit': article_max_hit,
        'rumor_value': rumor_value,
        'tweets': tweets_output,
    }


if __name__ == '__main__':
    exe(article_clusters, article_clusters_filepath, TRESHOLD)
