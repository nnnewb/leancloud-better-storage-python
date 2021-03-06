from copy import copy, deepcopy
from enum import Enum

import leancloud

from leancloud_better_storage.storage.cursor import Cursor
from leancloud_better_storage.storage.err import LeanCloudErrorCode
from leancloud_better_storage.storage.order import ResultElementOrder
from leancloud_better_storage.storage.pages import Pages


class ConditionOperator(Enum):
    Equal = '=='
    NotEqual = '!='
    GreaterThan = '>'
    GreaterThanOrEqualTo = '>='
    LessThan = '<'
    LessThanOrEqualTo = '<='
    StartsWith = 'startswith'  # query.startswith
    Contains = 'in'  # query.contains
    ContainedIn = 'in_'  # query.contained_in
    Regex = 'regex'  # query.matched
    Near = 'near'  # query.near
    WithinKilometers = 'within_kilometers'  # query.within_kilometers


class Condition(object):
    operator_mapping = {
        ConditionOperator.Equal: lambda q, l, r: q.equal_to(l, r),
        ConditionOperator.GreaterThan: lambda q, l, r: q.greater_than(l, r),
        ConditionOperator.GreaterThanOrEqualTo: lambda q, l, r: q.greater_than_or_equal_to(l, r),
        ConditionOperator.LessThan: lambda q, l, r: q.less_than(l, r),
        ConditionOperator.LessThanOrEqualTo: lambda q, l, r: q.less_than_or_equal_to(l, r),
        ConditionOperator.NotEqual: lambda q, l, r: q.not_equal_to(l, r),
        ConditionOperator.Contains: lambda q, l, r: q.contains(l, r),
        ConditionOperator.ContainedIn: lambda q, l, r: q.contained_in(l, r),
        ConditionOperator.Regex: lambda q, l, r: q.matched(l, r),
        ConditionOperator.StartsWith: lambda q, l, r: q.startswith(l, r),
        ConditionOperator.Near: lambda q, l, r: q.near(l, r),
        ConditionOperator.WithinKilometers: lambda q, l, r: q.within_kilometers(l, *r),
    }

    def __init__(self, operand_left, operator, operand_right):
        self._operand_left = operand_left
        self._operand_right = operand_right
        self._operator = operator

    @property
    def operand_left(self):
        return self._operand_left

    @property
    def operand_right(self):
        return self._operand_right

    @property
    def operator(self):
        return self._operator

    def apply(self, query):
        self.operator_mapping[self.operator](query, self.operand_left.field_name, self.operand_right)
        return query


class QueryLogicalError(Exception):
    pass


class Query(object):
    """ query class """

    class State(Enum):
        BEGIN = -1
        COND = 0
        AND = 1
        OR = 2

    def __init__(self, model, **kwargs):
        self._model = model
        self._state = kwargs.get('_state', self.State.BEGIN)
        self._query = leancloud.Query(self._model.__lc_cls__)
        self._last_logical_op = None

    def _merge_conditions(self, *conditions):
        if len(conditions) >= 2:
            q = leancloud.Query.and_(*(cond.apply(leancloud.Query(self._model.__lc_cls__)) for cond in conditions))
        else:
            q = conditions[0].apply(leancloud.Query(self._model.__lc_cls__))

        return q

    @property
    def _logical_fn(self):
        if self._last_logical_op in ('and', None):
            return leancloud.Query.and_
        else:
            return leancloud.Query.or_

    def filter(self, *conditions):
        """ select data with custom conditions. """
        self._state = self.State.COND
        query = self._merge_conditions(*conditions)
        self._query = self._logical_fn(self._query, query)
        self._last_logical_op = None

        return self

    def filter_by(self, **kwargs):
        """ select data with equation conditions. """
        self._state = self.State.COND

        input_key_set = set(kwargs.keys())
        fields_key_set = set(self._model.__fields__.keys())

        if not input_key_set.issubset(fields_key_set):
            raise KeyError('Unknown fields {0}'.format(input_key_set - fields_key_set))

        conditions = [self._model.__fields__[key] == val for key, val in kwargs.items()]
        self._query = self._logical_fn(self._query, self._merge_conditions(*conditions))
        self._last_logical_op = None

        return self

    def and_(self):
        if self._state not in (self.State.BEGIN, self.State.COND):
            raise QueryLogicalError('Should not connect two logical operation.')
        self._state = self.State.AND
        self._last_logical_op = 'and'

        return self

    def or_(self):
        if self._state not in (self.State.BEGIN, self.State.COND):
            raise QueryLogicalError('Should not connect two logical operation.')
        self._state = self.State.OR
        self._last_logical_op = 'or'

        return self

    def includes(self, *args):
        for field in args:
            from leancloud_better_storage.storage.fields import Field
            if not isinstance(field, Field):
                raise ValueError('Unexpected argument {}, '.format(repr(field)) +
                                 'includes(...) only take Field instance as argument.')
            self._query.include(*(field.field_name for field in args))
        return self

    def skip(self, n):
        self._query.skip(n)
        return self

    def limit(self, n):
        self._query.limit(n)
        return self

    def order_by(self, *args):
        for arg in args:
            if arg.order == ResultElementOrder.Ascending:
                self._query.add_ascending(arg.field.field_name)
            elif arg.order == ResultElementOrder.Descending:
                self._query.add_descending(arg.field.field_name)

        return self

    def build_query(self):
        """ 与之前的Query 的兼容性方案 """
        return deepcopy(self._query)

    @property
    def leancloud_query(self):
        return self._query

    def find(self, skip=None, limit=None):
        # don't change the origin query object
        q = copy(self._query)

        if skip:
            q.skip(skip)
        if limit:
            q.limit(limit)

        try:
            return tuple(map(self._model, q.find()))
        except leancloud.LeanCloudError as exc:
            if exc.code == LeanCloudErrorCode.ClassOrObjectNotExists.value:
                return []
            raise

    def scan(self, batch_size=None, scan_key=None):
        return Cursor(self._query.scan(batch_size, scan_key), self._model)

    def first(self):
        try:
            return self._model(self._query.first())
        except leancloud.LeanCloudError as exc:
            if exc.code == LeanCloudErrorCode.ClassOrObjectNotExists.ClassOrObjectNotExists.value:
                return None
            raise

    def count(self):
        try:
            return self._query.count()
        except leancloud.LeanCloudError as exc:
            if exc.code == LeanCloudErrorCode.ClassOrObjectNotExists.value:
                return 0
            raise

    def paginate(self, page, size):
        return Pages(self, page, size)
