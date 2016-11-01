from unittest import TestCase

from features.term_frequency import write_tf_to_file, get_idf_map


class TestWriteTfToFile(TestCase):
    def test_write_tf_to_file(self):
        write_tf_to_file()
        tf = get_idf_map()
