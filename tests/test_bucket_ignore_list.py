#!/usr/bin/env python

import osn.bucket_ignore_list as bucket_ignore_list
import unittest


class BucketIgnoreListTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_bucket_ignore_list(self):
        correct_bucket_ignore_list = {
            "site_1": ["ignore_bucket_1", "ignore_bucket_2"],
            "site_2": ["ignore_bucket_1", "ignore_bucket_3"],
        }

        #
        # Test that the bucket_ignore_list is read correctly
        #
        test_bucket_ignore_list = bucket_ignore_list.get_bucket_ignore_list(
            "tests/examples/good-bucket-ignore-list.yaml"
        )

        self.assertEqual(test_bucket_ignore_list, correct_bucket_ignore_list)

        #
        # Test that the bucket_ignore_list returns an empty dictionary when the file is not proper YAML
        #
        test_bucket_ignore_list = bucket_ignore_list.get_bucket_ignore_list(
            "tests/examples/error-bucket-ignore-list.yaml"
        )

        self.assertEqual(test_bucket_ignore_list, {})

        #
        # Test that the bucket_ignore_list returns an empty dictionary when the file is missing
        #
        test_bucket_ignore_list = bucket_ignore_list.get_bucket_ignore_list(
            "tests/examples/missing-bucket-ignore-list.yaml"
        )

        self.assertEqual(test_bucket_ignore_list, {})
