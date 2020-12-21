import pickle
from collections.abc import MutableMapping
from typing import Any


class S3Cache(MutableMapping):
    """AWS S3 basic Cache"""

    def __init__(
        self,
        maxsize: int,
        s3_client: Any,
        bucket: str,
        key_prefix: str = "",
    ):
        if not isinstance(maxsize, int):
            raise TypeError("maxsize must be int or None")

        self.maxsize = maxsize
        self.bucket = bucket
        self.client = s3_client
        self.key_prefix = key_prefix

    def __getitem__(self, key):
        try:
            response = self.client.get_object(
                Bucket=self.bucket, Key=self.key_prefix + key
            )
            value = pickle.loads(response["Body"].read())
            return value
        except Exception:
            pass
        return self.__missing__(key)

    def __missing__(self, key):
        raise KeyError(key)

    def __setitem__(self, key: Any, value: Any) -> None:
        payload = pickle.dumps(value)
        self.client.put_object(
            Bucket=self.bucket, Key=(self.key_prefix + key), Body=payload
        )

    def __delitem__(self, key):
        self.client.delete_object(Bucket=self.bucket, Key=self.key_prefix + key)

    def __len__(self) -> int:
        return sum([1 for _ in self])

    def __iter__(self):
        yield from get_all_keys(self.client, self.bucket, self.key_prefix)


def get_all_keys(s3_client, bucket, key_prefix):
    def page(s3_client, bucket, key_prefix, start_after=""):
        response = s3_client.list_objects_v2(
            Bucket=bucket, Prefix=key_prefix, StartAfter=start_after
        )

        if "Contents" not in response:
            return [], False

        key_list = response["Contents"]
        has_next_page = response["IsTruncated"]

        return key_list, has_next_page

    keys, has_next_page = page(s3_client, bucket, key_prefix, start_after="")

    for key in keys:
        yield key

    while has_next_page:
        new_keys, has_next_page = page(
            s3_client, bucket, key_prefix, start_after=keys[-1]
        )
        for key in new_keys:
            yield key
