from datetime import datetime
from urllib.parse import urlparse

from inputoutput.input import InputReader, Writer
from preprocessing.preprocess_util import  re_whitespace, re_html, re_unicode_decimal, MultiProcessor, replace_in_string, \
    remove_unicode, remove_unprintable, replace_whitespaces, replace_html_entities


def get_new_id(generator, seen, prefix=''):
    i = abs(hash(generator))
    id = prefix + str(i)
    while id in seen:
        i += 1
        id = 't' + str(i)
    return id


class ArticlePreprocessor(MultiProcessor):
    def __init__(self, reader: InputReader, writer: Writer, user_writer, seen_ids=set(), seen_urls_titles=set(),
                 seen_authors: dict = None):
        super().__init__(reader, (writer, user_writer))
        if seen_authors is None:
            seen_authors = dict()
        self.seen_urls_titles = seen_urls_titles  # set: url + '' + title
        self.seen_ids = seen_ids
        self.authors = seen_authors  # dict: Name -> author

    ARTICLE_COLUMNS = ('id', 'author_ids', 'description', 'html', 'published_date', 'title', 'link', 'domain',)

    def process_obj(self, raw_data):
        # title
        title = raw_data['Title']

        # id, based on unqiueness of url
        id = get_new_id(raw_data['Link'], self.seen_ids, 'r')
        url_str = raw_data['Link']
        unqique_str = url_str + '' + title
        if unqique_str in self.seen_urls_titles:
            print("Info: skipping article %s:%d" % (self.reader.current_file, self.reader.i))
        self.seen_urls_titles.add(unqique_str)
        self.seen_ids.add(id)

        # published_date
        try:
            published_date_str = raw_data['Publish date'].replace('CET', '')
            published_date_str = published_date_str.replace('CEST', '')
            published_date = datetime.strptime(published_date_str, '%a %b %d %H:%M:%S  %Y')
        except ValueError as e:
            print("Could not parse date %s" % raw_data['Publish date'])
            raise e

        # link
        url = urlparse(url_str)
        link = url.geturl()
        domain = str(url.hostname)
        if domain.startswith('www.'):
            domain = domain[4:len(domain)]
        if domain.endswith('.com'):
            domain = domain[0:len(domain) - 4]

        # author
        author_ids = self.parse_authors(raw_data)

        # description
        raw_description = raw_data['Description']
        description = replace_in_string(raw_description, replace_html_entities)[0]
        # remove unicode
        description = remove_unicode(description)[0]
        # remove unprintable charcters
        description = remove_unprintable(description)[0]
        # html
        is_html = re_html.search(raw_description) is not None
        if is_html:
            finditer = re_unicode_decimal.finditer(description)
            offset = 0
            for m in finditer:
                unicode = (m.group(1) or m.group(2))
                description = str(description[0:m.start() + offset] + description[m.end() + offset:len(description)])
                offset -= (m.end() - m.start())
            assert re_unicode_decimal.search(description) is None
            description = re_html.sub(' ', description)
        # replace whitespaces
        description = replace_whitespaces(description)

        return {
            'id': id,
            'author_ids': author_ids,
            'description': description,
            'html': is_html,
            'published_date': published_date,
            'title': title,
            'link': link,
            'domain': domain
        }

    AUTHOR_COLUMNS = ('id', 'name',)

    def parse_authors(self, raw_data):
        if raw_data['Author'] == '':
            return []
        author_ids = []
        for author_name in raw_data['Author'].split(', '):
            if author_name == '':
                raise ValueError()
            if author_name in self.authors:
                # already found author before
                author = self.authors[author_name]
            else:
                # new author
                author_id = get_new_id(author_name, self.authors.keys(), 'a')
                author = {
                    'id': author_id,
                    'name': author_name
                }
                self.processed_obj(0, author)
                self.authors[author_name] = author
            author_ids.append(author['id'])
        return author_ids