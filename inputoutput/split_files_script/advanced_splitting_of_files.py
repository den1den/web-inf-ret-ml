"""
Splits all files in `root_dir` into `tweets_per_file_target` tweets.
If the number of characters one one line is less then 1 << 32, otherwise it is skipped
"""
import json
import os
import re
import time
from abc import abstractmethod, ABCMeta
from os import listdir

from inputoutput.input import clean_output_dir
from preprocessing.preprocess_util import re_whitespace

re_filename = re.compile(r'(\d{8})_+\d+\.json')
tweets_per_file_limit = 500
WRITE_OUTPUT = True
buffer = 1 << 22

ERROR_FILES = {'T:\\FILEZILLA PUBLIC FOLDER\\WebInfRet\\newoutput\\TWEETS\\20161004___1.json', 'T:\\FILEZILLA PUBLIC FOLDER\\WebInfRet\\newoutput\\TWEETS\\20161007___0.json', 'T:\\FILEZILLA PUBLIC FOLDER\\WebInfRet\\newoutput\\TWEETS\\20161005___0.json', 'T:\\FILEZILLA PUBLIC FOLDER\\WebInfRet\\newoutput\\TWEETS\\20161010___0.json', 'T:\\FILEZILLA PUBLIC FOLDER\\WebInfRet\\newoutput\\TWEETS\\20161006___1.json', 'T:\\FILEZILLA PUBLIC FOLDER\\WebInfRet\\newoutput\\TWEETS\\20161011___0.json', 'T:\\FILEZILLA PUBLIC FOLDER\\WebInfRet\\newoutput\\TWEETS\\20161008___0.json', 'T:\\FILEZILLA PUBLIC FOLDER\\WebInfRet\\newoutput\\TWEETS\\20161005___1.json', 'T:\\FILEZILLA PUBLIC FOLDER\\WebInfRet\\newoutput\\TWEETS\\20161009___0.json'}

class BaseParser(metaclass=ABCMeta):
    def __init__(self, input_dir, output_dir, output_item_limit):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.output_item_limit = output_item_limit
        self.items = []
        self.output_filename_base = None
        self.output_filename_index = 0
        self.mem_errors = set()

    def __call__(self):
        for input_filename in listdir(self.input_dir):
            input_filepath = os.path.join(self.input_dir, input_filename)
            if not os.path.isfile(input_filepath):
                continue
            try:
                # Check filename
                match = re_filename.match(input_filename)
                if not match:
                    print("Will not parse file %s" % input_filepath)
                    continue
                output_filename_base = match.group(1)
                if self.output_filename_base is None:
                    self.output_filename_base = output_filename_base
                elif self.output_filename_base != output_filename_base:
                    # New base filename, so new numbering
                    self.close()
                    self.output_filename_index = 0
                    self.output_filename_base = output_filename_base
                self.parse_file(input_filepath)
            except Exception as e:
                if type(e) is MemoryError:
                    # bp = BufferedParser(self.input_dir, self.output_dir, self.output_item_limit)
                    # bp.output_filename_index = self.output_filename_index
                    # bp.items = self.items
                    #
                    # bp.parse_file(input_filepath)
                    # bp.close()
                    #
                    # self.output_filename_index = bp.output_filename_index + 1
                    #
                    # continue
                    self.memory_error(input_filepath)
                else:
                    print("Could not parse file %s" % input_filepath)
        self.close()

    def memory_error(self, input_filepath):
        self.mem_errors.add(input_filepath)
        print("MemoryError found in: %s" % self.mem_errors)

    @abstractmethod
    def parse_file(self, input_filepath):
        pass

    def clean_output_dir(self):
        clean_output_dir(self.output_dir, '.valid.json')

    def output(self, force=False):
        if not (force or len(self.items) >= self.output_item_limit):
            return
        while True:
            output_path = os.path.join(self.output_dir,
                                       '%s__%d.valid.json' % (self.output_filename_base, self.output_filename_index))
            if WRITE_OUTPUT and len(self.items) > 0:
                t0 = time.time()
                with open(output_path, 'w+', encoding='UTF8') as fp:
                    json.dump(self.items[:self.output_item_limit], fp, indent=1)
            self.output_filename_index += 1
            self.items = self.items[self.output_item_limit:]
            if len(self.items) < self.output_item_limit:
                break

    def close(self):
        self.output(force=True)


class FullFileParser(BaseParser):
    def parse_file(self, input_filepath):
        with open(input_filepath, 'r', encoding='UTF8') as fp:
            print("Reading from %s" % input_filepath)
            self.parse_items(fp)

    @abstractmethod
    def parse_items(self, fp):
        pass


