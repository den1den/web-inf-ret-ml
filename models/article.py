class Article(dict):
    def __init__(self, iterable=None, **kwargs):
        super().__init__(iterable, **kwargs)

    def __str__(self, *args, **kwargs):
       return str(self['title'])

    def get_keywords(self):
        return self['keywords_title'] if 'keywords_title' in self else None
