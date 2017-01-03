import json
import os
from _operator import itemgetter
from datetime import timedelta

from Clustering.clustering import find_tweets_with_keywords_idf
from config.config import PROJECT_DIR
from inputoutput.cli import query_yes_no
from inputoutput.getters import get_articles, get_tweets_by_date, update_tweets_cache

# output
article_clusters = {}  # article_id -> tweet_id
article_clusters_filepath = os.path.join(PROJECT_DIR, 'article_clusters.json')

# the idf baseline to use
idf_files = [os.path.join(PROJECT_DIR, 'idf_tweet_600000_0.json'), os.path.join(PROJECT_DIR, 'idf_tweet_577244_1.json')]

# treshold to make sure only words that are unique are searched for
TRESHOLD = 15

def exe(article_clusters, article_clusters_filepath, TRESHOLD):
    tweets_cache = {}

    if os.path.exists(article_clusters_filepath):
        if not query_yes_no("Are you sure you want to overwrite %s" % article_clusters_filepath, default='no'):
            exit()

    # get idf values
    idf = {}
    for idf_file in idf_files:
        with open(idf_file) as fp:
            idf.update(json.load(fp))

    # For all articles
    articles = get_articles()
    i = 0
    last_start_date = None
    tweets = None
    for a in articles:
        try:
            kwds = a.get_preproc_title()
            if a.get_date() != last_start_date:
                last_start_date = a.get_date()
                update_tweets_cache(last_start_date - timedelta(days=1), last_start_date + timedelta(days=10), tweets_cache)

            all_tweets = []
            for tweets in tweets_cache.values():
                all_tweets += tweets
            ts = find_tweets_with_keywords_idf(all_tweets, kwds, idf, TRESHOLD)
            ts.sort(reverse=True, key=itemgetter(0))
            if len(ts) > 0:
                article_max_hit = ts[0][0]
                article_clusters[a.id] = {
                    'article_max_hit': article_max_hit,
                    'tweets': [tweet.id_str() for (idf_sum, tweet) in ts],
                }
            else:
                print("No hit on %s" % a)
                article_clusters[a.id] = {
                    'article_max_hit': 0,
                    'tweets': [],
                }
        except Exception as err:
            try:
                print("Writing to %s" % article_clusters_filepath)
                json.dump(article_clusters, open(article_clusters_filepath, 'w+', encoding='utf-8'), indent=1)
            except Exception as e:
                print(article_clusters)
                raise e
            print("Error: Could not cluster with article %s\n%s" % (a, err))
        i += 1
        if i % 20 == 0:
            print("Writing to %s" % article_clusters_filepath)
            json.dump(article_clusters, open(article_clusters_filepath, 'w+', encoding='utf-8'), indent=1)

    print("Writing to %s" % article_clusters_filepath)
    json.dump(article_clusters, open(article_clusters_filepath, 'w+', encoding='utf-8'), indent=1)

if __name__ == '__main__':
    exe(article_clusters, article_clusters_filepath, TRESHOLD)
