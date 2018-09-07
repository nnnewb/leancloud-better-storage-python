快速开始
##########

建立模型
************

使用 `better-leancloud-storage` 建立模型就像是编写一个 Python 类。

::

    from leancloud_better_storage.storage.models import Model
    from leancloud_better_storage.storage.fields import Field

    class MyModel(Model):
        name = Field()

除去导入必要的类，声明一个数据模型只需要这样几行代码。类名 `MyModel` 默认被作为映射到LeanCloud的类名称，对应于 LeanCloud 的
.. [Ref] Class 概念
