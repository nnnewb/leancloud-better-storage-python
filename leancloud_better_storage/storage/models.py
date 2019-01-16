from copy import deepcopy

import leancloud
from leancloud import operation

from leancloud_better_storage.storage.query import Query
from leancloud_better_storage.storage.fields import Field, undefined


class ModelMeta(type):
    """
    ModelMeta

    metaclass of all lean cloud storage models.
    it fill field property, collect model information and make more function work.
    """
    _fields_key = '__fields__'
    _lc_cls_key = '__lc_cls__'
    __classes__ = {}

    @classmethod
    def merge_parent_fields(mcs, bases):
        fields = {}

        for bcs in bases:
            fields.update(deepcopy(getattr(bcs, '__fields__', {})))

        return fields

    @classmethod
    def tag_all_fields(mcs, model, fields):
        for key, val in fields.items():
            val._cls_name = model.__lc_cls__
            val._model = model

            # if field unnamed, set default name as python class declared member name.
            if val.field_name is None:
                val._field_name = key

    def __new__(mcs, name, bases, attr):
        # merge super classes fields into __fields__ dictionary.
        fields = attr.get(mcs._fields_key, {})
        fields.update(mcs.merge_parent_fields(bases))

        # Insert fields into __fields__ dictionary.
        # It will replace super classes same named fields.
        for key, val in attr.items():
            if isinstance(val, Field):
                fields[key] = val

        attr[mcs._fields_key] = fields

        # if __lc_cls__ not set, set it as same as python class name.
        lc_cls = attr.get(mcs._lc_cls_key, name)
        attr[mcs._lc_cls_key] = lc_cls

        # Tag fields with created model class and its __lc_cls__.
        created = type.__new__(mcs, name, bases, attr)
        mcs.tag_all_fields(created, created.__fields__)
        mcs.__classes__[name] = created
        return created


class Pointer(dict):
    def __init__(self, className, objectId):
        self['__type'] = 'Pointer'
        self['className'] = className
        self['objectId'] = objectId





class Model(object, metaclass=ModelMeta):
    __lc_cls__ = ''
    __fields__ = {}

    __data__ = None

    object_id = Field('objectId')
    created_at = Field('createdAt')
    updated_at = Field('updatedAt')

    @property
    def lc_object(self):
        return self._lc_obj

    def __init__(self, lc_obj=None):
        self._lc_obj = lc_obj
        self.__data__ = {}

    def __getattribute__(self, item):
        ret = super(Model, self).__getattribute__(item)
        if isinstance(ret, Field):
            field_name = self._get_real_field_name(item)
            if field_name not in self.__data__:
                result = self._lc_obj.get(field_name)
                if result is None:
                    return ret.default
                self.__data__[field_name] = ret.to_python_value(result)
            return self.__data__[field_name]
        return ret

    def __setattr__(self, key, value):
        field = self.__fields__.get(key)
        if field:
            if isinstance(value, operation.BaseOp):
                if field.field_name in self.__data__:
                    del self.__data__[field.field_name]
                self._lc_obj.set(field.field_name, value)
            else:
                self.__data__[field.field_name] = value
                self._lc_obj.set(field.field_name, field.to_leancloud_value(value))
        else:
            return super(Model, self).__setattr__(key, value)

    @classmethod
    def _get_real_field_name(cls, name):
        if name in cls.__fields__:
            return cls.__fields__[name].field_name
        return None

    @classmethod
    def create(cls, **kwargs):
        if not {*kwargs.keys()}.issubset({*cls.__fields__.keys()}):
            raise KeyError('Unknown field name {0}'.format({*kwargs.keys()} - {*cls.__fields__.keys()}))

        attr = {
            field.field_name: field.default() if callable(field.default) else field.default
            for field in filter(lambda v: v.default is not undefined, cls.__fields__.values())
            if field.nullable or field.default
        }

        for key, val in kwargs.items():
            real_name = cls._get_real_field_name(key)
            attr[real_name] = val

        missing_fields = {
            key
            for key, field in cls.__fields__.items()
            if field.nullable is False and field.default in (None, undefined) and field.field_name not in attr
        }
        if len(missing_fields) != 0:
            raise KeyError('Missing required field {0}.'.format(missing_fields))

        data = {k: cls.__fields__[k].to_leancloud_value(v) for (k, v) in attr.items()}
        lc_obj = leancloud.Object.create(cls.__lc_cls__, **data)
        return cls(lc_obj)

    def commit(self, **kwargs):
        self._lc_obj.save(**kwargs)
        self.__data__ = {}
        return self

    @classmethod
    def commit_all(cls, *models):
        leancloud.Object.extend(cls.__lc_cls__).save_all([
            model._lc_obj
            for model in models
        ])

    def drop(self):
        self._lc_obj.destroy()
        self._lc_obj = None

    @classmethod
    def drop_all(cls, *models):
        leancloud.Object.extend(cls.__lc_cls__).destroy_all([
            model._lc_obj
            for model in models
        ])
        for model in models:
            model._lc_obj = None

    @classmethod
    def query(cls):
        return Query(cls)

    @classmethod
    def create_without_data(cls, object_id):
        return cls(leancloud.Object.extend(cls.__lc_cls__).create_without_data(object_id))

    @classmethod
    def createPointer(cls, object_id):
        return Pointer(cls.__lc_cls__, object_id)

    def toPointer(self):
        return Pointer(self.__lc_cls__, self.object_id)
