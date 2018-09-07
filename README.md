# leancloud-better-storage-python

[![travis-ci](https://www.travis-ci.com/nnnewb/leancloud-better-storage-python.svg?branch=master)](https://www.travis-ci.com/nnnewb/leancloud-better-storage-python)
[![codecov](https://codecov.io/gh/nnnewb/leancloud-better-storage-python/branch/master/graph/badge.svg)](https://codecov.io/gh/nnnewb/leancloud-better-storage-python)

更优雅且 pythonic 的方式使用 leancloud storage。

> :construction: 施工中，文档也没有。有意参与或者疑问就开个 issue，看到回复。

## 快速开始

以一系列最简单的例子来说明使用方式。

### 模型声明

```python
from better_leancloud_storage.storage.models import Model
from better_leancloud_storage.storage.fields import Field

class Product(Model):
    name = Field('product_name', nullable=False)
    price = Field(nullable=False)
    field3 = Field(nullable=False, default=1)
```

### CRUD

#### 创建和保存

```python
product = Product.create(name='FirstProduct',price=100)
product.commit()
```

#### 查找

代码仅演示查询语法

```python
products = Product\
    .query()\
    .filter_by(name='LastProduct', price=100)\
    .and_()\
    .filter(Product.other_field > 10, Product.other_field < 100)\
    .or_()\
    .filter(Product.other_field < 10, Product.other_field > -10)\
    .order_by(Product.created_at.asc)\
    .find(skip=10, limit=100)  # also support first(), count()
```

### 更新

```python
product = Product.query().filter_by(name='FirstProduct').first()
product.name = 'LastProduct'
product.commit()
```

### 删除

```python
product = Product.query().filter_by(name='FirstProduct').first()
product.drop()
```
