# needs: import nltk; nltk.download();
# d gutenberg
# d webtext
# d nps_chat
import collections

import nltk.corpus as corpus

from config.config import SPELLING

corpa = []


def _read_corpa():
    _read_corpus(corpus.gutenberg)
    _read_corpus(corpus.webtext)
    _read_corpus(corpus.nps_chat)


def _read_corpus(c):
    for f in c.fileids():
        corpa.append(c.words(f))


def train():
    model = collections.defaultdict(lambda: 1)
    for corpus in corpa:
        for w in corpus:
            model[w] += 1
    for w in ('Hillary', 'Trump', 'trump', 'hillary', 'RT', 'rt', 'clinton', 'Clinton',
        'Tweet',
        'tweet',
        'Twitter',
        'twitter',
        'retweet',
        'hashtag',
              ):
        model[w] += 1
    return model

if SPELLING:
    _read_corpa()
    NWORDS = train()
    alphabet = 'abcdefghijklmnopqrstuvwxyz'


def edits1(word):
    s = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [a + b[1:] for a, b in s if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in s if len(b) > 1]
    replaces = [a + c + b[1:] for a, b in s for c in alphabet if b]
    inserts = [a + c + b for a, b in s for c in alphabet]
    return set(deletes + transposes + replaces + inserts)


def known_edits2(word):
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in NWORDS)


def known(words):
    return set(w for w in words if w in NWORDS)


def correct(word):
    candidates = known([word]) or known(edits1(word)) or known_edits2(word) or [word]
    return max(candidates, key=NWORDS.get)


def known_correct(word):
    r = known([word])
    if r:
        return 0, r
    r = known(edits1(word))
    if r:
        return 1, r
    r = known_edits2(word)
    if r:
        return 2, r
    return 3, []
