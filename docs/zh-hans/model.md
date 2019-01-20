# 模型声明

模型声明的方法类似于传统的 python orm，如 sqlalchemy 或 peewee。将自己的模型类继承于指定的类即可。

## 简单模型

```python
from leancloud_better_storage.storage import models, fields

class People(models.Model):
    name = fields.Field()
    age = fields.Field()
    invited = fields.Field()
```

关于模型字段的声明，可以继续查阅[字段文档](field.md)。

## 名称映射

默认情况下，模型类的类名将会作为 LeanCloud 存储服务的数据集名字。如果想要指定一个不同于类名的名字，可以通过给类变量`__lc_cls__`赋值实现。

```python
from leancloud_better_storage.storage import models, fields

class People(models.Model):
    __lc_cls__ = 'chinese'
    name = fields.Field()
    age = fields.Field()
    invited = fields.Field()
```

此时，`People`类对应的 LeanCloud 存储服务的数据集名将会是`chinese`。
