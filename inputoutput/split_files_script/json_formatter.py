import json
import os

from config.config import TWEETS_HOMEDIR

es = []
for dp, dn, fn in os.walk(TWEETS_HOMEDIR + 'Tweet'):
    for tweet_filename in fn:
        filename = os.path.join(dp, tweet_filename)
        dirname = os.path.basename(os.path.dirname(filename))
        if dirname == 'elections-29-09-raw' or dirname == 'elections-28-09-raw':
            continue
        with open(filename) as rf:
            try:
                data = json.load(rf)
                print("Read in OK: " + filename)
            except Exception as e:
                print("ERROR in " + filename)
                raise e

print("Exceptions:")
print(es)

# with open(TWEETS_HOMEDIR + '' + 'elections.json') as rf:
#     data = json.load(rf)
# print("Read in OK")

# with open('elections-out.json', 'w') as wf:
#    json.dump(data[0:100], wf, indent=2)
