# leancloud-better-storage-python

![travis-ci](https://www.travis-ci.com/nnnewb/leancloud-better-storage-python.svg?branch=master)

:construction_worker: 单元测试依赖于一个可用的leancloud-app，所以travis-ci的测试总是failed的，考虑后面怎么做个mock。

更优雅且pythonic的方式使用leancloud storage。

:construction: 施工中，文档也没有。有意参与或者疑问就开个issue，看到回复。

## Quick Start

一个简单的商品类声明和查询，分别用leancloud sdk和这个包写查询代码。

```python
# 使用 leancloud-sdk 编写
from datetime import datetime
from leancloud import Object, LeanCloudError

Product = Object.extend('Product')
try:
    # 查找叫做 MyProduct，价格比10高，在18年8月1日之前创建的商品
    product = Product.query.equal_to('name', 'MyProduct')\
        .greater_than_or_equal_to('price', 10)\
        .less_than_or_equal_to('createdAt', datetime(year=2018,month=8,day=1))\
        .first()
except LeanCloudError as exc:
    if exc.code == 101:
        product = None
    else:
        raise
```

```python
# 使用 better-leancloud-storage-python 编写
from datetime import datetime
from better_leancloud_storage.storage.models import Model
from better_leancloud_storage.storage.fields import Field

class Product(Model):
    name = Field()
    price = Field()
    created_at =Field()

product = Product.query()\
    .filter_by(name='MyProduct')\
    .filter(Product.price > 10,
            Product.created_at < datetime(year=2018,month=8,day=1))\
            .first()
```