class Tweet(dict):
    def __init__(self, iterable=None, **kwargs):
        super().__init__(iterable, **kwargs)

    def __str__(self, *args, **kwargs):
        return self['text']

    def get_hashtags(self):
        return [h['text'] for h in self['entities']['hashtags']]
