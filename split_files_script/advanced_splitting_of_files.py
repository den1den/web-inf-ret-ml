"""
Splits all files in `root_dir` into `tweets_per_file_target` tweets.
If the number of characters one one line is less then 1 << 32, otherwise it is skipped
"""
import json
import os

from os import listdir

import re

WRITE_OUTPUT = True

skip_dirs = {'elections-03-10-raw', 'elections-28-09-raw', 'elections-29-09-raw'}

DENNIS_LINUX_ROOT_DIR = '/home/dennis/pCloudDrive/tweets/'
DENNIS_WINDOWS_ROOT_DIR = 'E:\\pCloud\\'
DENNIS_WINDOWS_OUTPUT_ROOT_DIR = 'E:\\pCloud_buffer\\'

root_dir = os.path.join(DENNIS_WINDOWS_ROOT_DIR, 'Tweet')

tweets_per_file_target = 1000
buffer = 1 << 25
buffer = 1 << 22


class Processor:
    chunk = ""
    file_index = 0
    file_array = []

    tweets_found = 0

    def __init__(self, dirpath, filename):
        self.dirpath = dirpath
        self.basefilename, ext = os.path.splitext(filename)
        self.filepath = os.path.join(dirpath, filename)
        self.output_path = os.path.join(DENNIS_WINDOWS_OUTPUT_ROOT_DIR, os.path.basename(self.dirpath))

    def try_find_tweet(self):
        if self.chunk == "":
            return False
        splitted = self.chunk.split('}{')
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
        output_filename = self.basefilename + "." + str(self.file_index) + '.valid.json'
        output_filepath = os.path.join(self.output_path, output_filename)
        if WRITE_OUTPUT:
            if not os.path.exists(self.output_path):
                os.makedirs(self.output_path)
            print("Writing %d to file %s" % (len(self.file_array), output_filepath))
            json.dump(self.file_array, open(output_filepath, 'w+'), indent=1)
        self.file_index += 1
        self.file_array = []

    def execute(self):
        print("executing %s" % self.filepath)
        self.delete_previous()

        with open(self.filepath, 'r', encoding='utf8') as fp:
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
        prefix = self.basefilename + '.'
        postfix = '.valid.json'
        r = re.compile(re.escape(prefix) + r'\d+' + re.escape(postfix))
        for f in listdir(self.dirpath):
            if r.match(f):
                print("removing "+os.path.join(self.dirpath, f))
                os.remove(os.path.join(self.dirpath, f))
        if os.path.exists(self.output_path):
            for f in listdir(self.output_path):
                if r.match(f):
                    print("removing " + os.path.join(self.output_path, f))
                    os.remove(os.path.join(self.output_path, f))


def main():
    print("Reading from %s" % root_dir)
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirname = os.path.basename(dirpath)
        if dirname in skip_dirs:
            # skip
            continue
        for filename in filenames:
            if filename.endswith('.valid.json'):
                continue
            Processor(dirpath, filename).execute()


if __name__ == '__main__':
    main()