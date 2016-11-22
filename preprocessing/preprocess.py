import os
import re
import string
import time
from operator import itemgetter
from urllib.parse import urlparse

from nltk.corpus import stopwords

from config import config
from inputoutput.input import csv_write, read_json_array_from_files, Reader
from preprocessing.spell_checker import known_correct

re_whitespace = re.compile(r'\s+')
re_html = re.compile(r'<[^>]+>')
re_unicode_decimal = re.compile(r'&#(\d{2,4});|&([a-z]+);')
re_unicode = re.compile(r'[^\x00-\x7f]')
re_html_a_tag = re.compile(r'<a href="([^"]+)"[^>]*>(.+)</a>', flags=re.IGNORECASE)
re_next_word = re.compile(r'\s*(\w+)(…|[.][.][.])?')
CURRENCY_PATTERN = r'[$€](\d+(?:[,]\d+)*(?:[.]\d+)?)'
re_currency = re.compile(r'(?:^|\s+)' + CURRENCY_PATTERN + r'(?:$|\s+)')
re_currency = re.compile(CURRENCY_PATTERN)
re_quotations = re.compile(r'"\s*([^"]+)[.]?\s*"')

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


class Preprocessor:
    def __init__(self):
        self.i = 0

        self.tweet_skipped = []
        self.tweet_n_unique = 0
        self.tweet_n_duplicate = 0
        self.tweet_texts = {}
        self.tweet_sources = set()
        self.quotations = set()

        self.stopwords = set(stopwords.words('english'))
        self.drop_chars = [',', '.', '#', '@', '[', ']', '{', '}', '"', ':', '!', "'", '?', '\\']
        self.replace_chars = [
            ('&amp;', 'and'),
            ('&gt;', '>'),
            ('&lt;', '<'),
            ('\n', ' '),
        ]
        self.replace_words = (
            ("ain't", 'are not'),
            ("can't", 'cannot'),
            (" he's", ' he is'),
            (" she's", ' she is'),
            (" we're", ' we are'),
            ("we're", 'we are'),
        )

        self.article_authors = {}
        self.article_ids = set()
        self.article_descriptions = set()

    def pp_tweet_data(self, raw_data, reader:Reader):
        """ process a tweet for feature extraction
        :param raw_data
        :return: preprocessed_data
        """
        self.i += 1

        #
        # check if it should be ignored
        #
        if 'id' not in raw_data:
            # skip incomplete tweets
            self.tweet_skipped.append(raw_data)
            return None
        if 'text' not in raw_data:
            # skip incomplete tweets
            self.tweet_skipped.append(raw_data)
            return None
        if 'lang' not in raw_data:
            # skip incomplete tweets
            self.tweet_skipped.append(raw_data)
            return None
        if raw_data['lang'] != 'en':
            # only look at english tweets
            self.tweet_skipped.append(raw_data)
            return None
        if 'user' not in raw_data:
            # only look at tweets with a user account
            self.tweet_skipped.append(raw_data)
            return None
        if 'entities' not in raw_data:
            # suspicious
            self.tweet_skipped.append(raw_data)
            return None
        if raw_data['lang'] != 'en':
            # only look at english tweets
            self.tweet_skipped.append(raw_data)
            return None

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
                assert raw_data['text'][i_start - 1:i_start] == '@'
                assert um['screen_name'].lower() == raw_data['text'][i_start:i_end].lower()

        # tweet id
        id = 't' + str(raw_data['id'])

        # user_id
        if 'user' not in raw_data:
            user_id = '-1'
        else:
            user_id = str(raw_data['user']['id'])

        # rt
        rt = 'retweeted_status' in raw_data

        # @
        mentions = [str(um['id']) for um in raw_data['entities']['user_mentions']]

        # urls
        urls = [url['expanded_url'] for url in raw_data['entities']['urls']]

        # hashtags
        hashtags = [hashtag['text'] for hashtag in raw_data['entities']['hashtags']]

        # source
        source = raw_data['source']
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

        if id == 't783506351360139264':
            pass
        #
        # text processing
        #
        raw_text = str(raw_data['text'])  # the original
        text = raw_text  # as much like the original
        normalized_text = raw_text  # as much normalized

        if __debug__:
            # check for duplicate tweets
            if id in self.tweet_texts:
                previously_found_text = self.tweet_texts[id]
                if previously_found_text != raw_text:
                    raise ValueError("Tweet with same ID but different text found")
                else:
                    # skip tweets with same text and id
                    self.tweet_n_duplicate += 1
                    return None
            else:
                self.tweet_texts[id] = raw_text

        #
        # remove entities (stripped_text)
        # these are given in the original indices, so should be done first on the `normalized_text`
        #
        index_offset = 0
        strip_indices = []
        for e_type in raw_data['entities']:
            for e in raw_data['entities'][e_type]:
                strip_indices.append((e['indices'][0], e['indices'][1],))
        strip_indices.sort(key=itemgetter(0))
        for (index_start, index_end) in strip_indices:
            normalized_text = normalized_text[:index_start - index_offset] + normalized_text[index_end - index_offset:]
            index_offset += index_end - index_start

        # replace chars (stripped_text, text)
        for (find, replace) in self.replace_chars:
            i = 0
            while True:
                i = text.find(find, i)
                if i == -1:
                    break
                text = text[0:i] + replace + text[i + len(find):]
            i = 0
            while True:
                i = normalized_text.find(find, i)
                if i == -1:
                    break
                normalized_text = normalized_text[:i] + replace + normalized_text[i + len(find):]
        # lowercase
        normalized_text = normalized_text.strip().lower()
        # ends_dots
        ends_dots = normalized_text.endswith('…') or normalized_text.endswith('...')
        if ends_dots:
            # strip differently with end_dots
            if normalized_text.endswith('…'):
                normalized_text = normalized_text[0:len(normalized_text) - 1]
            if normalized_text.endswith('...'):
                normalized_text = normalized_text[0:len(normalized_text) - 3]
            if normalized_text.endswith(' '):
                # Only strip the last '...'
                pass
            else:
                # Strip the last '...' and the last word, as it was probably cut off
                #FIXME: decide when to skip these things
                if len(normalized_text) < 25:
                    # print(" note: not skipping last word in: %s" % raw_text.replace('\n', ''))
                    pass # probably not cut off
                else:
                    # print(" note: skipping last word in: %s" % raw_text.replace('\n', ''))
                    normalized_text = normalized_text.rsplit(' ', 1)[0]
        # strip 'RT : '
        if rt:
            if not normalized_text.startswith('rt : '):
                #FIXME
                raise ValueError("Could not strip RT")
            normalized_text = normalized_text[5:]
            index_offset += 5
            text = text[6 + len(raw_data['entities']['user_mentions'][0]['screen_name']):]
        # replace words
        for (find, replace) in self.replace_words:
            i = 0
            while True:
                i = normalized_text.find(find, i)
                if i == -1:
                    break
                # print('replacing %s in %s' % (find, raw_text.replace('\n', ' ')))
                normalized_text = normalized_text[0:i] + replace + normalized_text[i + len(find):]
        # remove special chars
        dropped_chars = 0
        for s in self.drop_chars:
            i = 0
            while True:
                i = normalized_text.find(s, i)
                if i == -1:
                    break
                normalized_text = normalized_text[0:i] + normalized_text[i + len(s):len(normalized_text)]
                dropped_chars += 1
        pre_unicodefilter_size = len(normalized_text)
        normalized_text = ''.join(filter(lambda x: x in string.printable, normalized_text))
        dropped_chars += pre_unicodefilter_size - len(normalized_text)

        # remove duplicate spaces and unwanted characters (text)
        text = ''.join(filter(lambda x: x in string.printable, text))
        if '\\' in text:
            text = text.replace('\\', '')
        try:
            text = re_whitespace.sub(text, ' ')
        except Exception:
            #FIXME: why does this fail?
            raise e
        if config.SPELLING:
            print("Tweet (%d)\n     raw_text: %s\n         text: %s\n   normalized: %s" % (self.i-1, raw_text.replace('\n', '<NEWLINE>'), text, normalized_text))

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
            #TODO: check how to interpet these results
            correct_raw = [known_correct(word) for word in re_whitespace.split(raw_text)]
            correct_txt = [known_correct(word) for word in re_whitespace.split(text)]
            correct_nor = [known_correct(word) for word in re_whitespace.split(normalized_text)]
            print(" error rating: %d/%d, %d/%d, %d/%d" % (
                sum([1 << s for (s, w) in correct_raw]), len(re_whitespace.split(raw_text)),
                sum([1 << s for (s, w) in correct_txt]), len(re_whitespace.split(text)),
                sum([1 << s for (s, w) in correct_nor]), len(re_whitespace.split(normalized_text))
            ))
            print("   raw errors: %s\n   raw errors: %s" % ([s for (s, w) in correct_raw], [w for (s, w) in correct_raw]))
            print("   txt errors: %s\n   txt errors: %s" % ([s for (s, w) in correct_txt], [w for (s, w) in correct_txt]))
            print("   nor errors: %s\n   nor errors: %s" % ([s for (s, w) in correct_nor], [w for (s, w) in correct_nor]))

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

        #TODO: find dates
        date_matches = re_date_matches(normalized_text)

        self.tweet_n_unique += 1
        return {
            'id': id,
            'filename': '%s:%s' % (os.path.basename(reader.current_file), reader.i),
            'full_text': raw_text,
            'text': text,
            'rt': rt,
            'mentions': mentions,
            'urls': urls,
            'hashtags': hashtags,
            'newline_count': newline_count,
            'ends_dots': ends_dots,
            'user_id': user_id,
            'questionmark': questionmark,
            'keywords': keywords,
            'keywords_length': len(keywords),
            'dropped': dropped_chars,
            'source_type': source_type,
            'source_url': source_url,
            'currencies': currency_matches,
            'quotations': quotations
        }

    def __str__(self):
        return str({var: val for (var, val) in vars(self).items() if var not in ['replace_words', 'stopwords']})

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
            domain = domain[0:len(domain)-4]

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


