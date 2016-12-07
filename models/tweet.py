import ast

import re

from models.generics import HasKeywords

ARRAY = set()
ARRAY.add('mentions'), ARRAY.add('hashtags'), ARRAY.add('keywords'), ARRAY.add('media'), ARRAY.add('quotations'), ARRAY.add('symbols'), ARRAY.add('urls'), ARRAY.add('currencies'),
INT = set()
INT.add('keyword_length'), INT.add('n_abbriviations'), INT.add('n_html_entities'), INT.add('n_punctuations'), INT.add('n_quationmarks'), INT.add('n_unicode'), INT.add('newline_count')
BOOLEAN = set()
BOOLEAN.add('ends_dots'), BOOLEAN.add('questionmark'), BOOLEAN.add('rt')


class Tweet(dict, HasKeywords):
    def __init__(self, iterable=None, **kwargs):
        super().__init__(iterable, **kwargs)
        self.id = int(self['id'][1:])
        self.fix_types()

    def fix_types(self):
        # Dummy iterable to go through the set
        dummy_iterable = dict(self)
        for (key, value) in dummy_iterable.items():
            if key in ARRAY:  # Check if supposed to be a string
                # new_list = re.sub("\[|\]|,|'", '', value)
                # new_array = new_list.split(' ')
                self[key] = ast.literal_eval(value)
            elif key in INT:  # Check if supposed to be an integer
                self[key] = int(value)
            elif key in BOOLEAN:  # Check if supposed to be a boolean
                self[key] = bool(value)
            else:  # Just string
                self[key] = value

    def __str__(self, *args, **kwargs):
       return self['text']

    def __hash__(self, *args, **kwargs):
        # Hashlookups can be fatser if: return self.id
        return super().__hash__(*args, **kwargs)

    def __eq__(self, *args, **kwargs):
        # equals can be faster?
        return super().__eq__(*args, **kwargs)

    def get_small_txt(self):
        return re.sub('\s+', ' ', self.get_txt())

    def get_txt(self):
        return self['fulltext'] if 'fulltext' in self else self['text']

    def get_real_text(self):
        return self['real_text'] if 'real_text' in self else self['text']

    def get_hashtags(self):
        return [h['text'] for h in self['entities']['hashtags']]

    def get_retweet_id(self):
        if "retweet_id" not in self:
            return None
        return self["retweet_id"] or None

    def get_words(self):
        return [word.lower() for word in re.split('\s+', self.get_txt())]

    def get_keywords(self):
        return self['keywords'] if 'keywords' in self else None
