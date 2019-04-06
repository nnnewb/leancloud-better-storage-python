from leancloud_better_storage.storage._util import cache_result


def test_cache_result():
    a = 0

    def gen():
        nonlocal a
        a += 1
        return a

    def fn():
        # HighCostConstruction()
        return gen()

    fn = cache_result()(fn)
    assert fn() == 1
    assert fn() == 1

    def fn(self):
        return gen()

    class SomeCls:

        @cache_result('self._cache_attr')
        def fn(self):
            return gen()

    someobj = SomeCls()

    assert someobj.fn() == 2
    assert someobj.fn() == 2
    assert hasattr(someobj, '_cache_attr')
    assert getattr(someobj, '_cache_attr') == 2
