# leancloud-better-storage-python

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
```

### CRUD operations

#### Create

```python
product = Product.create(name='FirstProduct',price=100)
product.commit()
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
