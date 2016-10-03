import json
from argparse import Namespace


def convert_tweet(filename):
    with open(filename, encoding='utf8') as data_file:
        return json.load(data_file, object_hook=lambda d: Namespace(**d))
