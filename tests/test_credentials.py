#!/usr/bin/env python

import osn.credentials as credentials
import unittest


class CredentialsTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_credentials(self):
        correct_credentials = {
            "site_1": {"access_key": "abc123", "secret_key": "def456"},
            "site_2": {"access_key": "ghi789", "secret_key": "jkl012"},
        }

        #
        # Test that the credentials are read correctly
        #
        test_credentials = credentials.get_credentials("tests/examples/good-creds.yaml")

        self.assertEqual(test_credentials, correct_credentials)

        #
        # Test that the credentials are not read correctly
        #
        test_credentials = credentials.get_credentials(
            "tests/examples/error-creds.yaml"
        )

        self.assertEqual(test_credentials, None)
