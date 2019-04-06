import leancloud

from leancloud_better_storage.storage.fields import Field, auto_fill
from leancloud_better_storage.storage.meta import ModelMeta
from leancloud_better_storage.storage.query import Query


class Model(object, metaclass=ModelMeta):
    __lc_cls__ = ''
    __fields__ = {}

    object_id = Field('objectId', default=auto_fill)
    created_at = Field('createdAt', default=auto_fill)
    updated_at = Field('updatedAt', default=auto_fill)

    @classmethod
    def register_pre_create_hook(cls, fn):
        """ 注册新对象保存时的钩子函数。对于 object_id 为空的对象将被视为新对象。 """
        cls._pre_create_hook.append(fn)

    @classmethod
    def register_pre_update_hook(cls, fn):
        """ 注册对象更新时的钩子函数。 """
        cls._pre_update_hook.append(fn)

    @classmethod
    def register_pre_delete_hook(cls, fn):
        """ 注册删除对象时调用的钩子函数。 """
        cls._pre_delete_hook.append(fn)

    def _do_life_cycle_hook(self, life_cycle):
        hook_fn_attr_name = '_{}_hook'.format(life_cycle)
        hook_fn = getattr(self, hook_fn_attr_name, [])
        for cls in self.__class__.mro():
            hook_fn.extend(getattr(cls, hook_fn_attr_name, []))

        for fn in hook_fn:
            fn(self)

    @property
    def lc_object(self):
        return self._lc_obj

    def __init__(self, lc_obj=None):
        self._lc_obj = lc_obj

    @classmethod
    def create(cls, **kwargs):
        # check does given keyword arguments matches model schema
        input_keys = set(kwargs.keys())
        required_keys = set(cls.__meta__.required_fields.keys())
        all_keys = set(cls.__meta__.fields.keys())

        if not input_keys.issubset(all_keys):
            raise KeyError("Unknown field name {}".format(input_keys - all_keys))
        elif not required_keys.issubset(input_keys):
            raise KeyError("Missing required field {}".format(required_keys - input_keys))

        # fill fields and DO NOT BREAK field restriction
        lc_obj = leancloud.Object.create(cls.__lc_cls__)
        obj = cls(lc_obj)
        for attr_name, value in dict(cls.__meta__.attributes_default, **kwargs).items():
            setattr(obj, attr_name, value() if callable(value) else value)

        return obj

    def commit(self, where=None, fetch_when_save=None):
        if where:
            if not isinstance(where, Query):
                raise ValueError('Param `where` should be instance of Query.')
        self._do_life_cycle_hook('pre_create' if self.object_id is None else 'pre_update')
        self._lc_obj.save(where.leancloud_query if where else None, fetch_when_save)
        return self

    @classmethod
    def commit_all(cls, *models):
        for instance in models:
            instance._do_life_cycle_hook('pre_create' if instance.object_id is None else 'pre_update')

        leancloud.Object.extend(cls.__lc_cls__).save_all([instance._lc_obj for instance in models])

    def drop(self):
        self._do_life_cycle_hook('pre_delete')

        self._lc_obj.destroy()
        self._lc_obj = None

    @classmethod
    def drop_all(cls, *models):
        for instance in models:
            instance._do_life_cycle_hook('pre_delete')

        leancloud.Object.extend(cls.__lc_cls__).destroy_all([instance._lc_obj for instance in models])
        for model in models:
            model._lc_obj = None

    @classmethod
    def query(cls):
        return Query(cls)
