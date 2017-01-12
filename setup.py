"""
Cachual
-------

Cachual is a simple library that makes it easy to cache the return values from
your python functions with an annotation::

    cache = RedisCache()
    
    @cache.cached(ttl=900)
    def is_user_valid(user_id):
        ...
"""
import ast, re

from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('cachual.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='Cachual',
    version=version,
    url='https://github.com/bal2ag/cachual',
    license='BSD',
    author='Alex Landau',
    author_email='balexlandau@gmail.com',
    description='Simple annotation-based caching for your functions',
    long_description=__doc__,
    py_modules=['cachual'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'pymemcache>=1.4.0',
        'redis>=2.10',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
