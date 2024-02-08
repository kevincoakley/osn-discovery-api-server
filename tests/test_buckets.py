#!/usr/bin/env python

from botocore.client import ClientError
import osn.buckets as buckets
import unittest
from mock import patch


class BucketsTestCase(unittest.TestCase):
    def setUp(self):
        pass

    @patch("osn.cache.get_cache")
    @patch("builtins.open")
    @patch("rgwadmin.RGWAdmin.get_buckets")
    def test_get_all_buckets(self, mock_get_buckets, mock_open, mock_get_cache):
        credentials = {
            "site_1": {"access_key": "abc123", "secret_key": "def456"},
            "site_2": {"access_key": "ghi789", "secret_key": "jkl012"},
        }

        bucket_ignore_list = {
            "site_1": ["ignore_bucket_1"],
        }

        #
        # Test without cache
        #
        correct_buckets = [
            "bucket_1.site_1",
            "bucket_2.site_1",
            "bucket_1.site_2",
            "bucket_2.site_2",
            "ignore_bucket_1.site_2",
        ]

        mock_get_buckets.return_value = ["bucket_1", "bucket_2", "ignore_bucket_1"]
        test_buckets = buckets.get_all_buckets(credentials, bucket_ignore_list)

        self.assertEqual(test_buckets, correct_buckets)

        #
        # Test with cache
        #
        mock_get_cache.return_value = ["cache_bucket_1.site_1", "cache_bucket_2.site_1"]
        test_buckets = buckets.get_all_buckets(credentials, bucket_ignore_list)

        correct_buckets = [
            "cache_bucket_1.site_1",
            "cache_bucket_2.site_1",
        ]

        self.assertEqual(test_buckets, correct_buckets)

    @patch("osn.cache.get_cache")
    @patch("builtins.open")
    @patch("boto3.client")
    def test_get_read_buckets(self, mock_client, mock_open, mock_get_cache):
        all_buckets = [
            "bucket_1.site_1",
            "bucket_2.site_1",
            "bucket_1.site_2",
            "bucket_2.site_2",
        ]

        #
        # Test that buckets with objects are returned
        #
        correct_read_buckets = [
            "bucket_1.site_1",
            "bucket_2.site_1",
            "bucket_1.site_2",
            "bucket_2.site_2",
        ]

        mock_client.return_value.head_bucket.return_value = {
            "ResponseMetadata": {"HTTPHeaders": {"x-rgw-object-count": 1}}
        }
        test_read_buckets = buckets.get_read_buckets(all_buckets)

        self.assertEqual(test_read_buckets, correct_read_buckets)

        #
        # Test that empty buckets are not returned
        #
        correct_read_buckets = []

        mock_client.return_value.head_bucket.return_value = {
            "ResponseMetadata": {"HTTPHeaders": {"x-rgw-object-count": 0}}
        }
        test_read_buckets = buckets.get_read_buckets(all_buckets)

        self.assertEqual(test_read_buckets, correct_read_buckets)

        #
        # Test that private buckets are not returned
        #
        mock_client.return_value.head_bucket.side_effect = ClientError(
            error_response={}, operation_name="head_bucket"
        )

        test_read_buckets = buckets.get_read_buckets(all_buckets)

        self.assertEqual(test_read_buckets, correct_read_buckets)

        #
        # Test with cache
        #
        mock_get_cache.return_value = ["cache_bucket_1.site_1", "cache_bucket_2.site_1"]
        test_read_buckets = buckets.get_read_buckets(all_buckets)

        correct_buckets = [
            "cache_bucket_1.site_1",
            "cache_bucket_2.site_1",
        ]

        self.assertEqual(test_read_buckets, correct_buckets)

    @patch("boto3.client")
    def test_get_get_bucket_details(self, mock_client):
        correct_bucket_details = {
            "bucket": "bucket_1.site_1",
            "bytes-used": 1000,
            "name": "bucket_1",
            "object-count": 1,
            "site": "site_1",
        }
        mock_client.return_value.head_bucket.return_value = {
            "ResponseMetadata": {
                "HTTPHeaders": {"x-rgw-object-count": 1, "x-rgw-bytes-used": 1000}
            }
        }

        test_bucket_details = buckets.get_bucket_details("bucket_1.site_1")

        self.assertEqual(test_bucket_details, correct_bucket_details)

    @patch("osn.buckets.get_read_buckets")
    @patch("osn.buckets.get_bucket_details")
    def test_get_read_buckets_with_details(
        self, mock_get_bucket_details, mock_get_read_buckets
    ):
        read_buckets = ["bucket_1.site_1"]

        bucket_details = {
            "bucket": "bucket_1.site_1",
            "bytes-used": 1000,
            "name": "bucket_1",
            "object-count": 1,
            "site": "site_1",
        }

        correct_read_buckets_with_details = {
            "bucket_1.site_1": {
                "bytes-used": 1000,
                "name": "bucket_1",
                "object-count": 1,
                "site": "site_1",
            },
        }

        mock_get_read_buckets.return_value = read_buckets
        mock_get_bucket_details.return_value = bucket_details

        test_read_buckets_with_details = buckets.get_read_buckets_with_details(
            read_buckets
        )

        self.assertEqual(
            test_read_buckets_with_details, correct_read_buckets_with_details
        )

    @patch("boto3.client")
    def test_get_object_list(self, mock_client):
        correct_object_list = [
            {
                "key": "object_1",
                "last-modified": "2020-01-01T00:00:00.000Z",
                "size": 1000,
                "etag": "abc123",
                "url": "https://bucket_1.site_1/object_1",
            },
            {
                "key": "object_2",
                "last-modified": "2020-01-01T00:00:00.000Z",
                "size": 1001,
                "etag": "def456",
                "url": "https://bucket_1.site_1/object_2",
            },
        ]

        mock_client.return_value.list_objects_v2.return_value = {
            "Contents": [
                {
                    "Key": "object_1",
                    "LastModified": "2020-01-01T00:00:00.000Z",
                    "Size": 1000,
                    "ETag": "abc123",
                },
                {
                    "Key": "object_2",
                    "LastModified": "2020-01-01T00:00:00.000Z",
                    "Size": 1001,
                    "ETag": "def456",
                },
            ]
        }

        test_object_list = buckets.get_object_list("bucket_1.site_1")

        self.assertEqual(test_object_list, correct_object_list)
