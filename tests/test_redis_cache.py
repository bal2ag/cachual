from cachual import RedisCache

from mock import MagicMock, mock

@mock.patch('cachual.StrictRedis')
def test_ctor(mock_redis):
    host = "host"
    port = 1234
    db = 10

    mock_redis.return_value = "test"
    unit = RedisCache(host=host, port=port, db=db)

    mock_redis.assert_called_with(host=host, port=port, db=db)
    assert unit.client == "test"

@mock.patch('cachual.StrictRedis')
def test_get(mock_redis):
    client = MagicMock()
    client.get = MagicMock()
    mock_redis.return_value = client
    key = "test"

    unit = RedisCache()
    unit.get(key)
    client.get.assert_called_with(key)

@mock.patch('cachual.StrictRedis')
def test_put(mock_redis):
    client = MagicMock()
    client.set = MagicMock()
    mock_redis.return_value = client
    key = "test"
    value = "value"
    ttl = 5

    unit = RedisCache()
    unit.put(key, value, ttl)
    client.set.assert_called_with(key, value, ex=ttl)

@mock.patch('cachual.StrictRedis')
def test_put_no_ttl(mock_redis):
    client = MagicMock()
    client.set = MagicMock()
    mock_redis.return_value = client
    key = "test"
    value = "value"

    unit = RedisCache()
    unit.put(key, value)
    client.set.assert_called_with(key, value, ex=None)
