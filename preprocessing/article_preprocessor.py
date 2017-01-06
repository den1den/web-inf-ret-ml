import os
import datetime
from urllib.parse import urlparse

import re

from inputoutput.readers import InputReader
from inputoutput.writers import Writer
from preprocessing.preprocess_util import re_whitespace, re_html, re_unicode_decimal, MultiProcessor, replace_in_string, \
    remove_unicode, remove_unprintable, replace_whitespaces, replace_html_entities, re_quotations, \
    re_quotations_somewhere, re_quotations_somewhere_single, re_quotations_somewhere_slashes, re_url_wp_date, \
    re_url_stripes, re_url_stripes_no_id


def get_new_id(generator: str, seen_ids: set, prefix=''):
    """"Generate a new unique id"""
    while True:
        i = abs(hash(generator))
        id = prefix + str(i)
        if id not in seen_ids:
            break
    # while id in seen:
    #     i += 1
    #     id = prefix + str(i)
    return id


class ArticlePreprocessor(MultiProcessor):
    def __init__(self, reader: InputReader, writer: Writer, user_writer, seen_ids=set(), seen_urls=set(), seen_authors: dict = None):
        super().__init__(reader, (writer, user_writer))
        if seen_authors is None:
            seen_authors = dict()
        self.seen_urls = seen_urls  # set: url
        self.seen_ids = seen_ids
        self.authors = seen_authors  # dict: Name -> author

    ARTICLE_COLUMNS = ('id', 'author_ids', 'description', 'html', 'published_date', 'title', 'link', 'domain',)

    def process(self, raw_data):
        # title
        title = raw_data['Title']

        # check if duplicate
        url_str = raw_data['Link']
        unqique_str = url_str
        if unqique_str in self.seen_urls:
            print("Info: article already seen, skipping %s:%d" % (self.reader.current_file, self.reader.i))
            return
        self.seen_urls.add(unqique_str)

        # id, based on unqiueness of url
        article_id = get_new_id(url_str, self.seen_ids, 'r')

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

        self.processed_obj(0, {
            'id': article_id,
            'author_ids': author_ids,
            'description': description,
            'html': is_html,
            'published_date': published_date,
            'title': title,
            'link': link,
            'domain': domain
        })

    AUTHOR_COLUMNS = ('id', 'name',)

    def parse_authors(self, raw_data = None, authors = None):
        if authors is None:
            if raw_data is None:
                Exception('Not the right input in parse_authors')
            else:
                authors = raw_data['Author']

        if authors == '':
            return []
        author_ids = []

        if ', ' in authors:
            for author_name in authors.split(', '):
                author_ids.append(self.process_author_str(author_name))
        if ' and ' in authors.lower():
            for author_name in authors.lower().split(' and '):
                author_ids.append(self.process_author_str(author_name))
        return author_ids


    def process_author_str(self, author_name):
        if author_name == '':
            raise ValueError()

        author_name = author_name.lower()

        if author_name in self.authors:
            # already found author before
            return self.authors[author_name]
        else:
            # new author
            author_id = get_new_id(author_name, self.authors.keys(), 'a')
            author = {
                'id': author_id,
                'name': author_name
            }
            self.processed_obj(1, author)
            self.authors[author_name] = author
            return author


