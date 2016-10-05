import json

from extract_tweets.models import Tweet


def convert_tweet(filename):
    with open(filename, encoding='utf8') as data_file:
        plain_objects = json.load(data_file)  # Depr: object_hook=lambda d: Tweet(**d)
        return [Tweet(plain_object) for plain_object in plain_objects]


tweets = convert_tweet('xaa.valid.json')

[print("<>" + str(tweets[i]) + "</>") or print() for i in range(0, 9)]
