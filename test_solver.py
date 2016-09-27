from unittest import TestCase

from my_script import similarity_strings


class TestSolver(TestCase):
    def test_similarity_strings(self):
        assert similarity_strings("", "") == 1
        assert similarity_strings("test1", "test1") == 1
        assert similarity_strings("300", "-20") == 0