class ArticlePreprocessorSander(ArticlePreprocessor):
    origin_re = re.compile(r'^\d+_([a-z_]+)_\d+.json$')

    def __init__(self, reader: InputReader, writer: Writer, user_writer, seen_ids=set(), seen_urls=set(),
                 seen_authors: dict = None):
        super().__init__(reader, writer, user_writer, seen_ids, seen_urls, seen_authors)

    def process(self, raw_data):
        filename = os.path.basename(self.reader.current_file)

        origin = ArticlePreprocessorSander.origin_re.fullmatch(filename)

        if origin is None:
            print("Could not parse origin from filename %s" % filename)
            return
        origin = origin.group(1)

        url = urlparse(raw_data['url'])
        link_str = str(url.geturl())
        domain = str(url.hostname)
        if domain.startswith('www.'):
            domain = domain[4:len(domain)]
        if domain.endswith('.com'):
            domain = domain[0:len(domain) - 4]
        # check if duplicate
        if link_str in self.seen_urls:
            print("Info: article already seen, skipping %s:%d" % (self.reader.current_file, self.reader.i))
            return
        self.seen_urls.add(link_str)


        re_title_prepostfix = re.compile(r'\n|\r|{|}|:|\(|\)|;')
        raw_article = raw_data['article']
        if raw_article == "":
            print('Empty article')
            return

        #title & author
        if origin == 'huffpost':
            return
            # Title
            title_loc1 = raw_article.find("window.HP.modules.smarten.selector('.js-nav-sticky')")
            title_loc2 = raw_article.find("\"pageName\"")
            if title_loc1 != -1:
                raw_title = raw_article[title_loc1 - 130: title_loc1]
                title = re_title_prepostfix.sub('', raw_title)
            elif title_loc2 != -1:
                raw_title = raw_article[title_loc2 + 11 : title_loc2 + 100]
                match = re.match(re_quotations_somewhere, raw_title)
                if match:
                    title = match.group(1)
                else:
                    print('No match for title')
                    match = None
            else:
                print('Title not found in %s with link %s' % (filename, link_str))
                return

            # Author
            author_loc = raw_article.find("    author:")
            raw_author = raw_article[author_loc + 7:  author_loc + 100]
            match = re.match(re_quotations_somewhere, raw_author)
            if match:
                authors = match.group(1)
            else:
                authors = None
                return

        elif origin == 'la_times':

            #Title
            title_loc1 = raw_article.find("pageTitle")
            if title_loc1 != -1:
                raw_title = raw_article[title_loc1 + 9: title_loc1 + 209]
                match = re.match(re_quotations_somewhere_single, raw_title)
                if match:
                    title = match.group(1)
                else:
                    print('No match for title')
                    title = "Unknown Title"
            else:
                print('No title found')
                title = "Unknown Title"

            # Author
            author_loc1 = raw_article.find("page.author")
            if author_loc1 != -1:
                raw_author = raw_article[author_loc1 + 11: author_loc1 + 100]
                match = re.match(re_quotations_somewhere_single, raw_author)
                if match:
                    authors = match.group(1)
                else:
                    print('No match for author')
                    authors = "Unknown Author"
            else:
                print('No author found')
                authors = "Unknown Author"

        elif origin == 'wash_post':
            #Title
            match = re.match(re_url_wp_date, link_str)
            if match:
                raw_title = match.group(1)
                title = raw_title.replace('-', ' ')
            else:
                match = re.search(re_url_stripes, link_str)
                if match:
                    raw_title = match.group(1)
                    title = raw_title.replace('-', ' ')
                else:
                    print('No match for title')
                    title = "Unknown Title"

            #Author
            author_loc = raw_article.find('By')
            first_words = raw_article[author_loc + 3:author_loc + 200].split(' ')
            for i in range(len(first_words)):
                if first_words[i] in ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                                      'August', 'September', 'October', 'November', 'December']:
                    authors = ' '.join(first_words[0:i])
                    break
                if i == len(first_words):
                    authors = 'Unknown Author'

        elif origin == 'wash_times':
            #Title
            match = re.search(re_url_stripes, link_str)
            if match:
                raw_title = match.group(1)
                title = raw_title.replace('-', ' ')
            else:
                print('No match for title')
                title = "Unknown Title"

            #Author
            authors = "Unknown Author"

        elif origin == 'wsj':
            #Title
            match = re.search(re_url_stripes_no_id, link_str)
            if match:
                raw_title = match.group(1)
                title = raw_title.replace('-', ' ')
            else:
                match = re.search(re_url_stripes, link_str)
                if match:
                    raw_title = match.group(1)
                    title = raw_title.replace('-', ' ')
                else:
                    print('No match for title')
                    title = "Unknown Title"

            #Author
            authors = "Unknown Author"
        else:
            raise Exception("Origin %s not known" % origin)

        timestamp = raw_data['date']

        # id, based on unqiueness of url
        article_id = get_new_id(link_str, self.seen_ids, 'r')

        # published_date
        try:
            date_str = filename[:8]
            published_date = datetime.date(int(date_str[:4]), month=int(date_str[5:6]), day=int(date_str[7:8]))
        except ValueError as e:
            print("Could not parse date from filename %s" % filename)
            raise e

        # link
        url = urlparse(link_str)
        link = url.geturl()
        domain = str(url.hostname)
        if domain.startswith('www.'):
            domain = domain[4:len(domain)]
        if domain.endswith('.com'):
            domain = domain[0:len(domain) - 4]

        # author
        author_ids = self.parse_authors(authors=authors)

        # description
        description = 'No description'
        is_html = 'True'

        self.processed_obj(0, {
            'id': article_id,
            'author_ids': author_ids,
            'description': description,
            'html': is_html,
            'published_date': published_date,
            'title': title,
            'link': link,
            'domain': origin
        })
