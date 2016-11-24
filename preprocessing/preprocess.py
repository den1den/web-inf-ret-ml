import os
import re
import string
import unicodedata
from abc import abstractmethod
from datetime import datetime
from operator import itemgetter
from urllib.parse import urlparse

from nltk.corpus import stopwords

from config import config
from inputoutput.input import Writer, InputReader, CSVWriter
from preprocessing.spell_checker import known_correct

re_whitespace = re.compile('\s+')
re_html = re.compile(r'<[^>]+>')
re_unicode_decimal = re.compile(r'&#(\d{2,4});|&([a-z]+);')
re_unicode = re.compile(r'[^\x00-\x7f]')
re_html_a_tag = re.compile(r'<a href="([^"]+)"[^>]*>(.+)</a>', flags=re.IGNORECASE)
re_next_word = re.compile(r'\s*(\w+)(…|[.][.][.])?')
re_non_alpha = re.compile(r'\W+')
CURRENCY_PATTERN = r'[$€](\d+(?:[,]\d+)*(?:[.]\d+)?)'
re_currency = re.compile(r'(?:^|\s+)' + CURRENCY_PATTERN + r'(?:$|\s+)')
re_currency = re.compile(CURRENCY_PATTERN)
re_quotations = re.compile(r'"\s*([^"]+)[.]?\s*"')

REPORT_DUPLICATE = False


def re_currency_matches(string):
    amounts = []
    factor = 1
    prev_word = None
    for m in re_currency.finditer(string):
        amount = ''.join(m.groups(''))
        try:
            amount = float(amount.replace(',', ''))
        except ValueError:
            print("Strange amount found: %s" % amount)
            continue
        next_word_match = re_next_word.search(string, m.end())
        if next_word_match:
            nxt = next_word_match.group(1).lower()
            cutoff = next_word_match.group(2) is not None
            if cutoff:
                pass
            elif nxt == 'k' or nxt == 'g' or nxt == 'grand':
                factor = 1000
            elif nxt == 'm' or nxt == 'mm' or nxt == 'mil' or nxt == 'mill' or nxt == 'milion' or nxt == 'million':
                factor = 1000000
            elif nxt == 'b' or nxt == 'bil' or nxt == 'bill' or nxt == 'bilion' or nxt == 'billion':
                factor = 1000000000
            elif nxt == 't' or nxt == 'tril' or nxt == 'trill' or nxt == 'trilion' or nxt == 'trillion':
                factor = 1000000000000
            elif nxt == 'bn':
                pass

            if prev_word:
                if prev_word.isdigit():
                    amounts[-1] *= factor
            amount *= factor

            prev_word = nxt
        else:
            prev_word = None

        amounts.append(amount)
    return amounts


def re_date_matches(text):
    pass


def remove_by_indices(s, entities):
    """
    remove hashtags, mentions, urls, symbols (stripped_text)
    :param s:
    :param entities: array of dict with 'indices' key
    :return: s - all entities
    """
    index_offset = 0
    strip_indices = []
    for type, enities in entities.items():
        for enitiy in enities:
            strip_indices.append((enitiy['indices'][0], enitiy['indices'][1],))
    strip_indices.sort(key=itemgetter(0))
    for (index_start, index_end) in strip_indices:
        s = s[:index_start - index_offset] + s[index_end - index_offset:]
        index_offset += index_end - index_start
    return s


def replace_in_string(s, replace_pairs):
    """
    :param s:
    :param replace_pairs:
    :return: new string, the difference in characters, number of replacement operations
    """
    n = len(s)
    hits = 0
    for (find, replace) in replace_pairs:
        i = 0
        while True:
            i = s.find(find, i)
            if i == -1:
                break
            s = s[0:i] + replace + s[i + len(find):]
            hits += 1
            if hits > n:
                raise Exception("Livelock")
    return s, n - len(s), hits


def remove_strings(s, remove_substrings):
    """
    :param s:
    :param remove_substrings:
    :return: new string, the difference in characters, number of replacement operations
    """
    n = len(s)
    hits = 0
    for find in remove_substrings:
        i = 0
        while True:
            i = s.find(find, i)
            if i == -1:
                break
            s = s[0:i] + s[i + len(find):]
            hits += 1
    return s, n - len(s), hits


