import json
import os
import random
import re
from operator import itemgetter
from datetime import datetime
import math
from urllib.parse import urlparse
from config import config
from inputoutput.input import csv_write, read_json_array_from_files
from nltk.corpus import stopwords

re_spaces = re.compile(r'\s+')
re_html = re.compile(r'<[^>]+>')
re_unicode_decimal = re.compile(r'&#(\d{2,4});|&([a-z]+);')
re_html_a_tag = re.compile(r'<a href="([^"]+)"[^>]*>(.+)</a>', flags=re.IGNORECASE)

class Preprocessor:
    def __init__(self):
        self.i = 0

        self.tweet_skipped = []
        self.tweet_n_unique = 0
        self.tweet_n_duplicate = 0
        self.tweet_texts = {}
        self.tweet_sources = set()

        self.stopwords = set(stopwords.words('english'))
        self.drop_chars = [',', '.', '#', '@', '[', ']', '{', '}', '"', ':', '!', "'", '?']
        self.replace_words = [(' n\'t', ' not'), ('n\'t', ' not'), ('&amp;', 'and'), (' he\'s', ' he is')]

        self.article_authors = {}
        self.article_ids = set()
        self.article_descriptions = set()

    def pp_tweet_data(self, raw_data):
        """ process a tweet for feature extraction
        :param raw_data
        :return: preprocessed_data
        """
        self.i += 1

        # id
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
        id = int(raw_data['id'])

        # text
        raw_text = str(raw_data['text'])
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

        # rt
        rt = 'retweeted_status' in raw_data

        # @
        mentions = [um['id'] for um in raw_data['entities']['user_mentions']]

        # urls
        urls = [url['expanded_url'] for url in raw_data['entities']['urls']]

        # hashtags
        hashtags = [hashtag['text'] for hashtag in raw_data['entities']['hashtags']]

        # newline_count
        newline_count = raw_text.count('\n')

        # user_id
        user_id = raw_data['user']['id']

        # questionmark
        questionmark = '?' in raw_text

        # keywords / stripping
        stripped_text = raw_text
        index_offset = 0
        strip_indices = []
        for e_type in raw_data['entities']:
            for e in raw_data['entities'][e_type]:
                strip_indices.append((e['indices'][0], e['indices'][1], ))
        strip_indices.sort(key=itemgetter(0))
        for (index_start, index_end) in strip_indices:
            stripped_text = stripped_text[0:index_start - index_offset] + stripped_text[index_end - index_offset:len(stripped_text)]
            index_offset += index_end - index_start
        stripped_text = stripped_text.strip().lower()
        # ends_dots
        ends_dots = stripped_text.endswith('…') or stripped_text.endswith('...')
        if ends_dots:
            # strip differently with end_dots
            if stripped_text.endswith('…'):
                stripped_text = stripped_text[0:len(stripped_text) - 1]
            if stripped_text.endswith('...'):
                stripped_text = stripped_text[0:len(stripped_text) - 3]
            if stripped_text.endswith(' '):
                print('End cutoff alright? %d' % (self.i - 1))
                # print('%d, %d' % (raw_text.count('…'), raw_text.count('...')))
                # print('           raw: ' + raw_text)
                # print(' stripped_text: ' + stripped_text + '\n')
            else:
                # probably last word is cut off
                stripped_text = stripped_text.rsplit(' ', 1)[0]
        if rt:
            index_trim = len('RT : ')
            stripped_text = stripped_text[index_trim:len(stripped_text)]
            index_offset += index_trim

        dropped_chars = 0
        for s in self.drop_chars:
            i = 0
            while True:
                i = stripped_text.find(s, i)
                if i == -1:
                    break
                stripped_text = stripped_text[0:i] + stripped_text[i + len(s):len(stripped_text)]
            if s in stripped_text:
                stripped_text = stripped_text.replace(s, '')
                dropped_chars += 1
        for (find, replace) in self.replace_words:
            i = 0
            while True:
                i = stripped_text.find(find, i)
                if i == -1:
                    break
                stripped_text = stripped_text[0:i] + replace + stripped_text[i+len(find):len(stripped_text)]
        # remove duplicate spaces
        stripped_text = re_spaces.sub(' ', stripped_text)
        keywords = [word for word in stripped_text.split(' ') if word not in self.stopwords]
        if '.' in keywords:
            raise ValueError()

        # check input assertions
        assert raw_data['retweet_count'] == 0
        assert raw_data['retweeted'] == False
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

        # source
        if raw_data['source'] == '':
            source = 'unknown'
        source_match = re_html_a_tag.match(raw_data['source'])
        if source_match is None:
            raise ValueError("Could not identify source: `%s` at %d" % (raw_data['source'], self.i))
        source = source_match.group(1)
        source_url = source_match.group(2)
        if source not in self.tweet_sources:
            self.tweet_sources.add(source)
            print("raw_source: %s\n source: %s\n source_url: %s" % (raw_data['source'], source, source_url))
        if source == 'Twitter Web Client':
            source = 'web_client'
        elif source == 'Twitter for Android':
            source = 'mobile_android'
        elif source == 'Twitter for iPhone':
            source = 'mobile_iPhone'
        elif source == 'Twitter for iPad':
            source = 'mobile_iPad'
        elif source == 'Twitter for BlackBerry':
            source = 'mobile_blackberry'
        elif source.startswith('Mobile Web ('):
            source = 'mobile_webclient'
        else:
            # probably web
            source = source.lower().split('.')[0]
            source = '3party_' + source

        self.tweet_n_unique += 1
        return {
            'id': id,
            'full_text': raw_text,
            'rt': rt,
            'mentions': mentions,
            'urls': urls,
            'hashtags': hashtags,
            'newline_count': newline_count,
            'ends_dots': ends_dots,
            'user_id': user_id,
            'questionmark': questionmark,
            'keywords': keywords,
            'dropped': dropped_chars,
            'source': source,
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
        description = re_spaces.sub(' ', description).strip()
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
        # tweets = read_json_array_from_files(pre_processor.pp_tweet_data, inputdir, filename_prefix='20161006___1.20', item_offset=140, item_count=1)
        # tweets = read_json_array_from_files(pre_processor.pp_tweet_data, inputdir, filename_prefix='xaa') + read_json_array_from_files(pre_processor.pp_tweet_data, inputdir, filename_postfix='___0.0.valid.json')
        # print(pre_processor.tweet_sources)
        # tweets = read_json_array_from_files(pre_processor.pp_tweet_data, inputdir, item_offset=153810)
        tweets = read_json_array_from_files(pre_processor.pp_tweet_data, inputdir)
        tweets = read_json_array_from_files(pre_processor.pp_tweet_data, inputdir, item_offset=153810, filename_prefix='20161022___0')
        print(pre_processor.tweet_sources)
        csv_write(os.path.join(config.PROJECT_DIR, 'pre-test.csv'), tweets)
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
    csv_write(os.path.join(config.PROJECT_DIR, 'pre-test-articles.csv'), articles)


if __name__ == '__main__':
    pp_tweets()

