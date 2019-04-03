import logging
from functools import wraps


def cache_result(cache_location='fn'):  # pragma: no cover
    # actually it's covered by tests.test_cache_result
    # but i don't know how make coverage.py thinks inside code has tested.
    # so let it go. just say no cover here.

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
