from copy import deepcopy

from leancloud_better_storage.storage._util import ThreadSafeDict
from leancloud_better_storage.storage.fields import Field, undefined, auto_fill


class ModelMetaInfo:

    @property
    def fields(self):
        return self._fields

    @property
    def inherit_fields(self):
        return self._inherit_fields

    @property
    def required_fields(self):
        return self._required_fields

    @property
    def attributes_default(self):
        return self._default_attributes

    @property
    def leancloud_class(self):
        return self._leancloud_class

    def __init__(self, leancloud_class, fields, inherit_fields, required_fields, attributes_default):
        self._leancloud_class = leancloud_class
        self._fields = fields
        self._inherit_fields = inherit_fields
        self._required_fields = required_fields
        self._default_attributes = attributes_default


class ModelMeta(type):
    """
    ModelMeta

    metaclass of all lean cloud storage models.
    it fill field property, collect model information and make more function work.
    """

    def __new__(mcs, name, bases, attr):
        # collect fields in declaration
        fields = {
            name: a
            for name, a in attr.items()
            if isinstance(a, Field)
        }
        for the_attr_name, field in fields.items():
            field.attr_name = the_attr_name

        # collect inherit fields (DO NOT overwrite exists name)
        inherit_fields = {}
        for base in bases:
            for attr_name, field in getattr(base, '__fields__', {}).items():
                if attr_name not in fields:
                    fields[attr_name] = deepcopy(field)

                inherit_fields[attr_name] = deepcopy(field)

        # calculate required fields
        required_fields = {}
        for field in fields.values():
            if field.nullable is False and field.default in (None, undefined):
                required_fields[field.field_name] = field

        # calculate attributes default
        attributes_default = {}
        for field in fields.values():
            if field.default not in (undefined, auto_fill):
                attributes_default[field.attr_name] = field.default

        # set default model mapping name
        if not attr.get('__lc_cls__', None):
            attr['__lc_cls__'] = name

        # collect meta data
        attr['__meta__'] = ModelMetaInfo(attr['__lc_cls__'],
                                         fields,
                                         inherit_fields,
                                         required_fields,
                                         attributes_default)
        attr['__fields__'] = fields  # keep compatible with previous version

        # inject hook table
        attr['_pre_create_hook'] = []
        attr['_pre_update_hook'] = []
        attr['_pre_delete_hook'] = []

        # Tag fields with created model class and its __lc_cls__.
        created = type.__new__(mcs, name, bases, attr)

        for key, field in created.__fields__.items():
            field._after_model_created(created, key)

        model_registry[name] = created
        return created


class ModelRegistry(ThreadSafeDict):
    pass


model_registry = ModelRegistry()
