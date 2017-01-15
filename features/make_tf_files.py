import json
import os

from config.config import PROJECT_DIR
from features.term_frequency import write_tf_idf
from inputoutput.getters import get_tweets

idf_dir = PROJECT_DIR

def maketf_idf_file(m, d10s):
    tweet_idf_json_filename = os.path.join(idf_dir, 'idf_tweet_PD_%d_%s.json' % (m, d10s))
    tweet_idf_csv_filename = os.path.join(idf_dir, 'idf_tweet_PD_%d_%s.csv' % (m, d10s))
    tweets = get_tweets(filename_prefix='tweets_2016_%d_%s' % (m, d10s))
    write_tf_idf(tweets, tweet_idf_json_filename, tweet_idf_csv_filename)
    print("\nDone with %d %s\n" % (m, d10s))


for m in [11, 10]:
    for d10 in [0, 1, 2, 3]:
        if d10 == 0 and m == 11:
            for d10s in ['09', '01', '02', '03', '04', '05', '06', '07', '08']:
                maketf_idf_file(m, d10s)
        else:
            d10s = '%d' % d10
            maketf_idf_file(m, d10s)


# get idf values
idf = {}
for f in os.listdir(idf_dir):
    if f.startswith('idf_tweet_PD') and f.endswith('.json') and f != 'idf_tweet_PD_ALL.json':
        with open(os.path.join(idf_dir, f)) as fp:
            idf.update(json.load(fp))

output = os.path.join(idf_dir, 'idf_tweet_PD_ALL.json')
json.dump(idf, open(output, 'w+'), indent=1)
print("Idf written to %s" % output)