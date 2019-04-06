class Cursor:
    def __init__(self, cursor, model):
        self._cursor = cursor
        self._cursor_iter = iter(self._cursor)
        self._cls = model

    @property
    def lc_cursor(self):
        return self._cursor

    def __iter__(self):
        return self

    def __next__(self):
        return self._cls(next(self._cursor_iter))
