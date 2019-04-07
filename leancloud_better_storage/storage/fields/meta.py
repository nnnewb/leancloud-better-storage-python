class MetaField(type):

    def __new__(mcs, name, bases, attributes):
        created = type.__new__(mcs, name, bases, attributes)
        created.__hash__ = object.__hash__
        return created
