#!/usr/bin/env python

import json
import api as api
import unittest
from mock import patch


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = api.app.test_client()

    def test_index(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)

    @patch("osn.buckets.get_read_buckets")
    @patch("osn.buckets.get_all_buckets")
    @patch("osn.credentials.get_credentials")
    def test_get_buckets_v10(
        self, mock_get_credentials, mock_get_all_buckets, mock_get_read_buckets
    ):
        buckets = ["bucket_1.site_1", "bucket_2.site_1"]
        mock_get_credentials.return_value = {
            "site_1": {"access_key": "abc123", "secret_key": "def456"}
        }
        mock_get_all_buckets.return_value = buckets
        mock_get_read_buckets.return_value = buckets

        response = self.app.get("/v1.0/buckets")
        response_data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response_data, buckets)

    @patch("osn.buckets.get_bucket_details")
    @patch("osn.buckets.get_read_buckets")
    @patch("osn.buckets.get_all_buckets")
    @patch("osn.credentials.get_credentials")
    def test_get_buckets_v20(
        self,
        mock_get_credentials,
        mock_get_all_buckets,
        mock_get_read_buckets,
        mock_get_bucket_details,
    ):
        buckets = ["bucket_1.site_1"]
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
        mock_get_credentials.return_value = {
            "site_1": {"access_key": "abc123", "secret_key": "def456"}
        }
        mock_get_all_buckets.return_value = buckets
        mock_get_read_buckets.return_value = buckets
        mock_get_bucket_details.return_value = bucket_details

        response = self.app.get("/v2.0/buckets")
        response_data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response_data, correct_read_buckets_with_details)

    @patch("osn.buckets.get_bucket_details")
    def test_get_bucket_details_v10_v20(self, mock_get_bucket_details):
        bucket_details = {
            "bucket": "bucket_1.site_1",
            "name": "bucket_1",
            "site": "site_1",
            "size": 1000,
            "object_count": 1,
        }

        mock_get_bucket_details.return_value = bucket_details

        response = self.app.get("/v1.0/details/bucket_1.site_1")
        response_data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response_data, bucket_details)

        response = self.app.get("/v2.0/details/bucket_1.site_1")
        response_data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response_data, bucket_details)

    @patch("osn.buckets.get_object_list")
    def test_get_object_list_v10_v20(self, mock_get_object_list):
        object_list = [
            {
                "name": "object_1",
                "size": 1000,
                "last_modified": "2020-01-01 00:00:00",
                "etag": "abc123",
            }
        ]

        mock_get_object_list.return_value = object_list

        response = self.app.get("/v1.0/object-list/bucket_1.site_1")
        response_data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response_data, object_list)

        response = self.app.get("/v2.0/object-list/bucket_1.site_1")
        response_data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response_data, object_list)
