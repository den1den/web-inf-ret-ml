import csv
import json
import os
import time


def read_json_array_from_files(to_obj_function, dir_path, **kwargs):
    raise Exception("Depricated, use: reader = InputReader(); objs = reader.read_all()")


class InputReader:
    """
    Loads in json arrays from a directory recursively
    :param d2o: function from dict -> object to sto
    :param dir_path: abs path to directory to read from
    :param self.item_count: number of items to read in total
    :param self.item_offset: number of object to skip in total
    :param self.file_count: number of files to read
    :param self.file_offset: starting index of the file to read
    :param filename_prefix: filter on the filenames
    :param self.filename_postfix: filter on the filenames
    :param self.dir_name_prefix:
    :param file_alternation:
    :param file_alternation_index:
    :param give_filename_to_d2o: provide extra argument `filename` to d2o function
    """

    def __init__(self, dir_path, item_offset=0, file_offset=0,
                 filename_prefix='', filename_postfix='.json',
                 dir_name_prefix='',
                 file_alternation=1, file_alternation_index=0):
        self.item_offset = item_offset
        self.file_offset = file_offset
        self.filename_prefix = filename_prefix
        self.filename_postfix = filename_postfix
        self.dir_name_prefix = dir_name_prefix
        self.file_alternation = file_alternation
        self.file_alternation_index = file_alternation_index
        self.dir_path = dir_path
        self.os_walk_iter = iter(os.walk(dir_path))

        self.filecounter = 0  # File counter of files read
        self.nxt_index = 0  # Index of next item to be returned in the raw_items array
        self.raw_items = []  # Last read items
        self.i = 0  # Number of items read so far

    def filename_match(self, filename):
        lowercase_filename = filename.lower()
        if not lowercase_filename.endswith(self.filename_postfix):
            # skip non matching files
            return False
        if not lowercase_filename.startswith(self.filename_prefix):
            # skip non matching files
            return False
        return True


    def read_next_file(self):
        """
        Reads in the next file, or returns False when end is reached
        """
        while True:
            filename = self._next_file()
            if filename is None:
                break

            if not self.filename_match(filename):
                continue

            # file matches
            self.filecounter += 1
            if self.filecounter < self.file_offset:
                # skip file
                continue

            # New filename found
            self.current_file = os.path.join(self.dir_path, filename)
            try:
                # Read file
                self.raw_items = self.read_file()
                self.nxt_index = 0
                return True
            except Exception as e:
                print("Error: could not read_file file %s %s" % (self.current_file, e))
                continue
        return False

    def read_file(self):
        """
        Process the current file
        """
        with open(self.current_file, encoding='utf8') as data_file:
            raw_data = json.load(data_file)
        # print("Info: Input file read: %s" % self.current_file)
        return raw_data

    def __iter__(self):
        return self

    def __next__(self):
        while self.nxt_index == len(self.raw_items):
            if self.read_next_file():
                pass
            else:
                raise StopIteration()
        nxt = self.raw_items[self.nxt_index]
        self.nxt_index += 1
        self.i += 1
        return nxt

    def read_all(self, function=lambda x: x, item_count=None, item_offset=0):
        print(
            "Info: read all entries (with entry offset %d) from all `%s*%s` files (with file offset %d) from `%s`" %
            (self.item_offset, self.filename_prefix, self.filename_postfix, self.file_offset, self.dir_path)
        )

        t0 = time.time()
        self.items = []
        i = 0
        for item in self:
            i += 1
            if i < item_offset:
                continue
            try:
                fi = function(item)
                self.items.append(fi)
            except Exception as e:
                print("Error: could not apply function to file %s:%d %s" % (self.current_file, self.i, e))
                pass
            if item_count is not None and len(self.items) >= item_count:
                break
        t1 = time.time()
        duration = t1 - t0

        if item_count is not None and len(self.items) != item_count:
            raise AssertionError("Error: could only read %d of %d entries" % (len(self.items), item_count))

        if self.filecounter == 0:
            print("Info: read %d entries read from %d files" % (len(self.items), self.filecounter))
        else:
            print(
                "Info: read %d entries read from %d files (%.2f sec per file, %.0f seconds in total)"
                % (len(self.items), self.filecounter, duration / self.filecounter, duration)
            )
        return self.items

    def __str__(self, *args, **kwargs):
        return "file: %s at entry %d" % (self.current_file, self.i)

    fn_iter = None

    def _next_file(self):
        if self.fn_iter is not None:
            try:
                return next(self.fn_iter)
            except StopIteration:
                pass
        try:
            self.dir_path, dn, fn = next(self.os_walk_iter)
            lowercase_dir_name = os.path.basename(self.dir_path)
            if not lowercase_dir_name.startswith(self.dir_name_prefix):
                # skip non matching dirs
                return self._next_file()
            self.fn_iter = iter(fn)
            return self._next_file()
        except StopIteration:
            return None


class CSVInputReader(InputReader):
    def __init__(self, dir_path, columns, item_offset=0, file_offset=0, filename_prefix='', filename_postfix='.csv',
                 dir_name_prefix='', file_alternation=1, file_alternation_index=0, delimiter=';'):
        super().__init__(dir_path, item_offset, file_offset, filename_prefix, filename_postfix, dir_name_prefix,
                         file_alternation, file_alternation_index)
        self.columns = columns
        self.delimiter = delimiter

    def read_file(self):
        raw_data = csv_read(self.current_file, self.columns, delimiter=self.delimiter)
        # print("Info: Input file read: %s" % self.current_file)
        return raw_data


def csv_read(filepath, column=None, delimiter=';'):
    """
    Warning: will not read correct data type
    """
    if not filepath.endswith('.csv'):
        print("Warning: writing csv to file without .csv extension")
    items = []
    if not os.path.exists(filepath):
        print("Warning: file not found, could not read from %s" % filepath)
        return items
    with open(filepath, 'r', encoding='utf8', newline='\n') as fp:
        data = csv.reader(fp, delimiter=delimiter)
        if column is None:
            header = [column for column in next(data)]
        else:
            header = [column for column in next(data) if column in column]
        for line, item in enumerate(data):
            items.append({header[i]: value for i, value in enumerate(item)})
    print("Info: %d items read from %s" % (len(items), filepath))
    return items


class JSONInputReader(InputReader):
    def __init__(self, dir_path, item_offset=0, file_offset=0, filename_prefix='', filename_postfix='.json',
                 dir_name_prefix='', file_alternation=1, file_alternation_index=0, delimiter=';'):
        super().__init__(dir_path, item_offset, file_offset, filename_prefix, filename_postfix, dir_name_prefix,
                 file_alternation, file_alternation_index)
        self.delimiter = delimiter

    def read_file(self):
        raw_data = json_read(self.current_file, headers = ['url', 'date', 'article'])
        # print("Info: Input file read: %s" % self.current_file)
        return raw_data


def json_read(filepath, headers = None):
    """
    Warning: will not read correct data type
    """
    if not filepath.endswith('.json'):
        print("Warning: writing json to file without .json extension")
    items = []
    if not os.path.exists(filepath):
        print("Warning: file not found, could not read from %s" % filepath)
        return items
    with open(filepath) as fp:
        data = json.load(fp)
        if headers is None:
            headers = ['url', 'date', 'article']
        for line in data:
            for i in range(len(headers)):
                items.append({headers[i]: value for i, value in enumerate(line)})
    print("Info: %d items read from %s" % (len(items), filepath))
    return items
