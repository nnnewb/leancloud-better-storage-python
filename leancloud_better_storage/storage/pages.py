from copy import deepcopy


class Pages(object):
    """ pages iterator """

    def __init__(self, query, page, size):
        """
        constructor of Pages class

        :param query: select query
        :type query: leancloud_better_storage.storage.query.Query
        :param page: current page
        :type page: int
        :param size: elements size per page
        :type size: int
        """
        self._query = deepcopy(query)
        self._page = page
        self._size = size
        self._content_cache = []
        self._total = None

    @property
    def element_offset(self):
        """ get element offset. """
        return (self._page - 1) * self._size

    @property
    def items(self):
        """ get all element of current page. """
        if len(self._content_cache) == 0:
            query = deepcopy(self._query)
            self._content_cache = query.find(self.element_offset, self._size)
        return self._content_cache

    @property
    def total_pages(self):
        if self._total is None:
            self._total = self._query.count() / self._size
        return self._total

    def __iter__(self):
        """ get iterator """
        return self

    def __next__(self):
        """ go next page """
        self._page += 1
        self._content_cache = []

        if len(self.items) == 0:
            raise StopIteration()

        return self
