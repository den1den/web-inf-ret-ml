import os
import re
from datetime import datetime

from nltk.corpus import stopwords

from config import config
from inputoutput.readers import InputReader
from inputoutput.writers import Writer
from preprocessing.preprocess_util import re_currency_matches, re_date_matches, remove_by_indices, replace_in_string, \
    remove_strings, remove_unicode, replace_whitespaces, remove_unprintable, replace_nonalpha_in_string, \
    re_whitespace, re_html_a_tag, re_quotations, MultiProcessor, drop_punctuation, replace_html_entities, \
    replace_abbreviations
from preprocessing.spell_checker import known_correct


class TweetPreprocessor(MultiProcessor):

    def __init__(self, reader: InputReader, writer: Writer, user_writer):
        super().__init__(reader, (writer, user_writer))
        self.stopwords = set(stopwords.words('english'))
        self.drop_punctuation = drop_punctuation
        self.replace_html_entities = replace_html_entities
        self.replace_abbreviations = replace_abbreviations
        self.tweet_skipped = []
        self.tweet_n_unique = 0
        self.tweet_n_duplicate = 0
        self.tweet_texts = {}
        self.tweet_sources = set()
        self.quotations = set()

    TWEET_COLUMNS = (
        'id', 'filename', 'rt', 'user_id', 'mentions', 'urls', 'hashtags', 'symbols', 'media', 'source_type',
        'timestamp',
        'source_url', 'full_text', 'text', 'fully_normalized_text', 'keywords', 'keywords_length', 'newline_count',
        'questionmark', 'quotations', 'ends_dots', 'currencies', 'n_html_entities', 'n_abbriviations',
        'n_quationmarks', 'n_unicode', 'n_punctuations', 'n_unprintable'
    )
    TUSER_COLUMNS = (
        'u_id', 'followers_count', 'favourites_count', 'statuses_count', 'created_at', 'location'
    )

    def process(self, raw_data):
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
                    from preprocessing.preprocess import REPORT_DUPLICATE
                    if REPORT_DUPLICATE:
                        print("Warning: duplicate tweet %s found!" % id)
                    return None, None
            else:
                self.tweet_texts[id] = raw_data['text']

        # user_id
        if 'user' not in raw_data:
            user_id = 'unknown'
        else:
            user_id = 'u' + raw_data['user']['id_str']
            self.process_user(raw_data)

        # rt
        rt = 'retweeted_status' in raw_data

        # @
        mentions = [str('u' + um['id']) for um in raw_data['entities']['user_mentions']]

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

        if 'extended_entities' in raw_data and 'media' in raw_data['extended_entities']:
            for m in raw_data['extended_entities']['media']:
                if media['id'] not in [m['id'] for m in media]:
                    print("Assertion failed, Media only found in extended media, asserted entities => extended_entities")
                    media.append({'id': media['id'], 'type': media['type'], 'url': media['url']})
                    raise AssertionError("Duplicate media")

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

        # timestamp
        timestamp = int(raw_data['timestamp_ms'])

        self.tweet_n_unique += 1
        filename = '%s:%s' % (os.path.basename(self.reader.current_file), self.reader.i)
        keywords_length = len(keywords)
        self.processed_obj(0, {
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
            'timestamp': timestamp,

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
        })

    def process_source(self, source):
        if source == '':
            source_url = ''
            source_type = 'unknown'
        else:
            source_match = re_html_a_tag.match(source)
            if source_match is None:
                raise ValueError("Could not identify source: `%s` at %d" % (source, self.read_objects_counter - 1))
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
        self.processed_obj(1, {
            'u_id': u_id,
            'followers_count': followers_count,
            'favourites_count': favourites_count,
            'statuses_count': statuses_count,
            'created_at': created_at,
            'location': location,
        })
