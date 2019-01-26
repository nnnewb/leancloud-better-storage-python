import enum
from datetime import date, datetime
import leancloud

from leancloud_better_storage.storage.models import Model, Pointer
from leancloud_better_storage.storage.fields import Field
from leancloud_better_storage.storage.query import Condition, ConditionOperator


class DateField(Field):
    def to_python_value(self, value):
        if isinstance(value, datetime):
            return value.date()
        return value

    def to_leancloud_value(self, value):
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time())
        return value


class EnumField(Field):
    def __init__(self, enumInstance, **kwargs):
        self.enumInstance = enumInstance
        self.valueMapping = {
            i.value: i
            for i in enumInstance
        }
        super().__init__(**kwargs)

    def to_python_value(self, value):
        result = None
        if isinstance(value, str) and hasattr(self.enumInstance, value):
            result = getattr(self.enumInstance, value)
        else:
            result = self.valueMapping.get(value)
        if result is None:
            return self._field_default
        return result

    def to_leancloud_value(self, value):
        if isinstance(value, enum.Enum):
            return value.value
        return value


class NestField(Field):
    def __init__(self, ref, many=False, **kwargs):
        self._ref = ref
        self._many = many
        super().__init__(**kwargs)

    def get_model_class(self):
        if self._ref == 'self':
            return self._model
        elif isinstance(self._ref, Model):
            return self._ref
        elif self._ref in self._model.__class__.__classes__:
            return self._model.__class__.__classes__[self._ref]
        else:
            raise ValueError('Unknown model name `%s`' % self._ref)

    def to_lc_object(self, obj):
        if isinstance(obj, Model):
            return obj.lc_object
        if isinstance(obj, leancloud.Object):
            return obj
        if isinstance(obj, Pointer):
            return obj
        if obj is None:
            return obj
        raise TypeError('Expected leancloud.Object or leancloud_better_stroage.Model.')

    def __eq__(self, other):
        return Condition(self, ConditionOperator.Equal, self.to_lc_object(other))

    def __ne__(self, other):
        return Condition(self, ConditionOperator.NotEqual, self.to_lc_object(other))

    def __lt__(self, other):
        return Condition(self, ConditionOperator.LessThan, self.to_lc_object(other))

    def __le__(self, other):
        return Condition(self, ConditionOperator.LessThanOrEqualTo, self.to_lc_object(otherj))

    def __ge__(self, other):
        return Condition(self, ConditionOperator.GreaterThanOrEqualTo, self.to_lc_object(other))

    def __gt__(self, other):
        return Condition(self, ConditionOperator.GreaterThan, self.to_lc_object(other))

    def in_(self, other):
        other = [self.to_lc_object(i) for i in other]
        return Condition(self, ConditionOperator.ContainedIn, other)

    def to_python_value(self, value):
        cls = self.get_model_class()
        if self._many:
            return [cls(i) for i in value]
        else:
            return cls(value)

    def to_leancloud_value(self, value):
        if isinstance(value, dict) and value.get('__type') == 'Pointer':
            return value
        cls = self.get_model_class()
        fn = lambda i: cls.createPointer(i.id)
        if self._many:
            return [fn(j) for j in value]
        else:
            return fn(value)
