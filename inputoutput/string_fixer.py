import ast
from datetime import datetime

ARRAY = set()
ARRAY.add('author_ids')
INT = set()
#INT.add('keyword_length')
BOOLEAN = set()
BOOLEAN.add('ends_dots')
DATE_SIMPLE = set()
DATE_SIMPLE.add('published_date')
DATETIME_SIMPLE = set()

ARRAY.add('mentions'), ARRAY.add('hashtags'), ARRAY.add('keywords'), ARRAY.add('media'), ARRAY.add('quotations'), ARRAY.add('symbols'), ARRAY.add('urls'), ARRAY.add('currencies'),
INT.add('keyword_length'), INT.add('n_abbriviations'), INT.add('n_html_entities'), INT.add('n_punctuations'), INT.add('n_quationmarks'), INT.add('n_unicode'), INT.add('newline_count')
BOOLEAN.add('ends_dots'), BOOLEAN.add('questionmark'), BOOLEAN.add('rt')


def fix_types(d):
    # Dummy iterable to go through the set
    dummy_iterable = dict(d)
    for (key, value) in dummy_iterable.items():
        if key in ARRAY:  # Check if supposed to be a string
            # new_list = re.sub("\[|\]|,|'", '', value)
            # new_array = new_list.split(' ')
            d[key] = ast.literal_eval(value)
        elif key in INT:  # Check if supposed to be an integer
            d[key] = int(value)
        elif key in BOOLEAN:  # Check if supposed to be a boolean
            d[key] = bool(value)
        elif key in DATETIME_SIMPLE:
            d[key] = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        elif key in DATE_SIMPLE:
            d[key] = datetime.strptime(value, '%Y-%m-%d')
        else:  # Just string
            d[key] = value
