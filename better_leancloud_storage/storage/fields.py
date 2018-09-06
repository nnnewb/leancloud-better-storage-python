from better_leancloud_storage.storage.query import Condition, ConditionOperator

FIELD_AVAILABLE_TYPES = [int, float, str, list, dict]


class Field(object):

    @property
    def field_name(self):
        return self._field_name

    @property
    def field_nullable(self):
        return self._field_nullable

    @property
    def field_type(self):
        return self._field_type

    @property
    def model(self):
        return self._model

    def __init__(self, name=None, nullable=True, default=None, type_=None):
        self._model = None
        self._field_name = name
        self._field_nullable = nullable
        self._field_default = default
        self._field_type = type_

    def __eq__(self, other):
        return Condition(self, ConditionOperator.Equal, other)

    def __lt__(self, other):
        return Condition(self, ConditionOperator.LessThan, other)

    def __le__(self, other):
        return Condition(self, ConditionOperator.LessThanOrEqualTo, other)

    def __ge__(self, other):
        return Condition(self, ConditionOperator.GreaterThanOrEqualTo, other)

    def __gt__(self, other):
        return Condition(self, ConditionOperator.GreaterThan, other)
