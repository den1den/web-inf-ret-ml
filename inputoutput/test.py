from unittest import TestCase

from inputoutput.input import FileNameRecoginizer


class TestFileNameRecoginizer(TestCase):
    def test_regex(self):
        regex = FileNameRecoginizer.regex
        m = regex.match('12321321__kjfdosdjaoi.json')
        assert not not m
        assert m.group(1) == '12321321'
