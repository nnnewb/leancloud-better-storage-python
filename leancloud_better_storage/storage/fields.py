from leancloud_better_storage.storage.query import Condition, ConditionOperator
from leancloud_better_storage.storage.order import OrderBy, ResultElementOrder

FIELD_AVAILABLE_TYPES = [int, float, str, list, dict, None]


class undefined:
    ...


class Field(object):

    @property
    def field_name(self):
        return self._field_name

    @property
    def nullable(self):
        return self._field_nullable

    @property
    def field_type(self):
        return self._field_type

    @property
    def model(self):
        return self._model

    @property
    def default(self):
        return self._field_default

    @property
    def desc(self):
        return OrderBy(ResultElementOrder.Descending, self)

    @property
    def asc(self):
        return OrderBy(ResultElementOrder.Ascending, self)

    def __init__(self, name=None, nullable=True, default=undefined, type_=None):
        self._model = None
        self._field_name = name
        self._field_nullable = nullable
        self._field_default = default
        self._field_type = type_
        if self._field_type not in FIELD_AVAILABLE_TYPES:
            raise ValueError('required field type {0} not available!'.format(repr(self._field_type)))

    def __eq__(self, other):
        return Condition(self, ConditionOperator.Equal, other)

    def __ne__(self, other):
        return Condition(self, ConditionOperator.NotEqual, other)

    def __lt__(self, other):
        return Condition(self, ConditionOperator.LessThan, other)

    def __le__(self, other):
        return Condition(self, ConditionOperator.LessThanOrEqualTo, other)

    def __ge__(self, other):
        return Condition(self, ConditionOperator.GreaterThanOrEqualTo, other)

    def __gt__(self, other):
        return Condition(self, ConditionOperator.GreaterThan, other)

    def in_(self, other):
        return Condition(self, ConditionOperator.ContainedIn, other)

    def contains(self, sub):
        return Condition(self, ConditionOperator.Contains, sub)

    def regex(self, pattern):
        return Condition(self, ConditionOperator.Regex, pattern)

    def startswith(self, pattern):
        return Condition(self, ConditionOperator.StartsWith, pattern)

    def __get__(self, instance, owner):
        if instance:
            return instance.lc_object.get(self.field_name)
        return self

    def __set__(self, instance, value):
        instance.lc_object.set(self.field_name, value)

    # question: any behavior when user say wanna to delete a field ?
