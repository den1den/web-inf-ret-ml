class HasKeywords:

    def get_unique_word_count(self):
        return len(set(self.get_keywords()))

    def get_duplicate_count(self):
        return len(self.get_keywords()) - self.get_unique_word_count()

    def get_keyword_frequencies(self):
        f = {}
        for word in self.get_keywords():
            if word in f:
                f[word] += 1
            else:
                f[word] = 1
        return f