class Cursor:
    def __init__(self, cursor, model):
        self._cursor = cursor
        self._cls = model

    @property
    def lc_cursor(self):
        return self._cursor

    def __iter__(self):
        return self

    def __next__(self):
        n = next(self._cursor)
        yield self._cls(n)
