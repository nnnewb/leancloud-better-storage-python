# leancloud-better-storage-python

[![PyPI version](https://badge.fury.io/py/leancloud-better-storage.svg)](https://badge.fury.io/py/leancloud-better-storage)
[![travis-ci](https://www.travis-ci.com/nnnewb/leancloud-better-storage-python.svg?branch=master)](https://www.travis-ci.com/nnnewb/leancloud-better-storage-python)
[![codecov](https://codecov.io/gh/nnnewb/leancloud-better-storage-python/branch/master/graph/badge.svg)](https://codecov.io/gh/nnnewb/leancloud-better-storage-python)

better leancloud storage wrapper. Simple and lightweight.

## Installation

install by `easy_install` or `pip`.

```commandline
$ pip install leancloud-better-storage
```

## Quick start

Model declaration and query just like SQLAlchemy, see example below.

### Model declaration

```python
from leancloud_better_storage.storage.models import Model
from leancloud_better_storage.storage.fields import Field

class Product(Model):
    name = Field('product_name', nullable=False)
    price = Field(nullable=False)
    field3 = Field(nullable=False, default=1)
    field4 = Field()
```

### CRUD operations

#### Create

```python
product = Product.create(name='FirstProduct',price=100)
product.commit()

# v0.1.3 now default null value
assert product.field4 is None
```

#### Read & Query

```python
# find by simple equation
products = Product.query().filter_by(name='product').find()
# support >,<,>=,<=,==.but not support compare to another field.
products = Product.query().filter(Product.price < 10).find()
# support and_(), or_().
products = Product.query().filter(Product.created_at > datetime(2018,8,1)).and_() \
    .filter(Product.created_at < datetime(2018,9,1)).find()
# find support limit and skip argument.
products = Product.query().order_by(Product.price.desc).find(limit=10)
# also support pagination, start from page 0 and 10 elements per page.
pages = Product.query().paginate(0, 10)
for page in pages:
    print(page.items) # access elements
```

### Update

```python
product = Product.query().filter_by(name='FirstProduct').first()
product.name = 'LastProduct'
product.commit()
```

### Delete

```python
product = Product.query().filter_by(name='FirstProduct').first()
product.drop()
```

## Update log

* 0.1.7 修复初始值 null 覆盖了存储服务生成字段值的问题。
