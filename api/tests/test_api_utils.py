import unittest

from prescription.controller.api_utils import validate_json, validate_schema
from schema import Schema


class TestApiUtils(unittest.TestCase):
    def test_validate_json_true(self):
        self.assertTrue(validate_json("{}"))

    def test_validate_json_false(self):
        self.assertFalse(validate_json("Hello"))

    def test_validate_schema_true(self):
        self.assertTrue(validate_schema(Schema({"text": str}), {"text": "Hello World"}))


if __name__ == '__main__':
    unittest.main()