def remove_unicode(s):
    n = len(s)
    s = unicodedata.normalize('NFKD', s)
    s = s.encode('ascii', 'ignore')
    s = s.decode('latin-1')
    n -= len(s)
    return s, n


def replace_whitespaces(s):
    s = s.strip()
    s = re_whitespace.sub(' ', s)
    return s


def remove_unprintable(s):
    n = len(s)
    s = ''.join(filter(lambda x: x in string.printable, s))
    n -= len(s)
    return s, n


def replace_nonalpha_in_string(s, repl=' '):
    return re_non_alpha.sub(repl, s)


class Processor:
    def __init__(self, reader: InputReader, writer: Writer):
        self.reader = reader
        self.writer = writer

    def __call__(self, n=None):
        i = 0
        for data in self.reader:
            try:
                obj = self.process(data)
            except Exception as e:
                print("Warning: could not process %s:%d %s" % (self.reader.current_file, self.reader.i, e))
                print("         data: %s" % data)
                obj = None
            if obj is not None:
                self.writer.write(obj)
                i += 1
                if n is not None and i == n:
                    break
        print("Done processing %d/%d" % (i, self.reader.i))
        self.writer.close()

    @abstractmethod
    def process(self, raw_data):
        return None


class UserProcessor(Processor):
    def __init__(self, reader: InputReader, writer: Writer, user_writer):
        super().__init__(reader, writer)
        self.user_writer = user_writer

    def __call__(self, n=None, n_user=None):
        i = 0
        i_u = 0
        for data in self.reader:
            try:
                obj, user = self.process_with_user(data)
            except Exception as e:
                print("Warning: could not process %s:%d %s" % (self.reader.current_file, self.reader.i, e))
                print("         data: %s" % data)
                if __debug__:
                    try:
                        obj, user = self.process_with_user(data)
                    except Exception:
                        pass
                obj = None
                user = None
            if obj is not None:
                self.writer.write(obj)
                i += 1
                if n is not None and i == n:
                    break
            if user is not None:
                self.user_writer.write(user)
                i_u += 1
                if n_user is not None and i_u == n_user:
                    break
        print("Done processing %d/%d and %d users" % (i, self.reader.i, i_u))
        self.writer.close()
        self.user_writer.close()

    @abstractmethod
    def process_with_user(self, raw_data):
        return None, None


