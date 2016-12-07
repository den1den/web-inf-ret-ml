import ast

import datetime

from inputoutput.string_fixer import fix_types
from models.generics import HasKeywords


class Article(dict, HasKeywords):
    def __init__(self, iterable=None, **kwargs):
        super().__init__(iterable, **kwargs)
        if 'id' not in self:
            raise ValueError("No id found in article %s" % super(dict, self).__str__())
        self.id = self['id']
        fix_types(self)

    def __str__(self, *args, **kwargs):
       return str(self['title'])

    def get_keywords(self):
        return self['description'].split(' ') if 'description' in self else None
