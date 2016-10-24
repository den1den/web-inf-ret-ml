class Article(dict):
    def __init__(self, iterable=None, **kwargs):
        super().__init__(iterable, **kwargs)

    def __str__(self, *args, **kwargs):
       return str(self['Title'])

    def get_keywords(self):
        return self['keywords_Title'] if 'keywords_Title' in self else None