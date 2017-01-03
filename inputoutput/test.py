import os
from unittest import TestCase

from config.config import PROJECT_DIR
from inputoutput.readers import InputReader


class TestReader(TestCase):
    def test_os_walk(self):
        r = InputReader(os.path.join(PROJECT_DIR, 'inputoutput', 'split_files_script', 'test_3_files'))
        _next_file = r._next_file()
        assert _next_file == '1.txt', _next_file
        _next_file = r._next_file()
        assert _next_file == '2.txt', _next_file
        _next_file = r._next_file()
        assert _next_file == '3.txt', _next_file
        _next_file = r._next_file()
        assert r._next_file() is None, _next_file

    def test_os_walk_prefix(self):
        r = InputReader(os.path.join(PROJECT_DIR, 'inputoutput', 'split_files_script', 'test_3_files'), filename_prefix='2')
        _next_file = r._next_file()
        assert _next_file == '2.txt', _next_file
        _next_file = r._next_file()
        assert r._next_file() is None, _next_file

    def test_os_walk_offset(self):
        r = InputReader(os.path.join(PROJECT_DIR, 'inputoutput', 'split_files_script', 'test_3_files'), file_offset=1)
        _next_file = r._next_file()
        assert _next_file == '2.txt', _next_file
        _next_file = r._next_file()
        assert _next_file == '3.txt', _next_file
        _next_file = r._next_file()
        assert r._next_file() is None, _next_file