def pp_tweets():
    # Read and process all tweets from config.TWEETS_RAW_HOMEDIR
    inputdir = os.path.join(config.PCLOUD_BUFFER_DIR, 'raw-tweets')
    outputdir = os.path.join(config.PCLOUD_BUFFER_DIR, 'preprocessed-tweets')

    pre_processor = Preprocessor()
    try:
        # tweets_reader = Reader(pre_processor.pp_tweet_data, inputdir, item_offset=0, filename_prefix='20161005___1.24.valid.json')
        tweets_reader = Reader(pre_processor.pp_tweet_data, inputdir, item_offset=0)
        tweets_reader.supply_reader = True
        tweets = tweets_reader.read()
        # tweets = read_json_array_from_files(pre_processor.pp_tweet_data, inputdir, item_offset=153810)
        # tweets = read_json_array_from_files(pre_processor.pp_tweet_data, os.path.join(inputdir, 'elections-23-10-raw'), item_offset=1, filename_prefix='20161023__1')
        print(pre_processor.tweet_sources)
        csv_write(os.path.join(config.PROJECT_DIR, 'pp-tweets-%d.csv' % time.time()), tweets,
                  columns=('id',
                           'filename',
                           'full_text',
                           'text',
                           'rt',
                           'mentions',
                           'urls',
                           'hashtags',
                           'newline_count',
                           'ends_dots',
                           'user_id',
                           'questionmark',
                           'keywords',
                           'keywords_length',
                           'dropped',
                           'source_type',
                           'source_url',
                           'currencies',
                           'quotations'))
    except Exception as e:
        print(pre_processor.tweet_sources)
        raise e


def pp_articles():
    # Read and process all tweets from config.TWEETS_RAW_HOMEDIR
    inputdir = os.path.join(config.PCLOUD_DIR, 'RSS')
    outputdir = os.path.join(config.PCLOUD_BUFFER_DIR, 'preprocessed-articles')

    pre_processor = Preprocessor()
    # articles = read_json_array_from_files(pre_processor.pp_article_data, inputdir, filename_postfix='20161021_4.json', item_offset=7)
    articles = read_json_array_from_files(pre_processor.pp_article_data, inputdir, filename_postfix='.json', item_offset=0)
    csv_write(os.path.join(config.PROJECT_DIR, 'pp-articles-%s.csv' % time.time()), articles)


if __name__ == '__main__':
    pp_tweets()

