import pickle
import sqlite3
from collections.abc import MutableMapping
from pathlib import Path
from typing import Any, Optional, Union


class SQLiteLRUCache(MutableMapping):
    """SQLite3 LRU cache with optional TTL"""

    def __init__(
        self,
        maxsize: int,
        path: Optional[Union[Path, str]] = None,
        ttl: Optional[int] = None,
        clear_on_start=False,
    ):
        """

        maxsize
        getsizeof
        ttl: time to live in seconds
        """

        if not ((path is None) or isinstance(path, (str, Path))):
            raise TypeError("path must be str or None")

        if not ((ttl is None) or isinstance(ttl, int)):
            raise TypeError("ttl must be int or None")

        if not isinstance(maxsize, int):
            raise TypeError("maxsize must be int or None")

        # Absolute path to the cache
        self.path = Path(path).absolute() if path else Path(".") / "cache.db"
        self.ttl: Optional[int] = ttl
        self.maxsize = maxsize
        self.clear_on_start = clear_on_start

        # SQLite connection
        self.con = sqlite3.connect(str(self.path), check_same_thread=False)
        self.cursor = self.con.cursor()

        if clear_on_start:
            # Clear the cahce
            self.cursor.execute("drop table if exists cache;")

        # Enable reads while writing
        self.cursor.execute("PRAGMA journal_mode=WAL;")
        # Extend default timeout to 15 seconds
        self.cursor.execute("PRAGMA busy_timeout=15000;")

        # Create the table if it doesn't exist
        self.cursor.execute(
            """
        create table if not exists cache(
            key text primary key,
            value blob,
            created_at datetime not null default (strftime('%Y-%m-%d %H:%M:%f', 'NOW')),
            last_accessed_at datetime not null default (strftime('%Y-%m-%d %H:%M:%f', 'NOW'))
        );
        """
        )

        # Delete any existing expired entries
        self.__delete_expired_entries()

        self.con.commit()

    def __getitem__(self, key):
        self.__delete_expired_entries()

        entry = self.cursor.execute("select value from cache where key = ?", (key,)).fetchone()

        if entry is None:
            return self.__missing__(key)

        value = entry[0]

        value = pickle.loads(value)
        self.__update_last_accessed_at(key)
        return value

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

        self.cursor.execute(
            "insert or replace into cache(key, value) VALUES (?, ?)",
            (key, pickle.dumps(value)),
        )
        self.con.commit()

    def __delitem__(self, key):
        self.cursor.execute("delete from cache where key = ?", (key,))
        self.con.commit()

    def __contains__(self, key) -> bool:
        self.__delete_expired_entries()
        sql = "select count(key) from cache where key = ?"
        key_count = self.cursor.execute(sql, (key,)).fetchone()[0]
        if key_count == 0:
            return False
        return True

    def __len__(self):
        self.__delete_expired_entries()
        sql = "select count(key) as length from cache;"
        row = self.cursor.execute(sql).fetchone()
        self.con.commit()
        return row[0]

    def __iter__(self):
        self.__delete_expired_entries()
        sql = "select key from cache;"
        keys = self.cursor.execute(sql).fetchall()
        for (key,) in keys:
            yield key

    def items(self):
        self.__delete_expired_entries()
        for key in self.__iter__():
            try:
                value = self[key]
                yield key, value
            except KeyError:
                continue

    def keys(self):
        for key, _ in self.items():
            yield key

    def values(self):
        for _, value in self.items():
            yield value

    def popitem(self):
        """Remove and return the `(key, value)` pair least recently used."""

        sql = "select key from cache order by last_accessed_at asc limit 1"

        maybe_row = self.cursor.execute(sql).fetchone()

        if maybe_row is None:
            msg = "%s is empty" % self.__class__.__name__
            raise KeyError(msg) from None

        key = maybe_row[0]

        return (key, self.pop(key))

    def __update_last_accessed_at(self, key):
        """Update the last accessed date for a key to now"""
        sql = """
        update
            cache
        set
            last_accessed_at = current_timestamp
        where
            key = ?
        """
        self.cursor.execute(sql, (key,))
        self.con.commit()

    def __delete_expired_entries(self):
        """Delete entries with an expired ttl"""
        if self.ttl is None:
            return

        sql = """
        delete from cache
        where
            (
                cast(strftime('%s', current_timestamp) as integer) -
                cast(strftime('%s', last_accessed_at) as integer)
            ) > ?
        """
        self.cursor.execute(sql, (self.ttl,))
        self.con.commit()
