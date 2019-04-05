from copy import deepcopy

import leancloud

from leancloud_better_storage.storage.fields import Field, undefined, auto_fill
from leancloud_better_storage.storage.query import Query


def _validate(schema, input_):
    required_fields = {*filter(lambda field: field.nullable is False and field.default is undefined, schema.values())}
    required_keys = {key for key, field in schema.items() if field in required_fields}
    input_keys = {*input_.keys()}

    if not input_keys.issubset(set(schema.keys())):
        raise KeyError("Unknown field name {}".format(input_keys - {*schema.keys()}))
    elif not required_keys.issubset(input_keys):
        raise KeyError("Missing required field {}".format(required_keys - input_keys))


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


model_registry = {}


class ModelMeta(type):
    """
    Model 元类，收集类字段相关信息，完成初始化默认字段名和注册必须的回调。
    """
    _fields_key = '__fields__'
    _lc_cls_key = '__lc_cls__'

    @classmethod
    def _merge_parent_fields(mcs, bases):
        fields = {}

        for bcs in bases:
            fields.update(deepcopy(getattr(bcs, '__fields__', {})))

        return fields

    def __new__(mcs, name, bases, attr):
        # merge super classes fields into __fields__ dictionary.
        fields = attr.get(mcs._fields_key, {})
        fields.update(mcs._merge_parent_fields(bases))

        # Insert fields into __fields__ dictionary.
        # It will replace super classes same named fields.
        for key, val in attr.items():
            if isinstance(val, Field):
                fields[key] = val

        attr[mcs._fields_key] = fields

        # if __lc_cls__ not set, set it as same as python class name.
        lc_cls = attr.get(mcs._lc_cls_key, name)
        attr[mcs._lc_cls_key] = lc_cls

        attr['_pre_create_hook'] = []
        attr['_pre_update_hook'] = []
        attr['_pre_delete_hook'] = []

        # Tag fields with created model class and its __lc_cls__.
        created = type.__new__(mcs, name, bases, attr)

        for key, field in created.__fields__.items():
            field._after_model_created(created, key)

        model_registry[name] = created
        return created


class Model(object, metaclass=ModelMeta):
    """
    Model 基类，自定义的表模型应当继承于 Model。
    继承的 Model 类声明方式类似于 SQLAlchemy 和 Django ORM。

    例子:
    ::

        from leancloud_better_storage.storage.models import Model
        from leancloud_better_storage.storage.fields import StringField, NumberField

        class Person(Model):
            name = StringField(max_length=8)
            age = NumberField()

    模型已经包含了三个由 LeanCloud 产生的字段：

    - `object_id`
    - `created_at`
    - `updated_at`

    这三个字段会由 LeanCloud 自动填充，所以无需在调用`create`时传入。尤其是对于 `object_id`，
    通常不应在创建时指定。

    关于可以使用的字段类，请参考 :ref:`leancloud_better_storage.storage.fields`。
    """
    __lc_cls__ = ''
    __fields__ = {}  # type: dict

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
        """
        创建一个 Model 实例。这个实例不会立即保存至 LeanCloud。

        你可以通过关键字参数来初始化实例字段。

        看下面的例子： ::

            from leancloud_better_storage.storage.models import Model
            from leancloud_better_storage.storage.fields import StringField, NumberField

            class Person(Model):
                name = StringField(nullable=False)
                age = NumberField()

            remilia = Person.create(name='remilia scarlet', age=549)  # just a random age number, ignore it.
            flandre = Person.create(name='flandre scarlet', age=549)

        被指定 `nullable` 为 `False` 并且 `default` 为 `None` 、 `undefined` 的字段必须在初始化时提供，否则将会产生一个 `KeyError` 。

        需要注意的是 `default` 被指定为 `None` 时的行为和 `undefined` 行为不同，因为在传输和存储的过程，
        序列化为JSON/BSON的Python的 `None` 会被认作 `null` ，而 `undefined` 则令字段不出现。
        这一概念与 JavaScript 近乎一致。

        :param kwargs: 初始化字段
        :return:
        """
        _validate(cls.__fields__, kwargs)
        return cls(leancloud.Object.create(cls.__lc_cls__, **_merge_default_and_args(cls.__fields__, kwargs)))

    def commit(self):
        """
        保存这个对象到 LeanCloud。

        使用 LeanCloud SDK 的 `save` 实现。

        会触发 `pre_create` 回调。

        :return: self
        """
        self._do_life_cycle_hook('pre_create' if self.object_id is None else 'pre_update')
        self._lc_obj.save()
        return self

    @classmethod
    def commit_all(cls, *models):
        """
        保存多个对象到 LeanCloud。所有传入的对象必须是同一个 Model 类的实例。

        使用 LeanCloud SDK 的 `save_all` 实现。

        保存会触发 `pre_create` 回调。

        :param models:
        :return:
        """
        for instance in models:
            instance._do_life_cycle_hook('pre_create' if instance.object_id is None else 'pre_update')

        leancloud.Object.extend(cls.__lc_cls__).save_all([instance._lc_obj for instance in models])

    def drop(self):
        """
        从 LeanCloud 删除这个对象。

        删除后对象进入不可用状态，请不要再做任何读写操作。

        :return: None
        """
        self._do_life_cycle_hook('pre_delete')

        self._lc_obj.destroy()
        self._lc_obj = None

    @classmethod
    def drop_all(cls, *models):
        """
        从 LeanCloud 删除多个对象，所有传入的对象必须是同一个 Model 的实例。

        删除使用 LeanCloud SDK 提供的 `destroy_all` 实现。

        删除会触发在 Model 类注册的 `pre_delete` 回调。

        :param models: 一个或多个 Model 类实例
        :return: None
        """
        for instance in models:
            instance._do_life_cycle_hook('pre_delete')

        leancloud.Object.extend(cls.__lc_cls__).destroy_all([instance._lc_obj for instance in models])
        for model in models:
            model._lc_obj = None

    @classmethod
    def query(cls):
        return Query(cls)
