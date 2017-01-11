from cachual import CachualCache

from mock import MagicMock

import logging, sys

if (sys.version_info > (3, 0)):
    def unicode(value):
        return str(value)

    def long(value):
        return int(value)

KEY = "testKey"

def get_unit():
    unit = CachualCache()
    unit.put = MagicMock()
    unit.get = MagicMock()
    unit._get_key_from_func = MagicMock(return_value=KEY)

    logger = logging.getLogger("cachual")
    logger.addHandler(logging.StreamHandler(sys.stderr))
    logger.setLevel("DEBUG")

    return unit

def test_cache_get():
    unit = get_unit()
    test_value = "testing"
    unit.get.return_value = test_value

    @unit.cached()
    def test(a):
        return a

    assert test(test_value) == test_value
    unit.get.assert_called_with(KEY)

def test_cache_miss():
    unit = get_unit()
    unit.get.return_value = None
    test_value = "testing"
    
    @unit.cached()
    def test(a):
        return a

    assert test(test_value) == test_value
    unit.get.assert_called_with(KEY)
    unit.put.assert_called_with(KEY, test_value, None)

def test_cache_get_error():
    unit = get_unit()
    unit.get.side_effect = Exception("test")
    test_value = "testing"

    @unit.cached()
    def test(a):
        return a

    assert test(test_value) == test_value
    unit.get.assert_called_with(KEY)
    unit.put.assert_called_with(KEY, test_value, None)

def test_cache_put_error():
    unit = get_unit()
    test_value = "testing"
    unit.get.return_value = None
    unit.put.side_effect = Exception("test")

    @unit.cached()
    def test(a):
        return a

    assert test(test_value) == test_value
    unit.get.assert_called_with(KEY)
    unit.put.assert_called_with(KEY, test_value, None)

def test_cache_put():
    unit = get_unit()
    test_value = "testing"
    unit.get.return_value = None

    @unit.cached()
    def test(a):
        return a

    assert test(test_value) == test_value
    unit.get.assert_called_with(KEY)
    unit.put.assert_called_with(KEY, test_value, None)

def test_cache_put_ttl():
    unit = get_unit()
    test_value = "testing"
    ttl = 15
    unit.get.return_value = None

    @unit.cached(ttl=ttl)
    def test(a):
        return a

    assert test(test_value) == test_value
    unit.get.assert_called_with(KEY)
    unit.put.assert_called_with(KEY, test_value, ttl)

def test_cache_get_unpack():
    unit = get_unit()
    test_cache_get = "testingCacheGet"
    test_value = "testing"

    unit.get.return_value = test_cache_get
    unpack = MagicMock()
    unpack.return_value = "testing"

    @unit.cached(unpack=unpack)
    def test(a):
        return a

    assert test(test_value) == test_value
    unit.get.assert_called_with(KEY)
    unpack.assert_called_with(test_cache_get)

def test_cache_get_unpack_error():
    unit = get_unit()
    test_cache_get = "testingCacheGet"
    test_value = "testing"

    unit.get.return_value = test_cache_get
    unpack = MagicMock()
    unpack.side_effect = Exception("test")

    @unit.cached(unpack=unpack)
    def test(a):
        return a

    assert test(test_value) == test_value
    unit.get.assert_called_with(KEY)
    unpack.assert_called_with(test_cache_get)
    unit.put.assert_called_with(KEY, test_value, None)

def test_cache_put_pack():
    unit = get_unit()
    test_value = "testing"
    pack_return_value = "packed"

    unit.get.return_value = None 
    pack = MagicMock()
    pack.return_value = pack_return_value

    @unit.cached(pack=pack)
    def test(a):
        return a

    assert test(test_value) == test_value
    unit.get.assert_called_with(KEY)
    pack.assert_called_with(test_value)
    unit.put.assert_called_with(KEY, pack_return_value, None)

def test_cache_put_pack_error():
    unit = get_unit()
    test_value = "testing"
    pack_return_value = "packed"

    unit.get.return_value = None 
    pack = MagicMock()
    pack.side_effect = Exception("test")

    @unit.cached(pack=pack)
    def test(a):
        return a

    assert test(test_value) == test_value
    unit.get.assert_called_with(KEY)
    pack.assert_called_with(test_value)
    unit.put.assert_has_calls([])
