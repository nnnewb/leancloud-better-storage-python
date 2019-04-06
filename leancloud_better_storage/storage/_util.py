import logging
from functools import wraps
from threading import Lock
from collections import UserDict


class ThreadSafeDict(UserDict):
    """ Thread safe dictionary.
    线程安全的字典。

    todo: that's awful, need improvement.
    """

    def __init__(self, from_dictionary=None, **kwargs):
        self._lock = Lock()
        super().__init__(from_dictionary if from_dictionary else {}, **kwargs)

    def __setitem__(self, key, item):
        with self._lock:
            return super().__setitem__(key, item)

    def __getitem__(self, key):
        with self._lock:
            return super().__getitem__(key)


def cache_result(cache_location='fn'):
    """
    缓存结果装饰器。
    被缓存的函数会一直返回最后一次调用的结果，直至手动删除缓存的属性为止。
    缓存位置通过参数`cache_location`指定，当`cache_location`是`fn`时，缓存直接存储为`<decorated_fn>._cached_value`。
    如果`cache_location`由`self.`开头，则缓存储存为一个属性，属性名由参数决定，被装饰函数的首参数会被认作`self`处理。

    cache function return value for next time call.
    if cache_location is fn the cached result will be save as `<decorated_fn>._cached_value`.
    otherwise you can also save to `self.<attribute>`, the first arguments pass in will be regarded as the `self` object.

    :param cache_location: self.<attribute> or fn. default behavior is save as <decorated_fn>._cached_value.
    :return:
    """

    def wrapper(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            this = fn
            attr_name = '_cached_value'

            if cache_location.startswith('self.'):
                assert len(args) >= 1
                assert len(cache_location.split('.')) == 2

                attr_name = cache_location.split('.')[-1]
                this = args[0]

            if not getattr(this, attr_name, None):
                ret = fn(*args, **kwargs)
                setattr(this, attr_name, ret)
            return getattr(this, attr_name, None)

        return wrapped

    return wrapper


def deprecated(additional_message=None):  # pragma: no cover
    # just a message, doesn't need tests.

    def wrapper(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            additional = additional_message if additional_message else ''
            deprecated_message = 'Deprecated warning: ' \
                                 'beware, this function is deprecated, ' \
                                 '{} will removed in future version. {}'.format(fn.__name__, additional)
            logging.getLogger().warning(deprecated_message)
            return fn(*args, **kwargs)

        return wrapped

    return wrapper
