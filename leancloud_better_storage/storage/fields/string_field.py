from .defaults import undefined
from .field import Field
from ..query import Condition, ConditionOperator


class StringField(Field):

    def __init__(self, name=None, nullable=True, default=undefined, max_length=None):
        super().__init__(name, nullable, default)
        self.max_length = max_length

    def __set__(self, instance, value):
        if self.max_length and len(value) > self.max_length:
            raise ValueError('string too long.')
        super(StringField, self).__set__(instance, value)

    def contains(self, sub):
        return Condition(self, ConditionOperator.Contains, sub)

    def regex(self, pattern):
        return Condition(self, ConditionOperator.Regex, pattern)

    def startswith(self, pattern):
        return Condition(self, ConditionOperator.StartsWith, pattern)
