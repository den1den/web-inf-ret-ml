import math
import sys
from unittest import TestCase

import os

from config import config
from config.config import PCLOUD_BUFFER_DIR
from inputoutput.input import get_tweets, get_tusers, get_articles, csv_write, csv_read


class TestIOMethods(TestCase):
    def test_item_offset(self):
        i10 = read_json_array_from_files(lambda l: l, config.PCLOUD_DIR, item_count=10, item_offset=0)
        i5 = read_json_array_from_files(lambda l: l, config.PCLOUD_DIR, item_count=5, item_offset=0)
        i5_2 = read_json_array_from_files(lambda l: l, config.PCLOUD_DIR, item_count=5, item_offset=5)
        assert i10 == i5 + i5_2

    def test_file_offset(self):
        i10 = read_json_array_from_files(lambda l: l, config.PCLOUD_DIR, file_count=2, file_offset=10)
        i5 = read_json_array_from_files(lambda l: l, config.PCLOUD_DIR, file_count=1, file_offset=10)
        i5_2 = read_json_array_from_files(lambda l: l, config.PCLOUD_DIR, file_count=1, file_offset=11)
        assert i10 == i5 + i5_2

    def test_csv_writer(self):
        tmpfile = os.path.join(config.PROJECT_DIR, 'tmp.csv')
        data = [{'a': None, 'b': '489198'}, {'a': 'A\n\n\n2', 'b': 'B'+os.linesep+'2'}, {'a': 'A3', 'b': 'B3'}]
        write_data = csv_write(tmpfile, data, ['a', 'b'])
        read_data = csv_read(tmpfile, ['a', 'b'])
        print(write_data)
        print(read_data)
        assert read_data == write_data
        write_data = csv_write(tmpfile, write_data, ['a'])
        read_data = csv_read(tmpfile, ['a'])
        print(write_data)
        print(read_data)
        assert read_data == write_data
        write_data = csv_write(tmpfile, data, ['a', 'b', 'x'])
        read_data = csv_read(tmpfile, ['a', 'b', 'x'])
        print(write_data)
        print(read_data)
        assert read_data == write_data
        write_data = csv_write(tmpfile, data)
        read_data = csv_read(tmpfile)
        print(write_data)
        print(read_data)
        assert read_data == write_data
        os.remove(tmpfile)


class TestTweetsInput(TestCase):
    def test_valid_json(self):
        read_json_array_from_files(lambda d: d, os.path.join(PCLOUD_BUFFER_DIR, 'raw-tweets'), filename_prefix='20161023')

    def test_unique_tweet_ids(self):
        data = get_tweets(filename_prefix='')
        self.unique_ids_test(data)

    def test_unique_tuser_ids(self):
        data = get_tusers(filename_prefix='')
        self.unique_ids_test(data)

    def test_unique_get_articles(self):
        data = get_articles(filename_prefix='')
        self.unique_ids_test(data)

    def unique_ids_test(self, data_array, print_data=True, id_tag='id'):
        format_N = "[%0" + str(math.ceil(math.log(len(data_array) + 1, 10))) + "d]"
        format_str = format_N + " %020d: %s"

        seen_ids = set()
        id_printed = set()

        duplicate_indices = 0
        same_index_diff_text = 0

        sys.stdout.flush()
        for i in range(0, len(data_array)):
            #assert hasattr(data_array[i], id_tag), "No ID is set on this object, so no id to check!"
            data_id = data_array[i][id_tag]
            if data_id in seen_ids:
                # Duplicate found
                if data_id not in id_printed:
                    # Print all datas with same id
                    this_id_n = 0
                    this_id_strings = set()

                    # Find first data:
                    for j in range(0, i):
                        if data_array[j][id_tag] == data_id:
                            this_id_n += 1
                            this_id_strings.add(str(data_array[j]))
                            if print_data: print(format_str % (j, data_array[j][id_tag], data_array[j]))
                            break
                        elif j == i - 1:
                            raise AssertionError("Original not found")

                    # Find all consecutive data's with same data_id, O(n^2)
                    for j in range(i, len(data_array)):
                        if data_array[j][id_tag] == data_id:
                            if print_data: print(format_str % (j, data_array[j][id_tag], data_array[j]))
                            this_id_n += 1
                            this_id_strings.add(str(data_array[j]))
                    if print_data: print("\n----------------------------------------------------------\n")
                    sys.stdout.flush()

                    same_index_diff_text += len(this_id_strings) - 1
                    duplicate_indices += this_id_n
                    id_printed.add(data_id)
            else:
                seen_ids.add(data_array[i][id_tag])

            # Displays process halfway:
            # if i % (1 << 10) == 0:
            #     print("processed: %s / %s" % (i, len(data_array)))

        print("duplicate_indices: %s, same_index_diff_text: %s, data_array: %s"
              % (duplicate_indices,
                 same_index_diff_text,
                 len(data_array))
              )
        if len(id_printed) >  0:
            print("Actual indices: %s" % id_printed)
            assert False, "%d duplicates found in %d entries" % (duplicate_indices, len(data_array), )





