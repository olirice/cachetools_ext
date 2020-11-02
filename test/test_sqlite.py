from pathlib import Path

import pytest

from cachetools_ext.sqlite import SQLiteLRUCache


def test_set_get():
    cache = SQLiteLRUCache(maxsize=3, clear_on_start=True)
    cache["hello"] = "world"
    assert cache["hello"] == "world"


def test_len():
    cache = SQLiteLRUCache(maxsize=3, clear_on_start=True)
    assert len(cache) == 0
    cache["hello"] = "world"
    assert len(cache) == 1
    cache["hello"] = "world"
    assert len(cache) == 1
    cache["foo"] = "bar"
    assert len(cache) == 2


def test_del():
    cache = SQLiteLRUCache(maxsize=3, clear_on_start=True)
    assert len(cache) == 0
    cache["hello"] = "world"
    assert len(cache) == 1
    del cache["hello"]
    assert len(cache) == 0


def test_contains():
    cache = SQLiteLRUCache(maxsize=3, clear_on_start=True)
    assert "hello" not in cache
    cache["hello"] = "world"
    assert "hello" in cache


def test_popitem():
    cache = SQLiteLRUCache(maxsize=3, clear_on_start=True)
    cache["hello"] = "world"
    cache["foo"] = "bar"
    key, val = cache.popitem()
    assert (key, val) == ("hello", "world")
    assert len(cache) == 1

    with pytest.raises(KeyError):
        cache.popitem()
        cache.popitem()


def test_last_access_update():
    cache = SQLiteLRUCache(maxsize=3, clear_on_start=True)
    cache["hello"] = "world"

    last_accessed_at, created_at = cache.cursor.execute(
        """
    select
        last_accessed_at, created_at
    from
        cache
    limit 1
    """
    ).fetchone()

    assert last_accessed_at == created_at

    _ = cache["hello"]

    is_greater = cache.cursor.execute(
        """
    select
        last_accessed_at > created_at
    from
        cache
    limit 1
    """
    ).fetchone()

    assert is_greater


def test_itmes():
    cache = SQLiteLRUCache(maxsize=3, clear_on_start=True)
    cache["hello"] = "world"

    for k, v in cache.items():
        assert k == "hello"
        assert v == "world"


def test_keys():
    cache = SQLiteLRUCache(maxsize=3, clear_on_start=True)
    cache["hello"] = "world"

    keys = cache.keys()

    assert len([x for x in keys]) == 1

    for key in keys:
        assert key == "hello"


def test_values():
    cache = SQLiteLRUCache(maxsize=3, clear_on_start=True)
    cache["hello"] = "world"
    cache["a"] = "b"

    values = cache.values()

    assert len([x for x in values]) == 2

    for value in values:
        assert value in ("world", "b")


def test_maxsize():
    cache = SQLiteLRUCache(maxsize=3, clear_on_start=True)
    cache["a"] = 1
    cache["b"] = 2
    cache["c"] = 3
    assert len(cache) == 3
    cache["d"] = 4
    assert len(cache) == 3
    values = [x for x in cache.values()]
    assert 2 in values
    assert 3 in values
    assert 4 in values


def test_ttl():
    cache = SQLiteLRUCache(maxsize=3, clear_on_start=True, ttl=5)
    cache["a"] = 1

    cache.cursor.execute(
        """
    update cache set last_accessed_at = datetime(last_accessed_at, '-1 year');
    """
    )

    with pytest.raises(KeyError):
        res = cache["a"]


def test_input_validation():
    SQLiteLRUCache(maxsize=1, path="cache.db")
    SQLiteLRUCache(maxsize=1, path=Path("cache.db"))
    with pytest.raises(TypeError):
        SQLiteLRUCache(maxsize=1, path=1)

    with pytest.raises(TypeError):
        SQLiteLRUCache(maxsize=1, ttl="1")

    with pytest.raises(TypeError):
        SQLiteLRUCache(maxsize="1")


def test_current_size_too_big():
    cache = SQLiteLRUCache(maxsize=0)

    with pytest.raises(ValueError):
        cache["a"] = 1


def test_items_keyerror_squashed():
    cache = SQLiteLRUCache(maxsize=5)

    cache["a"] = 1
    cache["b"] = 2

    items = cache.items()

    del cache["b"]

    for k, v in items:
        assert True
