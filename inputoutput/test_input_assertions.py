import math
from unittest import TestCase

import sys

from inputoutput.input import get_tweets, get_tusers, get_articles


class TestTweetsInput(TestCase):
    def test_unique_tweet_ids(self):
        data = get_tweets(filename_prefix='')
        self.unique_ids_test(data)

    def test_unique_tuser_ids(self):
        data = get_tusers(10000, filename_prefix='')
        self.unique_ids_test(data)

    def test_unique_get_articles(self):
        data = get_articles(894)
        self.unique_ids_test(data, id_tag='ArticleID')

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





