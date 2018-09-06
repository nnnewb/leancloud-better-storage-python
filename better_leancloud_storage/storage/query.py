from enum import Enum

import leancloud

from better_leancloud_storage.storage.pages import Pages
from .err import LeanCloudErrorCode


class ConditionOperator(Enum):
    Equal = '=='
    GreaterThan = '>'
    GreaterThanOrEqualTo = '>='
    LessThan = '<'
    LessThanOrEqualTo = '<='


class Condition(object):
    operator_mapping = {
        ConditionOperator.Equal: lambda q, l, r: q.equal_to(l, r),
        ConditionOperator.GreaterThan: lambda q, l, r: q.greater_than(l, r),
        ConditionOperator.GreaterThanOrEqualTo: lambda q, l, r: q.greater_than_or_equal_to(l, r),
        ConditionOperator.LessThan: lambda q, l, r: q.less_than(l, r),
        ConditionOperator.LessThanOrEqualTo: lambda q, l, r: q.less_than_or_equal_to(l, r)
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
        self.operator_mapping[self._operator](query, self._operand_left.field_name, self._operand_right)


class QueryLinkRelation(Enum):
    """ logic relation between two query """
    RelationAnd = 'and'
    RelationOr = 'or'


class QueryLink(object):
    """
    linked query pointer with relation information between queries.
    """

    def __init__(self, query, relation):
        self.query = query
        self.relation = relation


class Query(object):
    """ query class """

    @property
    def _first(self):
        through_nodes_set = set()
        cur = self
        while cur._prev is not None:
            through_nodes_set.add(cur)
            cur = cur._prev
            if cur in through_nodes_set:
                raise ValueError('Found loop inside linked query!')
        return cur

    @property
    def _last(self):
        through_nodes_set = set()
        cur = self
        while cur._next is not None:
            through_nodes_set.add(cur)
            cur = cur._next
            if cur in through_nodes_set:
                raise ValueError('Found loop inside linked query!')
        return cur

    def __init__(self, model, prev=None, next_=None):
        """
        initializer of Query class

        data structure just like linked list, their is logical operation `and`/`or` between two query .

        :param model: storage model
        :type model: type
        :param prev: previous linked query
        :type prev: better_leancloud_storage.storage.query.QueryLink
        :param next_: next linked query
        :type next_: better_leancloud_storage.storage.query.QueryLink
        """
        self._model = model
        self._prev = prev
        self._next = next_
        self._conditions = []
        self._result_limit = 100
        self._skip_elements = 0

    def build_query(self, __keep_going=False):
        """ build leancloud query. """
        cur = self._first if __keep_going is False else self
        query = leancloud.Query(self._model.__lc_cls__)

        for condition in cur._conditions:
            condition.apply(query)

        if self._next is not None:
            if self._next.relation == QueryLinkRelation.RelationAnd:
                query = leancloud.Query.and_(query, cur._next.query.build_query(__keep_going=True))
            elif self._next.relation == QueryLinkRelation.RelationOr:
                query = leancloud.Query.or_(query, cur._next.query.build_query(__keep_going=True))

        query.skip(self._skip_elements)
        query.limit(self._result_limit)
        return query

    def filter(self, *conditions):
        """ select data with custom conditions. """
        self._conditions.extend(conditions)
        return self

    def filter_by(self, **kwargs):
        """ select data with equation conditions. """
        input_key_set = set(kwargs.keys())
        fields_key_set = set(self._model.__fields__.keys())

        if input_key_set.issubset(fields_key_set) is False:
            raise KeyError('Unknown fields {0}'.format(input_key_set - fields_key_set))

        self._conditions.extend([self._model.__fields__[key] == val for key, val in kwargs.items()])

        return self

    def and_(self):
        """ create new query and linked current query with and. """
        return self._build_next(QueryLinkRelation.RelationAnd)

    def or_(self):
        """ create new query and linked current query with or. """
        return self._build_next(QueryLinkRelation.RelationOr)

    def first(self):
        """ get first object match conditions. """
        q = self.build_query()
        try:
            return self._model(q.first())
        except leancloud.LeanCloudError as exc:
            if exc.code == LeanCloudErrorCode.ClassOrObjectNotExists.ClassOrObjectNotExists.value:
                return None
            raise

    def count(self):
        """ count elements. """
        q = self.build_query()
        try:
            return q.count()
        except leancloud.LeanCloudError as exc:
            if exc.code == LeanCloudErrorCode.ClassOrObjectNotExists.value:
                return 0
            raise

    def find(self, skip=0, limit=100):
        self._skip_elements = skip
        self._result_limit = limit
        q = self.build_query()

        try:
            return [
                self._model(obj)
                for obj in q.find()
            ]
        except leancloud.LeanCloudError as exc:
            if exc.code == LeanCloudErrorCode.ClassOrObjectNotExists.value:
                return []
            raise

    def paginate(self, page, size):
        """ paginate query result which is leancloud default and recommend behavior. """
        return Pages(self, page, size)

    def _build_next(self, rel):
        cur = self._last
        query = Query(self._model, cur)
        cur._next = QueryLink(query, rel)
        return query
