#!/usr/bin/env python3
"""Tests for the utils.py file."""
import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized
from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """Tests for accessing nested maps."""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, result):
        """Test accessing nested maps."""
        self.assertEqual(access_nested_map(nested_map, path), result)

    @parameterized.expand([
        ({}, ("a",), KeyError),
        ({"a": 1}, ("a", "b"), KeyError),
    ])
    def test_access_nested_map_exception(self, nested_map, path, exception):
        """Test exceptions for access_nested_map."""
        self.assertRaises(exception, access_nested_map, nested_map, path)


class TestGetJson(unittest.TestCase):
    """Tests for the get_json function."""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False})
    ])
    def test_get_json(self, test_url, test_payload):
        """Test the get_json function."""
        with patch("requests.get") as pat:
            pat.return_value = Mock()
            pat.return_value.json.return_value = test_payload
            self.assertEqual(get_json(test_url), test_payload)


class TestMemoize(unittest.TestCase):
    """Test the memoize function."""

    def test_memoize(self):
        """Test the memoize function."""
        class TestClass:
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        with patch.object(TestClass, "a_method") as test_method:
            test_method.return_value = 42
            test = TestClass()
            self.assertEqual(test.a_property, 42)
            self.assertEqual(test.a_property, 42)
            test_method.assert_called_once()
