# leancloud-better-storage-python

[![PyPI version](https://badge.fury.io/py/leancloud-better-storage.svg)](https://badge.fury.io/py/leancloud-better-storage)
[![travis-ci](https://www.travis-ci.com/nnnewb/leancloud-better-storage-python.svg?branch=master)](https://www.travis-ci.com/nnnewb/leancloud-better-storage-python)
[![codecov](https://codecov.io/gh/nnnewb/leancloud-better-storage-python/branch/master/graph/badge.svg)](https://codecov.io/gh/nnnewb/leancloud-better-storage-python)

better leancloud storage wrapper. Simple and lightweight.

> Sorry for my bad grammar and spell :)

## Compatibility

Compatible with Python3.5+ , no Python2 support.

## Installation

install by `easy_install` or `pip`.

```commandline
pip install leancloud-better-storage
```

## Quick start

Simple model declaration and query syntax.

### Model declaration

```python
from datetime import datetime
from leancloud_better_storage.storage.models import Model
from leancloud_better_storage.storage.fields import Field

class Product(Model):
    name = Field(nullable=False)
    price = Field(nullable=False)
    publish_at = Field()
```

`Field` constructor accept series option arguments.

- `name`, specify field name in database.
- `nullable`, should you provide initial value for this field when you create new record.
- `default`, if you are not set default value, `commit` will not create new field or set `null` in leancloud storage. Because `undefined` and `null` is different in javascript :( . leancloud storage based on MongoDB, and MongoDB use JavaScript as first class citizen.
- `type_` not used yet.

### CRUD operations

You can use `Model.create` to create new record, this method should check your record has been correctly initialized.

```python
product = Product.create(name='FirstProduct', price=100)
product.commit()

# v0.1.3 now default null value
assert product.publish_at is None
```

If you are not pass default initial value for non-default field, it will be null (in storage, `undefined`).

#### Read & Query

use `filter` and/or `filter_by` to select records.

`filter` support more human readable condition selection.

- `>`, `<`, `>=`, `<=`, `==` compare field with some value. Not supprot compare between fields in same or not same model.
- `contains` simple pattern match for string field.
- `and_`, `or_` between two or more queries.

See examples below.

```python
# find by simple equation
products = Product.query().filter_by(name='product').find()

# support >,<,>=,<=,==.but not support compare to another field.
products = Product.query().filter(Product.price < 10).find()

# support contains
products = Product.query().filter(Product.name.contains('art')).find()

# support and_(), or_().
products = Product.query().filter(Product.created_at > datetime(2018,8,1)).and_() \
    .filter(Product.created_at < datetime(2018,9,1)).find()

# find support limit and skip argument.
products = Product.query().order_by(Product.price.desc).find(limit=10)

# support pagination, start from page 0 and 10 elements per page.
pages = Product.query().paginate(0, 10)
for page in pages:
    print(page.items) # access elements
```

### Update

You can update record by assign new value and commit change.

```python
product = Product.query().filter_by(name='FirstProduct').first()
product.name = 'LastProduct'
product.commit()
```

### Delete

`drop` method will delete record and set object invalid. Use `drop_all` for bulk operation.

```python
product = Product.query().filter_by(name='FirstProduct').first()
product.drop()

products = Product.query().filter_by().find()
Product.drop_all(products)
```

### Known limit

Some bulk modification/deletion does not support execute with conditions.
It's limited by leancloud storage service.
For more detail, see document below.

- [python guide - bulk operation](https://leancloud.cn/docs/leanstorage_guide-python.html#hash787692837)
- [CQL guide - update](https://leancloud.cn/docs/cql_guide.html#hash-838846263)
- [CQL guide - delete](https://leancloud.cn/docs/cql_guide.html#hash-1335458389)

## Change log

- 0.1.7 修复初始值 null 覆盖了存储服务生成字段值的问题。
