_conversions = {}


def convert_to_fit(val, field_type):
    val_available_conversions = {}

    if type(val) in _conversions:
        val_available_conversions = _conversions[type(val)]
    else:
        for parent_cls in type(val).mro():
            if parent_cls in _conversions:
                val_available_conversions = _conversions[parent_cls]

    if field_type in val_available_conversions:
        return val_available_conversions[field_type](val)
    else:
        for parent_cls in field_type.mro():
            if parent_cls in val_available_conversions:
                return val_available_conversions[parent_cls](val)

    raise ValueError('No conversion found for type {} to fit {}'.format(type(val), field_type))


def conversion(fit_type, field_type):
    def wrapper(fn):
        if fit_type in _conversions:
            _conversions[fit_type][field_type] = fn
        else:
            _conversions[fit_type] = {field_type: fn}
        return fn

    return wrapper
