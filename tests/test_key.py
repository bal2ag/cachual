# -*- coding: utf-8 -*-
from cachual import CachualCache

from mock import MagicMock

import hashlib, sys

def get_unit():
    return CachualCache()

def get_hash(value):
    m = hashlib.md5()
    m.update(value.encode('utf-8'))
    return m.hexdigest()

def test_no_args():
    def test():
        pass
    test.__module__ = 'test.module'

    key = get_unit()._get_key_from_func(test, None, None)
    assert key == get_hash('test.module.test()')

def test_positional_args():
    def test(a, b):
        pass
    test.__module__ = 'test.module'

    key = get_unit()._get_key_from_func(test, [1, 2], None)
    assert key == get_hash('test.module.test(1, 2)')

def test_kwargs():
    def test(a, b):
        pass
    test.__module__ = 'test.module'

    key = get_unit()._get_key_from_func(test, None,
            {'a': "test1", 'b': "test2"})
    assert key == get_hash('test.module.test(a=test1, b=test2)')

def test_positional_and_kwargs():
    def test(a, b):
        pass
    test.__module__ = 'test.module'

    key = get_unit()._get_key_from_func(test, ['test1'], {'b': "test2"})
    assert key == get_hash('test.module.test(test1, b=test2)')

def test_unicode():
    def test(a):
        pass
    test.__module__ = 'test.module'

    utf8_str = '«ταБЬℓσ»'
    if (sys.version_info > (3, 0)): # Handling for Python 3; str is unicode
        uni = utf8_str
    else:
        uni = utf8_str.decode('utf-8')

    key = get_unit()._get_key_from_func(test, [utf8_str], None)
    assert key == get_hash('test.module.test(%s)' % uni)
