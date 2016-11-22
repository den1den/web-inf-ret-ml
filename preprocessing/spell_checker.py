# needs: import nltk; nltk.download();
# d gutenberg
# d webtext
# d nps_chat
import collections

import nltk.corpus as corpus

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
        for f in corpus:
            model[f] += 1
    return model


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
        print("-> %s" % r)
        return 1
    r = known(edits1(word))
    if r:
        print("-> %s" % r)
        return 1
    r = known_edits2(word)
    if r:
        print("-> %s" % r)
        return 1
    print("-> %s" % [])
    return 0
