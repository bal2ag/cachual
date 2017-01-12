from cachual import MemcachedCache

from mock import MagicMock, mock

@mock.patch('cachual.MemcachedClient')
def test_ctor(mock_memcached):
    host = "host"
    port = 1234

    mock_memcached.return_value = "test"
    unit = MemcachedCache(host, port)

    mock_memcached.assert_called_with((host, port))
    assert unit.client == "test"

@mock.patch('cachual.MemcachedClient')
def test_get(mock_memcached):
    client = MagicMock()
    client.get = MagicMock()
    mock_memcached.return_value = client
    key = "test"

    unit = MemcachedCache()
    unit.get(key)
    client.get.assert_called_with(key)

@mock.patch('cachual.MemcachedClient')
def test_put(mock_memcached):
    client = MagicMock()
    client.set = MagicMock()
    mock_memcached.return_value = client
    key = "test"
    value = "value"
    ttl = 5

    unit = MemcachedCache()
    unit.put(key, value, ttl)
    client.set.assert_called_with(key, value, expire=ttl)

@mock.patch('cachual.MemcachedClient')
def test_put_no_ttl(mock_memcached):
    client = MagicMock()
    client.set = MagicMock()
    mock_memcached.return_value = client
    key = "test"
    value = "value"

    unit = MemcachedCache()
    unit.put(key, value)
    client.set.assert_called_with(key, value, expire=0)
