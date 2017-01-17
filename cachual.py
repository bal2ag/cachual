import logging, json, sys, hashlib

if (sys.version_info > (3, 0)):
    def long(value):
        return int(value)

from functools import wraps

from redis import StrictRedis
from pymemcache.client.base import Client as MemcachedClient

__version__ = '0.2.2'

class CachualCache(object):
    """Base class for all cache implementations. Provides the
    :meth:`~CachualCache.cached` decorator which can be applied to methods
    whose return value you want to cache. This class should not be used
    directly, and is meant to be subclassed.

    Subclasses should define a **get** method, which takes a single string
    argument, and returns the value in the cache for that key, or ``None`` in
    the case of a cache miss; and a **put** method, which takes three arguments
    for the cache key, the value to store, and a TLL (which may be none) and
    puts the value in the cache.
    """
    def __init__(self):
        self.logger = logging.getLogger("cachual")

    def cached(self, ttl=None, pack=None, unpack=None,
            use_class_for_self=False):
        """Functions decorated with this will have their return values cached.
        It should be used as follows::

            cache = RedisCache()

            @cache.cached()
            def method_to_be_cached(arg1, arg2, arg3='default'):
                ...

        A unique cache key will be generated for each function call, so that
        different values for the arguments will result in different cache keys.
        When you decorate a function with this, the cache will be checked
        first; if there is a cache hit, the value in the cache will be
        returned. Otherwise, the function is executed and the return value is
        put into the cache.

        Cache get/put failures are logged but ignored; if the cache goes down,
        the function will continue to execute as normal.

        :type ttl: integer
        :param ttl: The time-to-live in seconds. For caches that support TTLs,
                    the keys will expire after this time. If None (the
                    default), the cache default will be used (usually no
                    expiration).

        :type pack: function
        :param pack: If specified, this function will be called with the
                     decorated function's return value, and the result will be
                     stored in the cache. This can be used to alter the value
                     that actually gets stored in the cache in case you need to
                     process it first (e.g. dump a JSON string that is properly
                     escaped).

        :type unpack: function
        :param unpack: If specified, this function will be called with the
                       value from the cache in the event of a cache hit, and
                       the result will be returned to the caller. This can be
                       used to alter the value that gets returned from a cache
                       hit, in case you need to process it first (e.g. turn a
                       JSON string into a Python dictionary).

        :type use_class_for_self: bool
        :param use_class_for_self: If True, cache keys will use the class
                                   representation of the first parameter
                                   instead of the object representation. This
                                   is useful when you want to cache instance
                                   methods, but you want the same cache key if
                                   the instance method's arguments are the same.
                                   An example would be a stateless class that
                                   is a client wrapper for an external service.
                                   The first argument would be the instance
                                   object, whose default representation
                                   contains the memory location of the object
                                   (and thus would be different for every
                                   instance, which is undesirable for a
                                   stateless class).

        .. versionchanged:: 0.2.2
           Added ``use_class_for_self`` parameter.
        """
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                key = self._get_key_from_func(f, args, kwargs,
                        use_class_for_self)
                self.logger.debug("key: [%s]" % key)
                try:
                    value = self.get(key)
                    if value is not None:
                        self.logger.debug("got value from cache: %s" % value)
                        if unpack is not None:
                            return unpack(value)
                        return value
                except:
                    self.logger.warn("Error getting value", exc_info=1)

                self.logger.debug("no value from cache, calling function")
                value = f(*args, **kwargs)
                self.logger.debug("got value from function call: %s" % value)
                try:
                    packed = value if pack is None else pack(value)
                    self.put(key, packed, ttl)
                except:
                    self.logger.warn("Error putting value", exc_info=1)
                return value
            return decorated
        return decorator

    def _get_key_from_func(self, f, args, kwargs, use_class_for_self=False):
        """Internal function to build the cache key from the function and the
        args and kwargs it was called with."""
        if use_class_for_self:
            # For instance methods, the first argument will be an object,
            # whose representation will include a memory location and result in
            # a new cache key for every instance. This behavior may be
            # undesirable, especially if the class instances are stateless.
            # use_class_from_self can be used to use the class instead of the
            # object for the first argument.
            args = [args[0].__class__] + list(args[1:])

        if args:
            args_str = ', '.join([_unicode(a) for a in args])
        else:
            args_str = None
        if kwargs:
            kwargs_str = ', '.join(\
                    ['%s=%s' % (_unicode(k), _unicode(kwargs[k]))\
                    for k in sorted(kwargs.keys())])
        else:
            kwargs_str = None

        prefix = f.__module__ + '.' + f.__name__
        suffix = ''
        if args_str is not None:
            suffix = '(' + args_str
            if kwargs_str is not None:
                suffix = suffix + ', ' + kwargs_str + ')'
            else:
                suffix = suffix + ')'
        else:
            if kwargs_str is not None:
                suffix = '(' + kwargs_str + ')'
            else:
                suffix = '()'

        m = hashlib.md5()
        key = ('%s%s' % (prefix, suffix)).encode('utf-8')
        self.logger.debug('prehash key: [%s]' % key)
        m.update(key)
        return m.hexdigest()