class TweetPreprocessor(UserProcessor):

    def __init__(self, reader: InputReader, writer: Writer, user_writer):
        super().__init__(reader, writer, user_writer)
        self.stopwords = set(stopwords.words('english'))
        self.drop_punctuation = [',', '.', '#', '@', '[', ']', '{', '}', '"', ':', '!', "'", '?', '\\']
        self.replace_html_entities = (
            ('&amp;', 'and'),
            ('&gt;', '>'),
            ('&lt;', '<'),
            ('“', "'"),
            ('”', "'"),
            ('"', "'"),
            (r"\\'", "'"),
            (r"\'", "'"),
            ("`", "'"),
        )
        self.replace_abbreviations = (
            ("ain't", 'are not'),
            ("can't", 'cannot'),
            (" he's", ' he is'),
            (" she's", ' she is'),
            (" we're", ' we are'),
            ("we're", 'we are'),
            (" w/", ' with'),
        )
        self.tweet_skipped = []
        self.tweet_n_unique = 0
        self.tweet_n_duplicate = 0
        self.tweet_texts = {}
        self.tweet_sources = set()
        self.quotations = set()

    def process_with_user(self, raw_data):
        """ process a tweet for feature extraction
        :param raw_data
        :return: preprocessed_data
        """
        if self.should_ignore(raw_data):
            if 'id' in raw_data:
                print("Info: skipping tweet %s %s:%d" % (raw_data['id'], self.reader.current_file, self.reader.i))
            else:
                print("Info: skipping tweet %s:%d" % (self.reader.current_file, self.reader.i))
            return None

        # tweet id
        id = 't' + raw_data['id_str']

        if __debug__:
            # check for duplicate tweets
            if id in self.tweet_texts:
                previously_found_text = self.tweet_texts[id]
                if previously_found_text != raw_data['text']:
                    raise ValueError("Tweet with same ID but different text found")
                else:
                    # skip tweets with same text and id
                    self.tweet_n_duplicate += 1
                    if REPORT_DUPLICATE:
                        print("Warning: duplicate tweet %s found!" % id)
                    return None, None
            else:
                self.tweet_texts[id] = raw_data['text']

        # user_id
        if 'user' not in raw_data:
            user_id = 'unknown'
            user_output = None
        else:
            user_id = 'u' + raw_data['user']['id_str']
            user_output = self.process_user(raw_data)

        # rt
        rt = 'retweeted_status' in raw_data

        # @
        mentions = [str(um['id']) for um in raw_data['entities']['user_mentions']]

        # urls
        urls = [url['expanded_url'] for url in raw_data['entities']['urls']]

        # hashtags
        hashtags = [hashtag['text'] for hashtag in raw_data['entities']['hashtags']]

        # symbols, donted by $
        symbols = [symbols['text'] for symbols in raw_data['entities']['symbols']]

        # media, special urls
        if 'media' in raw_data['entities']:
            media = [{'id': m['id'], 'type': m['type'], 'url': m['url']} for m in raw_data['entities']['media']]
        else:
            media = []

        # source
        source = raw_data['source']
        source_type, source_url = self.process_source(source)

        #
        # text processing
        #
        raw_text = str(raw_data['text'])  # the original
        text = raw_text  # `text` should be as much like the original
        # but without urls
        URL_KEYS = ('urls', 'media')
        text = remove_by_indices(text, {key: raw_data['entities'][key] for key in URL_KEYS if
                                        key in raw_data['entities'].keys()})
        # strip components without information from `text`
        if rt:
            text = text[6 + len(raw_data['entities']['user_mentions'][0]['screen_name']):]
        # replace html characters
        text = replace_in_string(text, self.replace_html_entities)[0]
        # remove unicode
        text = remove_unicode(text)[0]
        # remove unprintable charcters
        text = remove_unprintable(text)[0]
        # replace whitespaces
        text = replace_whitespaces(text)

        #
        # text normalization
        #
        normalized_text = raw_text  # as much normalized
        # remove hashtags, urls, mentions and symbols
        normalized_text = remove_by_indices(normalized_text, raw_data['entities'])
        if rt:
            # strip 'RT : '
            normalized_text = normalized_text[5:]
        normalized_text, _, n_html_entities = replace_in_string(normalized_text, self.replace_html_entities)
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
        normalized_text, _, n_abbriviations = replace_in_string(normalized_text, self.replace_abbreviations)
        # remove quotation marks
        normalized_text, _, n_quationmarks = remove_strings(normalized_text, ("'",))
        # remove unicode
        normalized_text, n_unicode = remove_unicode(normalized_text)
        # remove special chars
        normalized_text, _, n_punctuations = remove_strings(normalized_text, self.drop_punctuation)
        # remove unprintable charcters
        normalized_text, n_unprintable = remove_unprintable(normalized_text)
        # replace whitespaces
        normalized_text = replace_whitespaces(normalized_text)

        # normalize even futher
        normalized_text_2 = normalized_text
        normalized_text_2 = replace_nonalpha_in_string(normalized_text_2, ' ')
        normalized_text_2 = replace_whitespaces(normalized_text_2)

        if config.SPELLING:
            print("Tweet (%d)\n     raw_text: %s\n         text: %s\n   normalized: %s\n normalized 2: %s" % (
                self.reader.i - 1, raw_text.replace('\n', '<NEWLINE>'), text, normalized_text, normalized_text_2))

        #
        # text features
        #

        # newline_count
        newline_count = raw_text.count('\n')

        # questionmark
        questionmark = '?' in text

        # tokenization/keywords
        keywords = [word for word in re_whitespace.split(normalized_text) if word not in self.stopwords]

        # quotes
        quotations = re_quotations.findall(text)
        if len(quotations) > 0:
            new = False
            for quote in quotations:
                if quote not in self.quotations:
                    self.quotations.add(quote)
                    new = True
            if new:
                # print('found %s in %s' % (str(quotations).ljust(60), raw_text.replace('\n', ' ')))
                pass

        from config.config import SPELLING
        if SPELLING:
            # spelling mistakes, based on https://github.com/mattalcock/blog/blob/master/2012/12/5/python-spell-checker.rst
            # TODO: check how to interpet these results
            correct_raw = [known_correct(word) for word in re_whitespace.split(raw_text)]
            correct_txt = [known_correct(word) for word in re_whitespace.split(text)]
            correct_nor = [known_correct(word) for word in re_whitespace.split(normalized_text)]
            print(" error rating: %d/%d, %d/%d, %d/%d" % (
                sum([1 << s for (s, w) in correct_raw]), len(re_whitespace.split(raw_text)),
                sum([1 << s for (s, w) in correct_txt]), len(re_whitespace.split(text)),
                sum([1 << s for (s, w) in correct_nor]), len(re_whitespace.split(normalized_text))
            ))
            print(
                "   raw errors: %s\n   raw errors: %s" % ([s for (s, w) in correct_raw], [w for (s, w) in correct_raw]))
            print(
                "   txt errors: %s\n   txt errors: %s" % ([s for (s, w) in correct_txt], [w for (s, w) in correct_txt]))
            print(
                "   nor errors: %s\n   nor errors: %s" % ([s for (s, w) in correct_nor], [w for (s, w) in correct_nor]))

        # find currency
        currency_matches = re_currency_matches(normalized_text)
        # print currency
        # if len(currency_matches) > 0:
        #     print('%s found in: %s' % (currency_matches, raw_text.replace('\n', ' ')))

        number_match = re.search(r'\d\d*(?:[.]\d+)?', normalized_text)
        if number_match and len(currency_matches) == 0:
            number = int(number_match.group())
            if number == 2016 or number < 10:
                pass
            elif number_match.end() + 1 < len(normalized_text) and normalized_text[number_match.end() + 1] == '%':
                pass
            else:
                pass
                # print('%s found in: %s' % (currency_matches, raw_text.replace('\n', ' ')))

        # TODO: find dates
        date_matches = re_date_matches(normalized_text)

        self.tweet_n_unique += 1
        filename = '%s:%s' % (os.path.basename(self.reader.current_file), self.reader.i)
        keywords_length = len(keywords)
        return {
                   'id': id,
                   'filename': filename,
                   'rt': rt,
                   'user_id': user_id,
                   'mentions': mentions,
                   'urls': urls,
                   'hashtags': hashtags,
                   'symbols': symbols,
                   'media': media,
                   'source_type': source_type,
                   'source_url': source_url,

                   'full_text': raw_text,
                   'text': text,
                   'fully_normalized_text': normalized_text_2,
                   'keywords': keywords,
                   'keywords_length': keywords_length,

                   'newline_count': newline_count,
                   'questionmark': questionmark,
                   'quotations': quotations,
                   'ends_dots': ends_dots,
                   'currencies': currency_matches,

                   'n_html_entities': n_html_entities,
                   'n_abbriviations': n_abbriviations,
                   'n_quationmarks': n_quationmarks,
                   'n_unicode': n_unicode,
                   'n_punctuations': n_punctuations,
                   'n_unprintable': n_unprintable,
               }, user_output

    def process_source(self, source):
        if source == '':
            source_url = ''
            source_type = 'unknown'
        else:
            source_match = re_html_a_tag.match(source)
            if source_match is None:
                raise ValueError("Could not identify source: `%s` at %d" % (source, self.i - 1))
            source_url = source_match.group(1)
            source = source_match.group(2)
            if source not in self.tweet_sources:
                self.tweet_sources.add(source)
                # print newly found source
                # print("Found new source:\n raw_source: %s\n source: %s\n source_url: %s" % (raw_data['source'], source, source_url))
            if source == 'Twitter Web Client':
                source_type = 'web_client'
            elif source == 'Twitter for Android':
                source_type = 'mobile'
            elif source == 'Twitter for iPhone':
                source_type = 'mobile'
            elif source == 'Twitter for iPad':
                source_type = 'mobile'
            elif source == 'Twitter for BlackBerry':
                source_type = 'mobile'
            elif source.startswith('Mobile Web ('):
                source_type = 'mobile'
            else:
                # probably web
                source_type = 'other'

        return source_type, source_url

    def __str__(self):
        return str({var: val for (var, val) in vars(self).items() if var not in ['replace_words', 'stopwords']})

    def should_ignore(self, raw_data):
        """
        check if it should be ignored
        :param raw_data:
        :return:
        """
        if 'id' not in raw_data:
            # skip incomplete tweets
            self.tweet_skipped.append(raw_data)
            return True
        if 'text' not in raw_data:
            # skip incomplete tweets
            self.tweet_skipped.append(raw_data)
            return True
        if 'lang' not in raw_data:
            # skip incomplete tweets
            self.tweet_skipped.append(raw_data)
            return True
        if raw_data['lang'] != 'en':
            # only look at english tweets
            self.tweet_skipped.append(raw_data)
            return True
        if 'user' not in raw_data:
            # only look at tweets with a user account
            self.tweet_skipped.append(raw_data)
            return True
        if 'entities' not in raw_data:
            # suspicious
            self.tweet_skipped.append(raw_data)
            return True
        if raw_data['lang'] != 'en':
            # only look at english tweets
            self.tweet_skipped.append(raw_data)
            return True
        # check input assertions
        if __debug__:
            assert raw_data['retweet_count'] == 0
            assert raw_data['retweeted'] == False
            assert 'entities' in raw_data
            if 'retweeted_status' in raw_data:
                assert not raw_data['retweeted_status']['retweeted']
                assert len(raw_data['entities']['user_mentions']) > 0
                first_mention = raw_data['entities']['user_mentions'][0]['screen_name']
                assert raw_data['text'].lower().startswith(('RT @' + first_mention + ': ').lower())
                assert raw_data['text'][3:4] == '@'
            for um in raw_data['entities']['user_mentions']:
                assert len(um['indices']) == 2
                i_start = um['indices'][0] + 1
                i_end = um['indices'][1]
                assert i_end - i_start > 0
                mention_raw_text_start = raw_data['text'][i_start - 1:i_start]
                assert mention_raw_text_start == '@' or mention_raw_text_start == '＠', mention_raw_text_start
                assert um['screen_name'].lower() == raw_data['text'][i_start:i_end].lower()
            for e_type in raw_data['entities'].keys():
                assert e_type in ['media', 'hashtags', 'urls', 'user_mentions', 'symbols'], e_type
            if 'media' in raw_data['entities']:
                for m in raw_data['entities']['media']:
                    assert 'indices' in m, m
        return False

    def process_user(self, raw_data):
        u = raw_data['user']
        u_id = 'u' + u['id_str']
        followers_count = u['followers_count']
        favourites_count = u['favourites_count']
        statuses_count = u['statuses_count']
        created_at = int(datetime.strptime(u['created_at'], '%a %b %d %H:%M:%S +0000 %Y').timestamp())
        location = u['location']
        return {
            'u_id': u_id,
            'followers_count': followers_count,
            'favourites_count': favourites_count,
            'statuses_count': statuses_count,
            'created_at': created_at,
            'location': location,
        }


