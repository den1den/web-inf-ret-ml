import json
from argparse import Namespace


def convert_tweet(filename):
    with open(filename, encoding='utf8') as data_file:
        return json.load(data_file, object_hook=lambda d: Namespace(**d))

tweets = convert_tweet('xaa.valid.json')

[print("<>" + str(tweets[i]) + "</>") or print() for i in range(0, 9)]