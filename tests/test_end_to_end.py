from cachual import CachualCache

from mock import MagicMock

import hashlib

class FakeCache(CachualCache):
    def __init__(self):
        pass
    get = MagicMock(return_value=None)
    put = MagicMock()
    logger = MagicMock()

def get_unit():
    return FakeCache()

def get_hash(value):
    m = hashlib.md5()
    m.update(value.encode('utf-8'))
    return m.hexdigest()

def test_function():
    unit = get_unit()

    @unit.cached()
    def testing(a, b):
        return 'test'
    
    a = 'a'
    b = 'b'
    expected_key = get_hash('test_end_to_end.testing(a, b=b)')
    testing(a, b=b)

    unit.get.assert_called_with(expected_key)
    unit.put.assert_called_with(expected_key, 'test', None)

def test_classmethod():
    unit = get_unit()

    class Test(object):
        def __init__(self):
            pass
        @classmethod
        @unit.cached()
        def testing(cls, a, b):
            return 'test'
    
    a = 'a'
    b = 'b'
    expected_key = get_hash('test_end_to_end.testing(%s, a, b=b)' % Test)
    Test().testing(a, b=b)

    unit.get.assert_called_with(expected_key)
    unit.put.assert_called_with(expected_key, 'test', None)

def test_instancemethod():
    unit = get_unit()

    class Test(object):
        def __init__(self):
            pass
        
        @unit.cached()
        def testing(self, a, b):
            return 'test'
    
    a = 'a'
    b = 'b'
    t = Test()
    expected_key = get_hash('test_end_to_end.testing(%s, a, b=b)' % t)
    t.testing(a, b=b)

    unit.get.assert_called_with(expected_key)
    unit.put.assert_called_with(expected_key, 'test', None)

def test_subclass_classmethod():
    unit = get_unit()

    class Test(object):
        def __init__(self):
            pass
        @classmethod
        @unit.cached()
        def testing(cls, a, b):
            return 'test'

    class SubTest(Test):
        def __init__(self):
            pass
    
    a = 'a'
    b = 'b'
    expected_key = get_hash('test_end_to_end.testing(%s, a, b=b)' % SubTest)
    SubTest().testing(a, b=b)

    unit.get.assert_called_with(expected_key)
    unit.put.assert_called_with(expected_key, 'test', None)


def test_subclass_instancemethod():
    unit = get_unit()

    class Test(object):
        def __init__(self):
            pass
        
        @unit.cached()
        def testing(cls, a, b):
            return 'test'

    class SubTest(Test):
        def __init__(self):
            pass
    
    a = 'a'
    b = 'b'
    t = SubTest()
    expected_key = get_hash('test_end_to_end.testing(%s, a, b=b)' % t)
    t.testing(a, b=b)

    unit.get.assert_called_with(expected_key)
    unit.put.assert_called_with(expected_key, 'test', None)

def test_instancemethod_use_class_for_self():
    unit = get_unit()

    class Test(object):
        def __init__(self):
            pass
        
        @unit.cached(use_class_for_self=True)
        def testing(self, a, b):
            return 'test'
    
    a = 'a'
    b = 'b'
    t = Test()
    expected_key = get_hash('test_end_to_end.testing(%s, a, b=b)' % Test)
    t.testing(a, b=b)

    unit.get.assert_called_with(expected_key)
    unit.put.assert_called_with(expected_key, 'test', None)

def test_subclass_instancemethod_use_class_for_self():
    unit = get_unit()

    class Test(object):
        def __init__(self):
            pass
        
        @unit.cached(use_class_for_self=True)
        def testing(cls, a, b):
            return 'test'

    class SubTest(Test):
        def __init__(self):
            pass
    
    a = 'a'
    b = 'b'
    t = SubTest()
    expected_key = get_hash('test_end_to_end.testing(%s, a, b=b)' % SubTest)
    t.testing(a, b=b)

    unit.get.assert_called_with(expected_key)
    unit.put.assert_called_with(expected_key, 'test', None)