class RedisCache(CachualCache):
    """A cache using `Redis <https://redis.io/>`_ as the backing cache. All
    values will be stored as strings, meaning if you try to store non-string
    values in the cache, their unicode equivalent will be stored. If you want
    to alter this behavior e.g. to store Python dictionaries, use the
    pack/unpack arguments when you specify your @cached decorator.

    :type host: string
    :param host: The Redis host to use for the cache.

    :type port: integer
    :param port: The port to use for the Redis server.

    :type db: integer
    :param db: The Redis database to use on the server for the cache.

    :type kwargs: dict
    :param kwargs: Any additional args to pass to the :class:`CachualCache`
                   constructor.
    """
    def __init__(self, host='localhost', port=6379, db=0, **kwargs):
        super(RedisCache, self).__init__(**kwargs)
        self.client = StrictRedis(host=host, port=port, db=db)

    def get(self, key):
        """Get a value from the cache using the given key.

        :type key: string
        :param key: The cache key to get the value for.

        :returns: The value for the cache key, or None in the case of cache
                  miss.
        """
        return self.client.get(key)

    def put(self, key, value, ttl=None):
        """Put a value into the cache at the given key. If the value is not a
        string, its unicode value will be used. This behavior is defined by the
        underlying Redis library, and could be subject to change in future
        versions; thus it is safest to only store strings in Redis (although
        basic types should serialize into a string cleanly, you will need to
        unpack them when they are retrieved from the cache).

        :type key: string
        :param key: The cache key to use for the value.

        :param value: The value to store in the cache.

        :type ttl: integer
        :param ttl: The time-to-live for key in seconds, after which it will
                    expire.
        """
        self.client.set(key, value, ex=ttl)

class MemcachedCache(CachualCache):
    """A cache using `Memcached <https://memcached.org/>`_ as the backing
    cache. The same caveats apply to keys and values as for Redis - you should
    only try to store strings (using the packing/unpacking functions). See the
    documentation on Keys and Values here:
    :class:`pymemcache.client.base.Client`.

    :type host: string
    :param host: The Memcached host to use for the cache.

    :type port: integer
    :param port: The port to use for the Memcached server.

    :type kwargs: dict
    :param kwargs: Any additional args to pass to the :class:`CachualCache`
                   constructor.
    """
    def __init__(self, host='localhost', port=11211, **kwargs):
        super(MemcachedCache, self).__init__(**kwargs)
        self.client = MemcachedClient((host, port))

    def get(self, key):
        """Get a value from the cache using the given key.

        :type key: string
        :param key: The cache key to get the value for.

        :returns: The value for the cache key, or None in the case of cache
                  miss.
        """
        return self.client.get(key)

    def put(self, key, value, ttl=None):
        """Put a value into the cache at the given key. For constraints on keys
        and values, see :class:`pymemcache.client.base.Client`.

        :type key: string
        :param key: The cache key to use for the value.

        :param value: The value to store in the cache.

        :type ttl: integer
        :param ttl: The time-to-live for key in seconds, after which it will
                    expire.
        """
        if ttl is None:
            ttl = 0
        self.client.set(key, value, expire=ttl)

def pack_json(value):
    """Pack the given JSON structure for storage in the cache by dumping it as
    a JSON string.

    :param value: The JSON structure (e.g. dict, list) to pack.

    :rtype: string
    :returns: The JSON structure as a JSON string.
    """
    return json.dumps(value)

def unpack_json(value):
    """Unpack the given string by loading it as JSON.

    :type value: string
    :param value: The string to unpack.

    :returns: The string as JSON.
    """
    return json.loads(value)

def unpack_json_python3(value):
    """Unpack the given Python 3 bytes by loading them as JSON.

    :type value: bytes
    :param value: The bytes to unpack.

    :returns: The bytes as JSON.
    """
    return unpack_json(value.decode('utf-8'))

def unpack_bytes(value):
    """Unpack the given Python 3 bytes by loading them as a Python 3 unicode
    string, assuming UTF-8 encoding.

    :type value: bytes
    :param value: The bytes to unpack.

    :returns: The bytes as a Python 3 unicode string, assuming UTF-8 encoding.
    """
    return value.decode('utf-8')

def unpack_int(value):
    """Unpack the given string into an integer.

    :type value: string
    :param value: The string to unpack.

    :rtype: integer
    :returns: The string as an integer.
    """
    return int(value)

def unpack_long(value):
    """Unpack the given string into a long.

    :type value: string
    :param value: The string to unpack.

    :rtype: long
    :returns: The string as a long.
    """
    return long(value)

def unpack_float(value):
    """Unpack the given string into a float.

    :type value: string
    :param value: The string to unpack.

    :rtype: float
    :returns: The string as a float.
    """
    return float(value)

def unpack_bool(value):
    """Unpack the given string into a boolean. 'True' will become True, and
    'False' will become False (as per the unicode values of booleans); anything
    else will result in a ValueError.

    :type value: string
    :param value: The string to unpack.

    :rtype: bool
    :returns: The string as a boolean.
    """
    if value == 'True':
         return True
    elif value == 'False':
         return False
    raise ValueError("Cannot convert %s to bool" % value)

def _unicode(value):
    """Helper function to return the value as a unicode, regardless of the
    Python version of the type of the value."""
    if (sys.version_info > (3, 0)): # Handling for Python 3; str is unicode
        return str(value)

    if isinstance(value, unicode):
        return value
    return unicode(str(value), encoding='utf-8')
