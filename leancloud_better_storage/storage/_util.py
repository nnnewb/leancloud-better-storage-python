import logging
from functools import wraps


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
