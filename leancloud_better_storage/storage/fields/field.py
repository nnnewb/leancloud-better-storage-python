from .defaults import undefined
from .meta import MetaField
from .._util import deprecated
from ..order import OrderBy, ResultElementOrder
from ..query import Condition, ConditionOperator


class Field(object, metaclass=MetaField):

    @property
    def field_name(self):
        return self._field_name

    @property
    def attr_name(self):
        return self._attr_name

    @attr_name.setter
    def attr_name(self, name):
        if not self._attr_name:
            self._attr_name = name
        else:
            raise AttributeError('attr_name should only assigned once by ModelMeta.')

    @property
    def nullable(self):
        return self._field_nullable

    @property
    @deprecated('')
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

    def __init__(self, name=None, nullable=True, default=undefined):
        self._model = None
        self._attr_name = None
        self._field_name = name
        self._field_nullable = nullable
        self._field_default = default

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

    def __get__(self, instance, owner):
        if instance:
            return instance.lc_object.get(self.field_name)
        return self

    def __set__(self, instance, value):
        if value is undefined:
            instance.lc_object.unset(self.field_name, value)
        instance.lc_object.set(self.field_name, value)

    def _after_model_created(self, model, name):
        self._cls_name = model.__lc_cls__
        self._model = model
        if self._field_name is None:
            self._field_name = name

    # question: any behavior when user say wanna to delete a field ?

    @deprecated('Use String field instead.')
    def contains(self, sub):
        return Condition(self, ConditionOperator.Contains, sub)

    @deprecated('Use String field instead.')
    def regex(self, pattern):
        return Condition(self, ConditionOperator.Regex, pattern)

    @deprecated('Use String field instead.')
    def startswith(self, pattern):
        return Condition(self, ConditionOperator.StartsWith, pattern)
