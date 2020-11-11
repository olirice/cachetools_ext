import pytest

from cachetools_ext.fs import FSLRUCache


def test_set_get():
    cache = FSLRUCache(maxsize=3, clear_on_start=True)
    cache["hello"] = "world"
    assert cache["hello"] == "world"


def test_len():
    cache = FSLRUCache(maxsize=3, clear_on_start=True)
    assert len(cache) == 0
    cache["hello"] = "world"
    assert len(cache) == 1
    cache["hello"] = "world"
    assert len(cache) == 1
    cache["foo"] = "bar"
    assert len(cache) == 2


def test_del():
    cache = FSLRUCache(maxsize=3, clear_on_start=True)
    assert len(cache) == 0
    cache["hello"] = "world"
    assert len(cache) == 1
    del cache["hello"]
    assert len(cache) == 0


def test_contains():
    cache = FSLRUCache(maxsize=3, clear_on_start=True)
    assert "hello" not in cache
    cache["hello"] = "world"
    assert "hello" in cache


def test_popitem():
    cache = FSLRUCache(maxsize=3, clear_on_start=True)
    cache["hello"] = "world"
    cache["foo"] = "bar"
    key, val = cache.popitem()
    assert (key, val) == ("hello", "world")
    assert len(cache) == 1

    with pytest.raises(KeyError):
        cache.popitem()
        cache.popitem()


def test_last_access_update():
    cache = FSLRUCache(maxsize=3, clear_on_start=True)
    cache["hello"] = "world"
    cache["foo"] = "bar"

    # Access "hello" to make "foo" the oldest key to be accessed
    cache["hello"]

    key, val = cache.popitem()
    assert (key, val) == ("foo", "bar")


def test_itmes():
    cache = FSLRUCache(maxsize=3, clear_on_start=True)
    cache["hello"] = "world"

    for k, v in cache.items():
        assert k == "hello"
        assert v == "world"


def test_keys():
    cache = FSLRUCache(maxsize=3, clear_on_start=True)
    cache["hello"] = "world"

    keys = cache.keys()

    assert len([x for x in keys]) == 1

    for key in keys:
        assert key == "hello"


def test_values():
    cache = FSLRUCache(maxsize=3, clear_on_start=True)
    cache["hello"] = "world"
    cache["a"] = "b"

    values = cache.values()

    assert len([x for x in values]) == 2

    for value in values:
        assert value in ("world", "b")


def test_maxsize():
    cache = FSLRUCache(maxsize=3, clear_on_start=True)
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
    cache = FSLRUCache(maxsize=3, clear_on_start=True, ttl=0.1)
    cache["a"] = 1

    import time

    time.sleep(0.11)

    with pytest.raises(KeyError):
        res = cache["a"]


def test_input_validation():
    with pytest.raises(FileExistsError):
        FSLRUCache(maxsize=1, path="cache.db")

    with pytest.raises(TypeError):
        FSLRUCache(maxsize=1, path=1)

    with pytest.raises(TypeError):
        FSLRUCache(maxsize=1, ttl="1")

    with pytest.raises(TypeError):
        FSLRUCache(maxsize="1")


def test_current_size_too_big():
    cache = FSLRUCache(maxsize=0)

    with pytest.raises(ValueError):
        cache["a"] = 1


def test_items_keyerror_squashed():
    cache = FSLRUCache(maxsize=5)

    cache["a"] = 1
    cache["b"] = 2

    items = cache.items()

    del cache["b"]

    for k, v in items:
        assert True
