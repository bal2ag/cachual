Cachual
=======

.. image:: https://secure.travis-ci.org/bal2ag/cachual.png?branch=master
    :target: http://travis-ci.org/bal2ag/cachual
    :alt: Build

.. image:: https://readthedocs.org/projects/cachual/badge/?version=latest&style
    :target: http://cachual.readthedocs.org/
    :alt: Documentation Status

.. image:: https://coveralls.io/repos/github/bal2ag/cachual/badge.svg?branch=master
    :target: https://coveralls.io/github/bal2ag/cachual?branch=master
    :alt: Coverage

Cachual provides an easy way to cache the return values of your Python
functions with a simple decorator::

    from cachual import RedisCache
    cache = RedisCache()

    @cache.cached(ttl=360)
    def get_user_email(user_id):
        ...

Installation
------------

Installation is very easy with pip::

    pip install Cachual

Docs
----

Check out the full
`documentation <http://cachual.readthedocs.io/en/latest/overview.html>`_.
