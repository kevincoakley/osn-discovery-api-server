#!/usr/bin/env python

import boto3
from botocore import UNSIGNED
from botocore.client import ClientError
from botocore.config import Config
from rgwadmin import RGWAdmin
import osn.cache


def get_all_buckets(credentials, bucket_ignore_list):
    """
    :param credentials: a dictionary containing the credentials
    :return: a list containing all buckets
    """

    bucket_cache = osn.cache.get_cache("cache/buckets.json")

    if len(bucket_cache) > 0:
        return bucket_cache

    buckets = []

    for credential in credentials:
        rgw = RGWAdmin(
            access_key=credentials[credential]["access_key"],
            secret_key=credentials[credential]["secret_key"],
            server=credential,
        )

        for bucket in rgw.get_buckets():
            buckets.append("%s.%s" % (bucket, credential))

            # Remove the buckets that are in the ignore list
            if credential in bucket_ignore_list:
                if bucket in bucket_ignore_list[credential]:
                    buckets.remove("%s.%s" % (bucket, credential))

    osn.cache.write_cache("cache/buckets.json", buckets)

    return buckets


def get_read_buckets(buckets, empty_buckets=False):
    """
    :param buckets: a list containing the buckets
    :param empty_buckets: a boolean indicating whether empty buckets should be returned
    :return: a list containing the buckets that can be read
    """

    read_buckets = osn.cache.get_cache("cache/read_buckets.json")

    if len(read_buckets) > 0:
        return read_buckets

    read_buckets = []

    for bucket in buckets:
        bucket_prefix = bucket.split(".")[0]
        site = bucket.replace("%s." % bucket_prefix, "")

        s3 = boto3.client(
            "s3",
            endpoint_url="https://%s" % site,
            config=Config(signature_version=UNSIGNED),
        )

        try:
            response = s3.head_bucket(Bucket=bucket_prefix)
            # If the bucket is empty and empty_buckets is False,
            # don't add it to read_buckets
            if (
                int(response["ResponseMetadata"]["HTTPHeaders"]["x-rgw-object-count"])
                > 0
                or empty_buckets
            ):
                read_buckets.append(bucket)
        except ClientError:
            pass

    osn.cache.write_cache("cache/read_buckets.json", read_buckets)

    return read_buckets


def get_bucket_details(bucket):
    """
    :param bucket: the bucket to be checked
    :return: the response from the head_bucket request
    """

    bucket_prefix = bucket.split(".")[0]
    site = bucket.replace("%s." % bucket_prefix, "")

    s3 = boto3.client(
        "s3",
        endpoint_url="https://%s" % site,
        config=Config(signature_version=UNSIGNED),
    )

    response = s3.head_bucket(Bucket=bucket_prefix)

    return {
        "bucket": bucket,
        "name": bucket_prefix,
        "site": site,
        "bytes-used": int(
            response["ResponseMetadata"]["HTTPHeaders"]["x-rgw-bytes-used"]
        ),
        "object-count": int(
            response["ResponseMetadata"]["HTTPHeaders"]["x-rgw-object-count"]
        ),
    }


def get_read_buckets_with_details(buckets, empty_buckets=False):
    """
    :param buckets: a list containing the buckets
    :param empty_buckets: a boolean indicating whether empty buckets should be returned
    :return: a dict containing the buckets that can be read with their details
    """
    read_buckets_with_details = {}

    read_buckets = get_read_buckets(buckets, empty_buckets)

    for bucket in read_buckets:
        details = get_bucket_details(bucket)
        del details["bucket"]
        read_buckets_with_details[bucket] = details

    return read_buckets_with_details


def get_object_list(bucket, prefix=""):
    """
    :param bucket: the bucket to be checked
    :param prefix: limits the response to keys that begin with the specified prefix
    :return: the response from the list_objects request
    """

    bucket_prefix = bucket.split(".")[0]
    site = bucket.replace("%s." % bucket_prefix, "")

    max_keys = get_bucket_details(bucket)["object-count"]

    s3 = boto3.client(
        "s3",
        endpoint_url="https://%s" % site,
        config=Config(signature_version=UNSIGNED),
    )

    # Get the list of objects for the bucket
    objects = s3.list_objects_v2(Bucket=bucket_prefix, MaxKeys=max_keys, Prefix=prefix)[
        "Contents"
    ]

    reformat_objects = []

    # Reformat the response
    for object in objects:
        reformat_objects.append(
            {
                "key": object["Key"],
                "last-modified": object["LastModified"],
                "size": object["Size"],
                "etag": object["ETag"],
                "url": "https://%s/%s" % (bucket, object["Key"]),
            }
        )

    return reformat_objects
