
class TUser(dict):
    def __init__(self, iterable=None, **kwargs):
        super().__init__(iterable, **kwargs)
        self.id = int(self['userid'])

    def __str__(self, *args, **kwargs):
       return str(self['userid'])