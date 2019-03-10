import logging
from functools import wraps


def cache_result(cache_location='fn'):
    """
    cache function return value for next time call. if cache_location is fn the cached result will be save as `<decorated_fn>._cached_value`.
    otherwise you can also save to `self.<attribute>`, the first arguments pass in will be regarded as the `self` object.

    :param cache_location: self.<attribute> or fn. default behavior is save as <decorated_fn>._cached_value.
    :return:
    """

    def wrapper(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            self = fn
            attr_name = '_cached_value'

            if cache_location.startswith('self.'):
                assert len(args) >= 1
                assert len(cache_location.split('.')) == 2

                attr_name = cache_location.split('.')[-1]
                self = args[0]

            if getattr(self, attr_name, None):
                ret = fn(*args, **kwargs)
                setattr(self, attr_name, ret)
            return getattr(self, attr_name, None)

        return wrapped

    return wrapper


def deprecated(additional_message):
    def wrapper(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            deprecated_message = 'Deprecated warning: ' \
                                 'beware, this function is deprecated, ' \
                                 '{} will removed in future version. {}'.format(fn.__name__, additional_message)
            logging.getLogger().warning(deprecated_message)
            return fn(*args, **kwargs)

        return wrapped

    return wrapper
