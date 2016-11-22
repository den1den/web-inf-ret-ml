from unittest import TestCase

from preprocessing.spell_checker import known_correct


class TestSpellChecker(TestCase):
    def test_correct(self):
        print(known_correct('RT'))
        print(known_correct('I'))
        print(known_correct('I am'))
        print(known_correct('7460839'))
        print(known_correct('fniudslo'))
        print(known_correct('books'))
        print(known_correct('flawless'))
        print(known_correct('internet'))
        print(known_correct('whatsapp'))
        print(known_correct('water'))
        print(known_correct('wAter'))
        print(known_correct('WATER'))
        print(known_correct('Tweet'))
        print(known_correct('tweet'))
        print(known_correct('retweer'))
        print(known_correct('hashtag'))
