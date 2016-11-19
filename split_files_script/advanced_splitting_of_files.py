"""
Splits all files in `root_dir` into `tweets_per_file_target` tweets.
If the number of characters one one line is less then 1 << 32, otherwise it is skipped
"""
import json
import os
from os import listdir

from preprocessing.preprocess import re_spaces

WRITE_OUTPUT = True

items_per_file_target = 1000
buffer = 1 << 25
buffer = 1 << 22
buffer = 1 << 4

class NaiveParser():
    chunk = ""
    max_item_size_chars = 100000

    file_index = 0
    items = []

    def __init__(self, base_input_path, base_filename, base_output_path):
        self.base_input_path = base_input_path
        self.base_filename = base_filename
        self.base_output_path = base_output_path
        self.clean_output_dir()

    def parse_string(self, raw_string):
        self.chunk += raw_string
        while self.try_find_tweet:
            if len(self.items) >= items_per_file_target:
                self.output()
            pass

    @property
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
            print('item_candidate: `%s` ... `%s`\n' % (item_candidate[0:20], item_candidate[len(item_candidate)-20:len(item_candidate)]))
            raise e
        self.chunk = self.chunk[len(iso_chunk)+i_start:len(self.chunk)]
        return True

    def clean_output_dir(self):
        # Delete previous
        if not os.path.exists(self.base_output_path):
            os.makedirs(self.base_output_path)
            return
        for f in listdir(self.base_output_path):
            if f.endswith('.valid.json'):
                old_filepath = os.path.join(self.base_output_path, f)
                print("removing %s" % old_filepath)
                os.remove(old_filepath)

    def output(self):
        output_path = os.path.join(self.base_output_path, '%s__%d.valid.json' % (self.base_filename, self.file_index))
        if WRITE_OUTPUT:
            if len(self.items) > 0:
                json.dump(self.items, open(output_path, 'w+', encoding='UTF8'))
                print("Output written to %s" % output_path)
        self.file_index += 1
        self.items = []

    def close(self):
        self.output()

    def parse_file(self, fp):
        lines = fp.readlines()
        content = ''.join(lines)
        if content.startswith('{'):
            content = content[1:len(content)]
        if content.endswith('}'):
            content = content[0:len(content) - 1]
        self.parse_string(content)


class Processor:
    chunk = ""
    file_index = 0
    file_array = []

    tweets_found = 0

    def __init__(self, dirpath, filename):
        basefilename, ext = os.path.splitext(filename)
        self.input_filepath = os.path.join(dirpath, filename)
        self.output_path = os.path.join(dirpath, 'valid')
        self.output_filepath = os.path.join(self.output_path, basefilename + '.valid.json')

    def try_find_tweet(self):
        if self.chunk == "":
            return False
        splitted = self.chunk.split('}{')
        if len(splitted) == 1:
            splitted = re_spaces.sub('', self.chunk).split('}{')
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
                self.file_array.append(self.x)
                self.tweets_found += 1
                if len(self.file_array) >= tweets_per_file_target:
                    self.print_output()
                offset = len(concated) + 2
                self.chunk = self.chunk[offset:len(self.chunk)]
                return True
            except ValueError as e:
                pass
        return False

    def print_output(self):
        if WRITE_OUTPUT:
            if not os.path.exists(self.output_path):
                os.makedirs(self.output_path)
            print("Writing %d to file %s" % (len(self.file_array), self.output_path))
            json.dump(self.file_array, open(self.output_path, 'w+'), indent=1)
        self.file_index += 1
        self.file_array = []

    def execute(self):
        print("executing %s" % self.input_filepath)
        self.delete_previous()

        with open(self.input_filepath, 'r', encoding='utf8') as fp:
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

        if len(self.file_array) > 0:
            self.print_output()

    def delete_previous(self):
        # Delete previous
        if not os.path.exists(self.output_path):
            return
        for f in listdir(self.output_path):
            if f.endswith('.valid.json'):
                print("removing "+os.path.join(self.output_path, f))
                os.remove(os.path.join(self.output_path, f))

if __name__ == '__main__':
    dir_to_process = 'E:\\pCloud_buffer\\raw-tweets\\elections-22-10-raw\\'
    p = NaiveParser(dir_to_process, '20161022', os.path.join(dir_to_process, 'valid'))
    for f in listdir(p.base_input_path):
        if f.startswith('20161022___') or f.startswith('20161022___'):
            filepath = os.path.join(p.base_input_path, f)
            with open(filepath, 'r', encoding='UTF8') as fp:
                print("Reading from %s" % filepath)
                p.parse_file(fp)
    p.close()