class ArticlePreprocessor(Processor):
    def __init__(self, reader: InputReader, writer: Writer):
        super().__init__(reader, writer)

    def pp_article_data(self, raw_data):
        """ preprocesses the article for feature extraction
        :param raw_data
        :return: preprocessed_data
        """
        self.i += 1
        raw_description = raw_data['Description']

        article_id = hash(raw_description)
        article_id = article_id if article_id >= 0 else -article_id
        while article_id in self.article_ids:
            article_id += 1
        self.article_ids.add(article_id)

        if raw_description in self.article_descriptions:
            print("Duplicate %s" % raw_description)

        author_ids = []
        if raw_data['Author'] != '':
            author_names = raw_data['Author'].split(', ')
            for author_name in author_names:
                if author_name == '':
                    raise ValueError()
                if author_name in self.article_authors:
                    author_id = self.article_authors[author_name]
                else:
                    author_id = hash(author_name)
                    author_id = author_id if author_id >= 0 else -author_id
                    while author_id in self.article_authors.values():
                        author_id += 1
                    self.article_authors[author_name] = author_id
                author_ids.append(author_id)

        raw_description = raw_data['Description']
        description = raw_description
        is_html = re_html.search(description) is not None
        if is_html:
            finditer = re_unicode_decimal.finditer(description)
            offset = 0
            for m in finditer:
                unicode = (m.group(1) or m.group(2))
                description = str(description[0:m.start() + offset] + description[m.end() + offset:len(description)])
                offset -= (m.end() - m.start())
            assert re_unicode_decimal.search(description) is None
            description = re_html.sub(' ', description)
        description = re_whitespace.sub(' ', description).strip()
        if description == '':
            raise ValueError()

        # published_date
        try:
            published_date_str = raw_data['Publish date'].replace('CET', '')
            published_date_str = published_date_str.replace('CEST', '')
            published_date = datetime.strptime(published_date_str, '%a %b %d %H:%M:%S  %Y')
        except ValueError as e:
            print("Could not parse date %s" % raw_data['Publish date'])
            raise e

        # title
        title = raw_data['Title']

        # link
        url = urlparse(raw_data['Link'])
        link = url.geturl()
        domain = str(url.hostname)
        if domain.startswith('www.'):
            domain = domain[4:len(domain)]
        if domain.endswith('.com'):
            domain = domain[0:len(domain) - 4]

        return {
            'id': article_id,
            'author_ids': author_ids,
            'description': description,
            'html': is_html,
            'published_date': published_date,
            'title': title,
            'link': link,
            'domain': domain
        }


