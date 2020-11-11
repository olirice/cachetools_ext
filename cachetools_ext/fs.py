import datetime
import os
import pickle
import shutil
from collections.abc import MutableMapping
from pathlib import Path
from typing import Any, Optional, Union


class FSLRUCache(MutableMapping):
    """Filesystem LRU cache with optional TTL"""

    def __init__(
        self,
        maxsize: int,
        path: Optional[Union[Path, str]] = None,
        ttl: Optional[Union[int, float]] = None,
        clear_on_start=False,
    ):
        if not ((path is None) or isinstance(path, (str, Path))):
            raise TypeError("path must be str or None")

        if not ((ttl is None) or isinstance(ttl, (int, float))):
            raise TypeError("ttl must be int, float or None")

        if not isinstance(maxsize, int):
            raise TypeError("maxsize must be int or None")

        # Absolute path to the cache
        path = Path(path).absolute() if path else Path(".") / "cache/"

        if not path.is_dir():
            raise ValueError("path must be a directory")

        # Create the directory if not exists
        path.mkdir(parents=True, exist_ok=True)

        self.path = path
        self.ttl: Optional[int] = ttl
        self.maxsize = maxsize
        self.clear_on_start = clear_on_start

        if clear_on_start:
            # Clear the cache
            shutil.rmtree(self.path)
            path.mkdir(parents=True, exist_ok=True)

        # Delete any existing expired entries
        self.__delete_expired_entries()

    def key_to_path(self, key) -> Path:
        return self.path / f"{key}.pkl"

    def path_to_key(self, path) -> str:
        return path.name.strip(".pkl")

    def __getitem__(self, key):
        self.__delete_expired_entries()
        value_path = self.key_to_path(key)
        try:
            value = pickle.loads(value_path.read_bytes())
            return value
        except Exception:
            pass
        return self.__missing__(key)

    def __missing__(self, key):
        raise KeyError(key)

    def __setitem__(self, key: Any, value: Any) -> None:
        self.__delete_expired_entries()
        value_size = 1

        current_size = len(self)

        if value_size > self.maxsize:
            raise ValueError("value too large")

        while current_size + value_size > self.maxsize:
            self.popitem()
            current_size = len(self)

        value_path = self.key_to_path(key)
        value_path.write_bytes(pickle.dumps(value))

    def __delitem__(self, key):
        value_path = self.key_to_path(key)

        try:
            value_path.unlink()
        except Exception:
            pass

    def __contains__(self, key) -> bool:
        self.__delete_expired_entries()
        value_path = self.key_to_path(key)

        if value_path.is_file():
            return True
        return False

    def __len__(self):
        self.__delete_expired_entries()
        return len([x for x in self.path.glob("*")])

    def __iter__(self):
        self.__delete_expired_entries()
        for x in self.path.glob("*"):
            yield self.path_to_key(x)

    def items(self):
        self.__delete_expired_entries()
        for key in self.__iter__():
            try:
                value = self[key]
                yield key, value
            except KeyError:
                continue

    def keys(self):
        for key in self:
            yield key

    def values(self):
        for _, value in self.items():
            yield value

    def popitem(self):
        """Remove and return the `(key, value)` pair least recently used."""
        file_to_ts = {path: os.stat(path).st_atime_ns for path in self.path.glob("*")}

        ordered_file_to_ts = sorted(file_to_ts.items(), key=lambda x: x[1])
        for path, ts in ordered_file_to_ts:
            try:
                key = self.path_to_key(path)
                return (key, self.pop(key))
            except KeyError:
                pass
        raise KeyError("Cache is empty")

    def __delete_expired_entries(self):
        """Delete entries with an expired ttl"""
        if self.ttl is None:
            return

        now = datetime.datetime.now().timestamp()

        for path in self.path.glob("*"):
            try:
                created_ts = os.stat(path).st_ctime
            except FileNotFoundError:
                continue

            print(now, created_ts)

            if now - created_ts > self.ttl:
                try:
                    path.unlink()
                except FileNotFoundError:
                    continue
