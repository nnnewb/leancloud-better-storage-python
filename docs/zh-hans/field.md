# 字段

字段是模型类里的`fields.Field`实例。

## 默认字段

```python
from leancloud_better_storage.storage import models, fields

class People(models.Model):
    name = fields.Field()
    age = fields.Field()
    invited = fields.Field()
```

无参数创建的`fields.Field`实例所对应的字段有一些默认行为。

- 使用实例的名字作为映射的字段名
- 字段可空

## 名称映射

字段名默认是模型类声明时声明的字段名。例如，模型声明中写下`name = fields.Field()`则对应到 LeanCloud 数据集中的字段名将会是`name`。

如果需要指定不同的字段名，可以给予`fields.Field`一个`name`参数。

```python
from leancloud_better_storage.storage import models, fields

class People(models.Model):
    name = fields.Field('MyName')
    age = fields.Field('MyAge')
    invited = fields.Field('Invited')
```

此时的映射就被修改为了`name`对应 LeanCloud 存储的数据集中的`MyName`字段。

## 可空检查

可空检查是由`leancloud_better_storage`完成的，请注意，这一配置的强制约束性仅限于使用本库创建记录的情况下。

如果需要指定特定字段非空，则可以通过给予`fields.Field`一个`nullable`参数实现。

```python
from leancloud_better_storage.storage import models, fields

class People(models.Model):
    name = fields.Field('MyName', nullable=False)
    age = fields.Field('MyAge', nullable=False)
    invited = fields.Field('Invited')
```

`nullable`默认为`True`，即允许在创建时不提供初始值。

**需要注意的是，这没有限制你更新该字段的时候赋予 null 值**
