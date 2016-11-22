from models.generics import HasKeywords


class Article(dict, HasKeywords):
    def __init__(self, iterable=None, **kwargs):
        super().__init__(iterable, **kwargs)
        if 'id' not in self:
            raise ValueError("No id found in article %s" % super(dict, self).__str__())
        self.id = int(self['id'])

    def __str__(self, *args, **kwargs):
       return str(self['title'])

    def get_keywords(self):
        return self['keywords_title'] if 'keywords_title' in self else None
