import json
import os
from _operator import itemgetter
from datetime import timedelta

from Clustering.clustering import find_tweets_with_keywords_idf
from config.config import PROJECT_DIR
from inputoutput.getters import get_articles, get_tweets_by_date

articles = get_articles()

with open(os.path.join(PROJECT_DIR, 'idf_tweet_600000_0.json')) as fp:
    idf = json.load(fp)

output_articles = []

i = 0
for a in articles:
    kwds = a.get_preproc_title()
    if 'ayotte' in kwds:

        start_date = a.get_date()
        tweets = get_tweets_by_date(start_date - timedelta(days=1), start_date + timedelta(days=10))
        ts = find_tweets_with_keywords_idf(tweets, kwds, idf, 15)
        ts.sort(reverse=True, key=itemgetter(0))
        if len(ts) > 0:
            article_max_hit = ts[0][0]
            output_articles.append((article_max_hit, a, ts))
        else:
            print("No hit on %s" % a)
        i += 1
        break

output_articles.sort(key=itemgetter(0))
for article_max_hit, a, ts in output_articles[:]:
    print("\nArticle\n%s\n  %s" % (a, a.get_preproc_title()))
    for result_idf, result_tweet in ts[:10]:
        print("%s: %s\n  %s" % (result_idf, result_tweet, result_tweet.get_keywords()))
    if len(ts) > 10:
        print('...')
