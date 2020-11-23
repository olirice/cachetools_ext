# cachetools_ext

<p>

<a href="https://github.com/olirice/cachetools_ext/actions"><img src="https://github.com/olirice/cachetools_ext/workflows/tests/badge.svg" alt="Tests" height="18"></a>
<a href="https://codecov.io/gh/olirice/cachetools_ext"><img src="https://codecov.io/gh/olirice/cachetools_ext/branch/master/graph/badge.svg" height="18"></a>
</p>

<p>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.6+-blue.svg" alt="Python version" height="18"></a>
  <a href="https://badge.fury.io/py/cachetools_ext"><img src="https://badge.fury.io/py/cachetools_ext.svg" alt="PyPI version" height="18"></a>
    <a href="https://github.com/olirice/cachetools_ext/blob/master/LICENSE"><img src="https://img.shields.io/pypi/l/markdown-subtemplate.svg" alt="License" height="18"></a>
    <a href="https://pypi.org/project/cachetools_ext/"><img src="https://img.shields.io/pypi/dm/cachetools_ext.svg" alt="Download count" height="18"></a>
</p>

---

**Source Code**: <a href="https://github.com/olirice/cachetools_ext" target="_blank">https://github.com/olirice/cachetools_ext</a>

---


An extension for [cachetools](https://github.com/tkem/cachetools)


### Installation:


```shell
pip install cachetools_ext
```


### Features:

**cachetools_ext.fs.FSLRUCache:**

- A `cachetools.cached` compatible file system backed LRU cache with optional TTL. Note, the cache key must be a string.
- Parameters:
  - `maxsize: int = maximum number of entries in the cache before evicting`
  - `path: Optional[Union[str, pathlib.Path]] = path to the sqlite database (does not need to exist)`
  - `ttl: Optional[int] = time to live in seconds`
  - `clear_on_start: bool = if true, clear the cache on instantiation`


### Usage:


```python
from pathlib import Path
from urllib import request
from cachetools import cached
from cachetools_ext.fs import FSLRUCache

@cached(cache=FSLRUCache(maxsize=32, ttl=360), key=lambda x: f'get_pep|num={x}')
def get_pep(num):
    """Lookup a Python Enhacement Proposals (PEP) by id"""
    url = 'http://www.python.org/dev/peps/pep-%04d/' % num
    with request.urlopen(url) as s:
        return s.read()
```