class NaiveParser(FullFileParser):
    chunk = ""
    max_item_size_chars = 100000

    def parse_string(self, raw_string):
        self.chunk += raw_string
        while self.try_find_tweet():
            self.output()

    def try_find_tweet(self):
        if self.chunk == "":
            return False
        pre_chunk = self.chunk[0:24000]
        i_start = 0
        item_candidates = pre_chunk.split('}{')
        if len(item_candidates) != 1:
            i_start += 2
        else:
            item_candidates = pre_chunk.split('}\n{')
            i_start += 3
        iso_chunk = item_candidates[0]
        if iso_chunk.endswith('\n'):
            iso_chunk = iso_chunk.rstrip()

        item_candidate = iso_chunk
        if not iso_chunk.startswith('{"extended_entities"'):
            item_candidate = '{' + item_candidate
        if not iso_chunk.endswith('"notifications":null}}'):
            item_candidate = item_candidate + '}'

        try:
            self.items.append(json.loads(item_candidate))
        except ValueError as e:
            print('iso_chunk: `%s`\n' % iso_chunk)
            print('item_candidate: `%s` ... `%s`\n' % (
                item_candidate[0:20], item_candidate[len(item_candidate) - 20:len(item_candidate)]))
            raise e
        self.chunk = self.chunk[len(iso_chunk) + i_start:len(self.chunk)]
        return True

    def parse_items(self, fp):
        lines = fp.readlines()
        content = ''.join(lines)
        if content.startswith('{'):
            content = content[1:len(content)]
        if content.endswith('}'):
            content = content[0:len(content) - 1]
        self.parse_string(content)


class NewLineSeparatedParser(FullFileParser):
    seen_ids = set()

    def parse_items(self, fp):
        n = 0
        lines = fp.readlines()
        for line in lines:
            self.parse_line(n, line)
            n += 1

    def parse_line(self, n: int, line: str):
        line_size = len(line)
        data = None
        datas = None
        original_line = line
        line = line.strip()
        if line == '[':
            return
        if line == ']':
            return
        if line.endswith('},'):
            line = line[:-1]
        if line.startswith('[{'):
            line = line[1:]
        if line.endswith('}]'):
            line = line[:-1]
        if line.startswith('][{'):
            line = line[2:]
        if not (line.startswith('{') and line.endswith('}')):
            print('error at line %d: %s ... %s' % (n, original_line[:10], original_line[-10:]))
            return
        try:
            data = json.loads(line)
        except ValueError as e:
            dups = line.count('}}{')
            if dups == 9999 or dups == 19999:
                line = line.replace('}}{', '}},{')
            try:
                datas = json.loads('[' + line + ']')
            except ValueError:
                raise e
        if data is not None:
            # 1 item found
            if 'id' in data:
                if data['id'] in self.seen_ids:
                    print("skipping duplicate id")
                else:
                    self.seen_ids.add(data['id'])
            self.items.append(data)
        elif datas is not None:
            # Multiple items found
            for data in datas:
                if 'id' in data:
                    if data['id'] in self.seen_ids:
                        print("skipping duplicate id")
                    else:
                        self.seen_ids.add(data['id'])
                self.items.append(data)
        self.output()


class BufferedParser(BaseParser):
    def __init__(self, input_dir, output_dir, output_item_limit):
        super().__init__(input_dir, output_dir, output_item_limit)
        self.chunk = ""
        self.tweets_found = 0

    def try_find_tweet(self):
        if self.chunk == "":
            return False
        splitted = self.chunk.split('}{')
        if len(splitted) == 1:
            splitted = re_whitespace.sub('', self.chunk).split('}{')
        concated = ""
        for i in range(0, len(splitted)):
            if i == 0:
                concated += splitted[i]
            else:
                concated += '}{' + splitted[i]
            if i > 10:
                print("  Skipping %s" % splitted[0])
                offset = len(splitted[0]) + 2
                self.chunk = self.chunk[offset:len(self.chunk)]
                return True
            try:
                self.x = json.loads('{' + concated + '}')
                self.items.append(self.x)
                self.tweets_found += 1
                self.output()
                offset = len(concated) + 2
                self.chunk = self.chunk[offset:len(self.chunk)]
                return True
            except ValueError as e:
                pass
        return False

    def parse_file(self, input_filepath):
        with open(input_filepath, 'r', encoding='utf8') as fp:
            self.chunk = fp.read(buffer)
            if self.chunk.startswith('{"'):
                self.chunk = self.chunk[1:len(self.chunk)]

            while True:
                r = fp.read(buffer)
                if r == "":
                    break
                self.chunk += r

                found = True
                while found:
                    found = self.try_find_tweet()

            # EOF reached
            if self.chunk.endswith('}}'):
                self.chunk = self.chunk[0:len(self.chunk) - 1]

            found = True
            while found:
                found = self.try_find_tweet()


if __name__ == '__main__':
    input_dir = r'T:\FILEZILLA PUBLIC FOLDER\WebInfRet\newoutput\TWEETS'
    output_dir = os.path.join(os.path.dirname(input_dir), 'tweets_valid')
    p = NewLineSeparatedParser(input_dir, output_dir, tweets_per_file_limit)
    p.clean_output_dir()
    p()
