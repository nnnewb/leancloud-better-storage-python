from copy import deepcopy

import leancloud

from leancloud_better_storage.storage.query import Query
from leancloud_better_storage.storage.fields import Field


class ModelMeta(type):
    """
    ModelMeta

    metaclass of all lean cloud storage models.
    it fill field property, collect model information and make more function work.
    """
    _fields_key = '__fields__'
    _lc_cls_key = '__lc_cls__'

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
        return created


class Model(object, metaclass=ModelMeta):
    __lc_cls__ = ''
    __fields__ = {}

    object_id = Field('objectId')
    created_at = Field('createdAt')
    updated_at = Field('updatedAt')

    @property
    def lc_object(self):
        return self._lc_obj

    def __init__(self, lc_obj=None):
        self._lc_obj = lc_obj

    def __getattribute__(self, item):
        ret = super(Model, self).__getattribute__(item)
        if isinstance(ret, Field):
            field_name = self._get_real_field_name(item)

            return self._lc_obj.get(field_name)

        return ret

    def __setattr__(self, key, value):
        field_name = self._get_real_field_name(key)
        if field_name is None:
            return super(Model, self).__setattr__(key, value)

        self._lc_obj.set(field_name, value)

    @classmethod
    def _get_real_field_name(cls, name):
        if name in cls.__fields__:
            return cls.__fields__[name].field_name
        return None

    @classmethod
    def create(cls, **kwargs):
        default_key_set = {
            key
            for key, field in cls.__fields__.items()
            if field.default is not None
        }
        required_key_set = {
            key
            for key, field in cls.__fields__.items()
            if field.nullable is False and field.default is None
        }
        input_key_set = set(kwargs.keys())
        fields_key_set = set(cls.__fields__.keys())

        # if input key has any key not inside field declaration
        if input_key_set.issubset(fields_key_set) is False:
            difference = input_key_set - fields_key_set
            raise KeyError('Unknown fields {0}.'.format(difference))

        # if input key not contains all required keys
        if required_key_set != set(kwargs.keys()) and required_key_set.issubset(kwargs.keys()) is False:
            difference = required_key_set - input_key_set
            raise KeyError('Required fields {0}'.format(difference))

        attr = {
            cls.__fields__[key].field_name: cls.__fields__[key].default()
            if callable(cls.__fields__[key].default)
            else cls.__fields__[key].default
            for key in default_key_set
        }
        for key, _ in kwargs.items():
            field_name = cls._get_real_field_name(key)
            if field_name is None:
                raise Exception('Internal error: field not register correctly.')
            attr[field_name] = kwargs[key]

        lc_obj = leancloud.Object.create(cls.__lc_cls__, **attr)
        return cls(lc_obj)

    def commit(self):
        self._lc_obj.save()
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
