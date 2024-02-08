import unittest
from unittest.mock import patch
import osn.cache


class CacheTestCase(unittest.TestCase):
    @patch("os.path.exists")
    @patch("os.path.getmtime")
    @patch("time.time")
    @patch("builtins.open")
    def test_get_cache_valid_file(
        self, mock_open, mock_time, mock_getmtime, mock_exists
    ):
        mock_exists.return_value = True
        # Set modification time to 2021-08-26 00:00:00
        mock_getmtime.return_value = 1629878400
        # Set current time to 2021-08-26 00:00:01
        mock_time.return_value = 1629878401
        mock_file = mock_open.return_value.__enter__.return_value
        mock_file.read.return_value = '{"key": "value"}'

        cache = osn.cache.get_cache("cache.json")

        self.assertEqual(cache, {"key": "value"})
        mock_exists.assert_called_once_with("cache.json")
        mock_getmtime.assert_called_once_with("cache.json")
        mock_time.assert_called_once()
        mock_open.assert_called_once_with("cache.json", "r")
        mock_file.read.assert_called_once()

    @patch("os.path.exists")
    def test_get_cache_invalid_file(self, mock_exists):
        mock_exists.return_value = False

        cache = osn.cache.get_cache("cache.json")

        self.assertEqual(cache, {})
        mock_exists.assert_called_once_with("cache.json")

    @patch("os.path.exists")
    @patch("os.path.getmtime")
    @patch("time.time")
    @patch("builtins.open")
    def test_get_cache_expired_cache(
        self, mock_open, mock_time, mock_getmtime, mock_exists
    ):
        mock_exists.return_value = True
        # Set modification time to 2021-08-25 00:00:00
        mock_getmtime.return_value = 1629782400
        # Set current time to 2021-08-27 00:00:00
        mock_time.return_value = 1629964800

        cache = osn.cache.get_cache("cache.json")

        self.assertEqual(cache, {})
        mock_exists.assert_called_once_with("cache.json")
        mock_getmtime.assert_called_once_with("cache.json")
        mock_time.assert_called_once()

    @patch("os.path.exists")
    @patch("os.path.getmtime")
    @patch("time.time")
    @patch("builtins.open")
    def test_get_cache_invalid_json(
        self, mock_open, mock_time, mock_getmtime, mock_exists
    ):
        mock_exists.return_value = True
        # Set modification time to 2021-08-26 00:00:00
        mock_getmtime.return_value = 1629878400
        # Set current time to 2021-08-26 00:00:01
        mock_time.return_value = 1629878401
        mock_file = mock_open.return_value.__enter__.return_value
        mock_file.read.return_value = '{"key"bb: "value"}'

        cache = osn.cache.get_cache("cache.json")

        self.assertEqual(cache, {})
        mock_exists.assert_called_once_with("cache.json")
        mock_getmtime.assert_called_once_with("cache.json")
        mock_time.assert_called_once()
        mock_open.assert_called_once_with("cache.json", "r")
        mock_file.read.assert_called_once()

    @patch("json.dump")
    @patch("builtins.open")
    def test_write_cache_file(self, mock_open, mock_json_dump):
        mock_file = mock_open.return_value.__enter__.return_value

        osn.cache.write_cache("cache.json", '{"key": "value"}')

        mock_open.assert_called_once_with("cache.json", "w")
        mock_json_dump.assert_called_once_with('{"key": "value"}', mock_file)
