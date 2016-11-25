import re

from models.generics import HasKeywords


class Tweet(dict, HasKeywords):
    def __init__(self, iterable=None, **kwargs):
        super().__init__(iterable, **kwargs)
        self.id = int(self['id'][1:])

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
        return self['keywords_text'] if 'keywords_text' in self else None
