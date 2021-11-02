import unittest

from schema import Schema

from ..endpoints.prescription_endpoint import PrescriptionEndpoint


class TestPrescriptionEndpoint(unittest.TestCase):
    def test_get_schema(self):
        endpoint = PrescriptionEndpoint()
        self.assertIsInstance(endpoint.get_payload_schema, Schema)  # add assertion here


if __name__ == '__main__':
    unittest.main()