TWEET_COLUMNS = (
    'id', 'filename', 'rt', 'user_id', 'mentions', 'urls', 'hashtags', 'symbols', 'media', 'source_type',
    'source_url', 'full_text', 'text', 'fully_normalized_text', 'keywords', 'keywords_length', 'newline_count',
    'questionmark', 'quotations', 'ends_dots', 'currencies', 'n_html_entities', 'n_abbriviations',
    'n_quationmarks', 'n_unicode', 'n_punctuations', 'n_unprintable'
)
TUSER_COLUMNS = (
    'u_id', 'followers_count', 'favourites_count', 'statuses_count', 'created_at', 'location'
)


def pp_tweets():
    # Read and process all tweets from config.TWEETS_RAW_HOMEDIR
    inputdir = os.path.join(config.PCLOUD_BUFFER_DIR, 'raw-tweets')
    outputdir_tweets = os.path.join(config.PCLOUD_BUFFER_DIR, 'preprocessed-tweets')
    outputdir_tusers = os.path.join(config.PCLOUD_BUFFER_DIR, 'preprocessed-tusers')

    pre_processor = TweetPreprocessor(
        InputReader(inputdir),
        CSVWriter(outputdir_tweets, 'tweets', clear_output_dir=True, columns=TWEET_COLUMNS),
        CSVWriter(outputdir_tusers, 'tusers', clear_output_dir=True, columns=TUSER_COLUMNS)
    )
    pre_processor()


def pp_articles():
    # Read and process all tweets from config.TWEETS_RAW_HOMEDIR
    inputdir = os.path.join(config.PCLOUD_DIR, 'RSS')
    outputdir = os.path.join(config.PCLOUD_BUFFER_DIR, 'preprocessed-articles')

    pre_processor = ArticlePreprocessor(
        InputReader(inputdir),
        CSVWriter(outputdir, 'tweets', clear_output_dir=True)
    )
    pre_processor()


if __name__ == '__main__':
    pp_tweets()
