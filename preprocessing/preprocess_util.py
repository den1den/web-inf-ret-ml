import re
import string
import unicodedata
from abc import abstractmethod
from operator import itemgetter

#
# Regex patterns
#
from inputoutput.readers import InputReader

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
re_quotations_somewhere = re.compile(r'.*"\s*([^"]+)[.]?\s*".*')
re_quotations_somewhere_single = re.compile(r".*'\s*([^']+)[.]?\s*'.*")
re_quotations_somewhere_slashes = re.compile(r".*/\s*([^/]+)[.]?\s*/.*")
re_title_2 = re.compile(r"\s*=\s*'([^']+)';?.*")
re_url_wp_date = re.compile(r'.*/wp/\d\d\d\d/\d\d/\d\d/([^/]*)/.*')
re_url_stripes = re.compile(r'/(\w+-?-\w+-?-\w+(?:-?-\w+)+)')
re_url_stripes_no_id = re.compile(r'(\w+(?:-?-[0-9a-zA-Z]+)+)-\d+')

#
# Manual replacement
#
drop_punctuation = [',', '.', '#', '@', '[', ']', '{', '}', '"', ':', '!', "'", '?', '\\']
replace_html_entities = (
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
replace_abbreviations = (
    ("ain't", 'are not'),
    ("can't", 'cannot'),
    (" he's", ' he is'),
    (" she's", ' she is'),
    (" we're", ' we are'),
    ("we're", 'we are'),
    (" w/", ' with'),
)

#
# Helper functions
#

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

class MultiProcessor:
    """
    Helper class to read and write large files. And also parse the users
    """

    def __init__(self, reader: InputReader, writers):
        """
        :param reader:
        :param writers: list of writers
        """
        self.reader = reader
        assert len(writers) > 0
        self.writers = writers

    def __call__(self, n=None):
        """
        :param n: number of input items to parse
        """
        for raw_data_element in self.reader:
            try:
                self.process(raw_data_element)
            except Exception as e:
                print("Warning: could not process %s:%d %s" % (self.reader.current_file, self.reader.i, e))
                print("         data: %s" % raw_data_element)
                output_array = None
            if n is not None and self.reader.i == n:
                break
        self.done()

    @abstractmethod
    def process(self, raw_data):
        """
        :param raw_data:
        :return: None
        """
        pass

    def processed_obj(self, i, obj):
        """
        :param i: index of writer to use
        :param obj: obj that is processed
        :return:
        """
        self.writers[i].write(obj)

    def done(self):
        for w in self.writers:
            w.close()
        print("Done processing %d to %s" % (self.reader.i, [w.i for w in self.writers]))


