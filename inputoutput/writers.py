import csv
import json
import os

from inputoutput.readers import csv_read


class Writer:
    def __init__(self, dir_path, base_filename, write_every=10000, clear_output_dir=False):
        self.dir_path = dir_path
        self.base_filename = base_filename
        self.write_every = write_every
        self.item_buffer = []
        self.file_item_count = 0
        self.file_count = 0
        self.i = 0
        if clear_output_dir:
            clean_output_dir(self.dir_path)
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

    def write(self, item):
        self.item_buffer.append(item)
        self.file_item_count += 1
        if self.file_item_count >= self.write_every:
            try:
                self.write_to_file()
            except Exception as e:
                print("Error: could not write to %s %s" % (self.get_file_path(), e))
                pass

    def write_to_file(self):
        filename = self.get_file_path()
        json.dump(self.item_buffer, open(filename, 'w+', encoding='utf8'))
        print("Info: written %d items to %s" % (len(self.item_buffer), filename))
        self.file_count += 1
        self.i += self.file_item_count
        self.item_buffer = []
        self.file_item_count = 0

    def get_file_path(self):
        return os.path.join(self.dir_path, '%s_%s.json' % (self.base_filename, self.file_count))

    def close(self):
        self.write_to_file()


class CSVWriter(Writer):
    def __init__(self, dir_path, base_filename, columns, write_every=20000, clear_output_dir=False):
        super().__init__(dir_path, base_filename, write_every, clear_output_dir)
        self.columns = columns

    def write_to_file(self):
        filename = self.get_file_path()
        csv_write(filename, self.item_buffer, self.columns)
        self.file_count += 1
        self.item_buffer = []
        self.file_item_count = 0

    def get_file_path(self):
        return os.path.join(self.dir_path, '%s_%s.csv' % (self.base_filename, self.file_count))


class CSVAppendWriter(CSVWriter):
    def __init__(self, dir_path, base_filename, filename_counter, columns, write_every=20000, clear_output_dir=False):
        super().__init__(dir_path, base_filename, columns, write_every, clear_output_dir)
        old = csv_read(base_filename + ('_%d' % filename_counter + '.csv'))
        self.item_buffer = [0 for i in range(1, len(old))]

    def write_to_file(self):
        filepath = os.path.join(self.dir_path, '%s_%s_%s.csv' % (self.base_filename, self.file_count))
        csv_write_append(filepath, self.item_buffer, self.columns)
        self.file_count += 1
        self.item_buffer = []
        self.file_item_count = 0

    def get_file_path(self):
        pass


def csv_write(filepath, items, columns=None):
    if len(items) == 0:
        print("Warning: there are no items to write to %s" % filepath)
        return
    if columns is None:
        columns = [col for col in items[0].keys()]
        print("Info: writing csv with columns %s" % columns)
    if not filepath.endswith('.csv'):
        print("Warning: writing csv to file without .csv extension")
    written_items = []
    with open(filepath, 'w+', encoding='utf8', newline='\n') as fp:
        writer = csv.writer(fp, delimiter=';', dialect='excel')
        writer.writerow(columns)
        for item in items:
            if not type({}) is dict:
                # TODO: when this is not a dict something goes wrong!
                raise Exception("Coul not write: %s" % item)
            out_items = {}
            for key in columns:
                if key in item and item[key] is not None:
                    i = item[key]
                    if type(i) is str:
                        i = i.replace('\n', '')
                    out_items[key] = i
            writer.writerow([out_items[col] for col in columns])
            written_items.append(out_items)
    print("Info: %d items written to %s" % (len(items), filepath))
    return written_items


def csv_write_append(filepath, items, columns):
    if len(items) == 0:
        print("Warning: there are no items to write to %s" % filepath)
        return
    if not filepath.endswith('.csv'):
        print("Warning: writing csv to file without .csv extension")
    written_items = []
    with open(filepath, 'a', encoding='utf8', newline='\n') as fp:
        writer = csv.writer(fp, delimiter=';', dialect='excel')
        for item in items:
            if not type({}) is dict:
                # TODO: when this is not a dict something goes wrong!
                raise Exception("Coul not write: %s" % item)
            out_item = {key: (item[key] if (key in item and item[key] is not None) else '') for key in columns}
            writer.writerow([out_item[col] for col in columns])
            written_items.append(out_item)
    print("Info: %d items written to %s" % (len(items), filepath))
    return written_items


def clean_output_dir(dir, filename_postfix=''):
    # Delete previous
    if not os.path.exists(dir):
        os.makedirs(dir)
        return
    for f in os.listdir(dir):
        if f.endswith(filename_postfix):
            old_filepath = os.path.join(dir, f)
            print("removing %s" % old_filepath)
            os.remove(old_filepath)