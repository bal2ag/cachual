from cachual import CachualCache

from mock import MagicMock

def get_unit():
    return CachualCache()

def test_no_args():
    def test():
        pass
    test.__module__ = 'test.module'

    key = get_unit()._get_key_from_func(test, None, None)
    assert key == 'test.module.test()'

def test_positional_args():
    def test(a, b):
        pass
    test.__module__ = 'test.module'

    key = get_unit()._get_key_from_func(test, [1, 2], None)
    assert key == 'test.module.test(1, 2)'

def test_kwargs():
    def test(a, b):
        pass
    test.__module__ = 'test.module'

    key = get_unit()._get_key_from_func(test, None,
            {'a': "test1", 'b': "test2"})
    assert key == 'test.module.test(a=test1, b=test2)'

def test_positional_and_kwargs():
    def test(a, b):
        pass
    test.__module__ = 'test.module'

    key = get_unit()._get_key_from_func(test, ['test1'], {'b': "test2"})
    assert key == 'test.module.test(test1, b=test2)'
