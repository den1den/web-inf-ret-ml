import ast

import datetime

from nltk.corpus import stopwords
stopwords = set(stopwords.words('english'))

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

    def get_preproc_keywords(self):
        return self.filter_stopwords(dirty_normalizer(self['description']))

    def get_preproc_title(self):
        return self.filter_stopwords(dirty_normalizer(self['title']))

    def filter_stopwords(self, normalized_text):
        from preprocessing.preprocess_util import re_whitespace
        return [word for word in re_whitespace.split(normalized_text) if word not in stopwords]


def dirty_normalizer(raw_text):
    from preprocessing.preprocess_util import re_whitespace, remove_by_indices, replace_in_string, \
        replace_abbreviations, \
        remove_strings, remove_unicode, drop_punctuation, remove_unprintable, replace_whitespaces
    #
    # text normalization
    #
    normalized_text = raw_text  # as much normalized
    from preprocessing.preprocess_util import replace_html_entities
    normalized_text, _, n_html_entities = replace_in_string(normalized_text, replace_html_entities)
    # see if text ends with dots
    ends_dots = False
    normalized_text = normalized_text.strip()
    if normalized_text.endswith('…'):
        normalized_text = normalized_text[:-1]
        ends_dots = True
    elif normalized_text.endswith('...'):
        normalized_text = normalized_text[:-3]
        ends_dots = True
    if ends_dots:
        if normalized_text.endswith(' '):
            # Text of the form: 'words end here ...'
            pass
        else:
            # Text of the form: 'words may not end her...'
            if len(normalized_text) < 25:
                # print(" note: not skipping last word in: %s" % raw_text.replace('\n', ''))
                pass  # probably not cut off
            else:
                # print(" note: skipping last word in: %s" % raw_text.replace('\n', ''))
                # FIXME: goes wrong
                normalized_text = normalized_text.rsplit(' ', 1)[0]
    # lowercase
    normalized_text = normalized_text.lower()
    # replace abbreviations
    normalized_text, _, n_abbriviations = replace_in_string(normalized_text, replace_abbreviations)
    # remove quotation marks
    normalized_text, _, n_quationmarks = remove_strings(normalized_text, ("'",))
    # remove unicode
    normalized_text, n_unicode = remove_unicode(normalized_text)
    # remove special chars
    normalized_text, _, n_punctuations = remove_strings(normalized_text, drop_punctuation)
    # remove unprintable charcters
    normalized_text, n_unprintable = remove_unprintable(normalized_text)
    # replace whitespaces
    normalized_text = replace_whitespaces(normalized_text)
    return normalized_text
