from enum import Enum


class ResultElementOrder(Enum):
    Ascending = 'ascending'
    Descending = 'descending'


class OrderBy:

    def __init__(self, order, field):
        self._order = order
        self._field = field

    @property
    def order(self):
        return self._order

    @property
    def field(self):
        return self._field
