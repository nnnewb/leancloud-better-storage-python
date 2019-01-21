# 插入

插入一条新记录的过程如下。

1. 创建模型实例
2. 修改
3. 保存

## 1. 创建实例

使用`leancloud_better_storage`创建模型实例需要使用`create`方法。

`create`方法接受任意关键字参数，这些关键字参数将作为对应字段的初始值，初始值列表必须满足字段非空约束。

以一个`People`模型为例。

```python
from leancloud_better_storage.storage import models, fields

class People(models.Model):
    __lc_cls__ = 'chinese'
    name = fields.Field(nullable=False)
    age = fields.Field(nullable=False)
    invited = fields.Field()
```

约束`name`与`age`在创建时必须非空，所以对应的`create`调用必须提供`name`和`age`两个参数来初始化。

```python
mr_zhang = People.create(name='Mr.Zhang', age=22)
mr_zhang.commit()
```

`create`调用返回一个模型实例，如果未满足约束则抛出`KeyError`异常。

一旦创建完成，即可进行修改，或直接提交保存。

## 2. 修改

修改字段值的方式很简单。

```python
mr_zhang.invited = True
```

直接通过`.`访问字段并赋值即可。

## 3. 保存

保存记录可以通过`commit`或`Model.commit_all`方法，后者可以更高效地保存复数记录。

```python
other_visitors = [...]
mr_zhang.commit()
People.commit_all(*other_visitors)
```

`commit_all`接受任意数量的位置参数，这些参数必须是模型实例，否则保存将会抛出 LeanCloudError 异常。
