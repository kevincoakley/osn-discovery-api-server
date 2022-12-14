#!/usr/bin/env python

import boto3
from botocore import UNSIGNED
from botocore.client import ClientError
from botocore.config import Config
from rgwadmin import RGWAdmin


def get_all_buckets(credentials):
    """
    :param credentials: a dictionary containing the credentials
    :return: a list containing all buckets
    """

    buckets = []

    for credential in credentials:

        rgw = RGWAdmin(
            access_key=credentials[credential]["access_key"],
            secret_key=credentials[credential]["secret_key"],
            server=credential,
        )

        for bucket in rgw.get_buckets():
            buckets.append("%s.%s" % (bucket, credential))

    return buckets


def get_read_buckets(buckets, empty_buckets=False):
    """
    :param buckets: a list containing the buckets
    :return: a list containing the buckets that can be read
    """

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
