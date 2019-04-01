from datetime import datetime

from leancloud import Object

from leancloud_better_storage.storage._util import deprecated
from leancloud_better_storage.storage.objectid import ObjectId
from leancloud_better_storage.storage.order import OrderBy, ResultElementOrder
from leancloud_better_storage.storage.query import Condition, ConditionOperator

FIELD_AVAILABLE_TYPES = [int, float, str, list, dict, None]


class undefined:
    pass


class auto_fill:
    pass


class MetaField(type):

    def __new__(mcs, name, bases, attributes):
        created = type.__new__(mcs, name, bases, attributes)
        created.__hash__ = object.__hash__
        return created


class Field(object, metaclass=MetaField):

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


class StringField(Field):

    def __init__(self, max_length, name=None, nullable=True, default=undefined):
        super().__init__(name, nullable, default, None)
        self._max_length = max_length

    def __set__(self, instance, value):
        if len(value) > self._max_length:
            raise ValueError('string too long.')
        super(StringField, self).__set__(instance, value)

    def contains(self, sub):
        return Condition(self, ConditionOperator.Contains, sub)

    def regex(self, pattern):
        return Condition(self, ConditionOperator.Regex, pattern)

    def startswith(self, pattern):
        return Condition(self, ConditionOperator.StartsWith, pattern)


class NumberField(Field):
    pass


class BooleanField(Field):
    pass


class DateTimeField(Field):

    def __init__(self, name=None, nullable=True, default=undefined, auto_now=False, auto_now_add=False,
                 now_fn=datetime.now):
        super().__init__(name, nullable, default, None)
        self._auto_now = auto_now
        self._auto_now_add = auto_now_add
        self._now_fn = now_fn

    def _after_model_created(self, model, name):
        super()._after_model_created(model, name)

        def hook_fn(i): return i.lc_object.set(self.field_name, self._now_fn())

        if self._auto_now_add:
            model.register_pre_create_hook(hook_fn)
        if self._auto_now:
            model.register_pre_update_hook(hook_fn)


class FileField(Field):
    pass


class ArrayField(Field):
    pass


class ObjectField(Field):
    pass


class GeoPointField(Field):
    pass


class RefField(Field):
    __hash__ = object.__hash__
    _fit_fn = {
        ObjectId: lambda val: val.lc_object,
        int: lambda val: ObjectId(str(val)).lc_object,
        str: lambda val: ObjectId(hex(val)[2:]).lc_object,
    }

    def __init__(self, name=None, nullable=True, default=undefined, ref_cls=None, lazy=True):
        super().__init__(name, nullable, default, None)
        self._ref_cls = ref_cls
        self.lazy = lazy

    def __eq__(self, other):
        return Condition(self, ConditionOperator.Equal, self._fit_fn[type(other)](other))

    def __ne__(self, other):
        return Condition(self, ConditionOperator.NotEqual, self._fit_fn[type(other)](other))

    def __lt__(self, other):
        raise ValueError('RefField not support `<` comparison.')

    def __gt__(self, other):
        raise ValueError('RefField not support `>` comparison.')

    def __get__(self, instance, owner):
        if instance is None:
            return self

        obj = instance.lc_object.get(self.field_name)

        if obj is None:
            return None

        if len(obj._attributes) == 1 and self.lazy:
            obj.fetch()

        return self.ref_cls(obj)

    def __set__(self, instance, value):
        if value is undefined or value is None:
            super().__set__(instance, value)
        else:
            try:
                instance.lc_object.set(self.field_name, self._fit_fn[type(value)](value))
            except KeyError:
                from leancloud_better_storage.storage.models import Model
                if isinstance(value, Model):
                    instance.lc_object.set(self.field_name, value.lc_object)
                elif isinstance(value, Object):
                    instance.lc_object.set(self.field_name, value)
                else:
                    raise ValueError('Unexpected ref field assignment: {}'.format(repr(value)))

    @property
    def ref_cls(self):
        if isinstance(self._ref_cls, str):
            from leancloud_better_storage.storage.models import model_registry
            self._ref_cls = model_registry[self._ref_cls]

        return self._ref_cls


class AnyField(Field):
    pass
