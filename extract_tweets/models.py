import re


class Tweet(dict):
    def __init__(self, iterable=None, **kwargs):
        super().__init__(iterable, **kwargs)
        self.id = self['id']

    def __str__(self, *args, **kwargs):
       return self['text']

    def __hash__(self, *args, **kwargs):
        # Hashlookups can be fatser if: return self.id
        return super().__hash__(*args, **kwargs)

    def __eq__(self, *args, **kwargs):
        # equals can be faster?
        return super().__eq__(*args, **kwargs)

    def get_txt(self):
        return self['fulltext'] if 'fulltext' in self else self['text']

    def get_hashtags(self):
        return [h['text'] for h in self['entities']['hashtags']]

    def get_retweet_id(self):
        if "retweeted_status" not in self:
            return None
        return self["retweeted_status"]['id'] or None

    def get_words(self):
        return [word.lower() for word in re.split('\s+', self.get_txt())]
