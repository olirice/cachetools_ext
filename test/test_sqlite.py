from cachetools_ext.sqlite import SQLiteLRUCache
import time


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

    values = cache.values()

    assert len([x for x in values]) == 1

    for value in values:
        assert value == "world"
