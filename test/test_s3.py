import boto3
from moto import mock_s3

from cachetools_ext.s3 import S3Cache


@mock_s3
def test_set_get():
    s3_client = boto3.client("s3", region_name="us-east-1")
    bucket = "cache_bucket"
    s3_client.create_bucket(Bucket=bucket)

    cache = S3Cache(maxsize=3, s3_client=s3_client, bucket=bucket, key_prefix="abc_")
    cache["hello"] = "world"

    for item in cache:
        print(item)
    assert cache["hello"] == "world"


@mock_s3
def test_len():
    s3_client = boto3.client("s3", region_name="us-east-1")
    bucket = "cache_bucket"
    s3_client.create_bucket(Bucket=bucket)
    cache = S3Cache(maxsize=3, s3_client=s3_client, bucket=bucket, key_prefix="abc_")

    assert len(cache) == 0
    cache["hello"] = "world"
    assert len(cache) == 1
    cache["hello"] = "world"
    assert len(cache) == 1
    cache["foo"] = "bar"
    assert len(cache) == 2


@mock_s3
def test_del():
    s3_client = boto3.client("s3", region_name="us-east-1")
    bucket = "cache_bucket"
    s3_client.create_bucket(Bucket=bucket)
    cache = S3Cache(maxsize=3, s3_client=s3_client, bucket=bucket, key_prefix="abc_")

    assert len(cache) == 0
    cache["hello"] = "world"
    assert len(cache) == 1
    del cache["hello"]
    assert len(cache) == 0


@mock_s3
def test_contains():
    s3_client = boto3.client("s3", region_name="us-east-1")
    bucket = "cache_bucket"
    s3_client.create_bucket(Bucket=bucket)
    cache = S3Cache(maxsize=3, s3_client=s3_client, bucket=bucket, key_prefix="abc_")

    assert "hello" not in cache
    cache["hello"] = "world"
    assert "hello" in cache
