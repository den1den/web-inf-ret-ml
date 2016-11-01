
class TUser(dict):
    def __init__(self, iterable=None, **kwargs):
        super().__init__(iterable, **kwargs)
        self.id = int(self['id'])

    def __str__(self, *args, **kwargs):
       return str(self['id'])