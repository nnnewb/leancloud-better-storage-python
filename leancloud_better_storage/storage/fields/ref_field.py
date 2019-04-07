from leancloud import Object

from .defaults import undefined
from .field import Field
from ..objectid import ObjectId
from ..query import Condition, ConditionOperator


class RefField(Field):
    __hash__ = object.__hash__
    _fit_fn = {
        ObjectId: lambda val: val.lc_object,
        int: lambda val: ObjectId(str(val)).lc_object,
        str: lambda val: ObjectId(hex(val)[2:]).lc_object,
    }

    def __init__(self, name=None, nullable=True, default=undefined, ref_cls=None, lazy=True):
        super().__init__(name, nullable, default)
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
            from leancloud_better_storage.storage.meta import model_registry
            self._ref_cls = model_registry[self._ref_cls]

        return self._ref_cls
