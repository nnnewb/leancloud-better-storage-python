# 查询

## 1. Query

使用`query`方法取得一个`Query`实例后，即可开始查询。`filter_by`和`filter`方法是最基础的查询方法。

```python
from leancloud_better_storage.storage import models, fields

class People(models.Model):
    __lc_cls__ = 'chinese'
    name = fields.Field(nullable=False)
    age = fields.Field(nullable=False)
    invited = fields.Field()
```

举例言之，如果要查询出所有被邀请的人，可以通过如下代码实现。

```python
People.query().filter_by(invited=True).find()
# or
People.query().filter(People.invited == True).find()
```

`filter_by`接受任意数量的关键字参数，查询字段值等于参数的记录。

`filter`接受任意数量的位置参数，参数必须是`Condition`。

如上述代码中`People`模型的`invited`字段，是一个`Field`实例，`Field`类重载了`==`运算符，使`People.invited == True`返回一个`Condition`。

### 1.1 支持的运算符

目前字段都支持这些比较运算。

- `==`
- `!=`
- `>`
- `>=`
- `<`
- `<=`

### 1.2 字符串匹配

对于字符串类型的字段支持正则匹配的查询。

目前支持的有这些查询条件。

- `contains`

`contains`条件为查找包含子串的字符串。例子如下。

```python
# 查询名字包含 Wang 的人
People.query().filter(People.name.contains('Wang'))
```

- `startswith`

`startswith`条件查找以指定字符串开头的字符串。例子如下。

```python
# 查询名字以 Mr. 开头的字符串
People.query().filter(People.name.startswith('Mr.'))
```

- `regex`

`regex`允许以正则表达式查询匹配的字符串。例子如下。

```python
People.query().filter(People.name.regex(r'^Mr\..*Li'))
```

## 2. and* & or*

`and_`和`or_`允许连接多个条件进行查询。

举例来说，查询名字中包含`Wang`或者`Li`的人。

```python
People.query().filter(People.name.contains('Wang')).or_().filter(People.name.contains('Li'))
```

## 3. order_by

对查询结果可以使用`order_by`排序。`order_by`接受多个排序参数，当第一个字段相同时，比较第二个排序字段进行排序。

```python
People.query().order_by(People.name.desc, People.age.asc).find()
```

上述查询将`People`中的记录以`name`作为首要条件，倒序排列，再将`age`作为次要条件，正序排列。

## 4. limit 和 skip

`find`调用已经在上面出现了很多次。

`filter`和`filter_by`，以及`order_by`，`and_`，`or_`，都是在查询的条件上下功夫，而真正执行查询的是`find`。

`find`以列表的形式返回查询结果，你也可以通过`first`来返回单个查询结果。

`find`支持两个参数，`skip`和`limit`。`skip`指定跳过多少条记录进行查询，`limit`则限制查询结果记录数量。

`limit`最大值为 1000，这是受限于 LeanCloud 存储服务本身的约束，`skip`则没有限制最大值。

## 5. 分页

> LeanCloud 查询结果上限为 1000 条记录，默认为查询 100 条记录。如果需要遍历整个集合，必须使用分页器或自行指定 offset。

查询分页是一个很常见的场景，`leancloud_better_storage`提供了`Pages`类来帮助分页查询。

取得分页器的方式很简单。

```python
pages = People.query().paginate(1, 100)
```

`paginate`方法接受两个参数，`page`和`size`，分别表示查询的页数也每页记录数量。`size`最大值 1000，这是受限于 LeanCloud 服务本身的约束。

需要注意的是，`page`应从 1 开始计数。

### 5.1 遍历分页

`Pages`支持`for ... in ...`语法来进行遍历。

```python
for page in pages:
    for people in page.items:
        ...  # do something for each people
```

## 6. Aggregate 函数

目前仅支持`count`来查询符合条件的记录数量。

```python
# 查询被邀请的人数
invited_count = People.query().filter_by(invited=True).count()
```

## 7. 回到 LeanCloud SDK

对于被包装好的查询，可以通过`build_query`方法来取出一个 LeanCloud SDK 的原始`Query`对象。
