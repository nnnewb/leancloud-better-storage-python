from enum import Enum

import leancloud

from leancloud_better_storage.storage.pages import Pages
from leancloud_better_storage.storage.err import LeanCloudErrorCode
from leancloud_better_storage.storage.order import ResultElementOrder


class ConditionOperator(Enum):
    Equal = '=='
    NotEqual = '!='
    GreaterThan = '>'
    GreaterThanOrEqualTo = '>='
    LessThan = '<'
    LessThanOrEqualTo = '<='
    Contains = 'in'


class Condition(object):
    operator_mapping = {
        ConditionOperator.Equal: lambda q, l, r: q.equal_to(l, r),
        ConditionOperator.GreaterThan: lambda q, l, r: q.greater_than(l, r),
        ConditionOperator.GreaterThanOrEqualTo: lambda q, l, r: q.greater_than_or_equal_to(l, r),
        ConditionOperator.LessThan: lambda q, l, r: q.less_than(l, r),
        ConditionOperator.LessThanOrEqualTo: lambda q, l, r: q.less_than_or_equal_to(l, r),
        ConditionOperator.NotEqual: lambda q, l, r: q.not_equal_to(l, r),
        ConditionOperator.Contains: lambda q, l, r: q.contains(l, r),
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
        return query


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
            cur = cur._prev.query
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
        :type prev: leancloud_better_storage.storage.query.QueryLink
        :param next_: next linked query
        :type next_: leancloud_better_storage.storage.query.QueryLink
        """
        self._model = model
        self._prev = prev
        self._next = next_
        self._conditions = []
        self._result_limit = 100
        self._skip_elements = 0
        self._order_by_elements = []

    def build_query(self, _keep_going__=False):
        """ build leancloud query. """
        cur = self._first if _keep_going__ is False else self
        queries = [*map(lambda cond: cond.apply(leancloud.Query(self._model.__lc_cls__)), cur._conditions)]
        if len(queries) >= 2:
            query = leancloud.Query.and_(*queries)
        elif len(queries) >= 1:
            query, = queries
        else:
            query = leancloud.Query(self._model.__lc_cls__)

        if cur._next is not None:
            if cur._next.relation == QueryLinkRelation.RelationAnd:
                query = leancloud.Query.and_(query, cur._next.query.build_query(_keep_going__=True))
            elif cur._next.relation == QueryLinkRelation.RelationOr:
                query = leancloud.Query.or_(query, cur._next.query.build_query(_keep_going__=True))

        for order_by in self._order_by_elements:
            if order_by.order == ResultElementOrder.Ascending:
                query.add_ascending(order_by.field.field_name)
            elif order_by.order == ResultElementOrder.Descending:
                query.add_descending(order_by.field.field_name)

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

    def order_by(self, *order_by):
        self._validate_fields_belong_to_self(*map(lambda o: o.field, order_by))
        self._order_by_elements.extend(order_by)
        return self

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
        curr_query = self._last
        next_query = Query(self._model, curr_query)
        prev_link = QueryLink(curr_query, rel)
        next_query._prev = prev_link
        next_link = QueryLink(next_query, rel)
        curr_query._next = next_link

        return next_query

    def _validate_fields_belong_to_self(self, *fields):
        for field in fields:
            if field.model.__lc_cls__ != self._model.__lc_cls__:
                return False
        return True
