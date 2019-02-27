from copy import deepcopy

import leancloud

from leancloud_better_storage.storage.fields import Field, undefined, auto_fill
from leancloud_better_storage.storage.query import Query


def _validate(schema, input_):
    required_fields = {*filter(lambda field: field.nullable is False and field.default is undefined, schema.values())}
    required_keys = {key for key, field in schema.items() if field in required_fields}
    input_keys = {*input_.keys()}

    if input_keys.issuperset({*schema.keys()}):
        raise KeyError("Unknown field name {0}".format(input_keys - {*schema.keys()}))
    elif not required_keys.issubset(input_keys):
        raise KeyError("Missing required field {0}".format(required_keys - input_keys))


def _merge_default_and_args(schema, args):
    attrs = {
        field.field_name: field.default() if callable(field.default) else field.default
        for field in filter(lambda field: field.default not in (undefined, auto_fill), schema.values())
        if field.nullable or field.default
    }
    attrs.update({
        schema[key].field_name: value
        for key, value in args.items()
    })
    return attrs


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
    __fields__ = {}  # type: dict

    object_id = Field('objectId', default=auto_fill)
    created_at = Field('createdAt', default=auto_fill)
    updated_at = Field('updatedAt', default=auto_fill)

    @property
    def lc_object(self):
        return self._lc_obj

    def __init__(self, lc_obj=None):
        self._lc_obj = lc_obj

    @classmethod
    def create(cls, **kwargs):
        _validate(cls.__fields__, kwargs)
        return cls(leancloud.Object.create(cls.__lc_cls__, **_merge_default_and_args(cls.__fields__, kwargs)))

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
