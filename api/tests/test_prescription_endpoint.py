import http
import json

from flask_testing import TestCase
from prescription import app
from prescription.endpoints.prescription_endpoint import PrescriptionEndpoint
from schema import Schema


class TestPrescriptionEndpoint(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_get_schema(self):
        endpoint = PrescriptionEndpoint()
        self.assertIsInstance(endpoint.get_payload_schema, Schema)  # add assertion here

    def test_prescription_get(self):
        response = self.client.get("/prescriptions/")
        self.assertEqual(response.status_code, http.HTTPStatus.METHOD_NOT_ALLOWED)

    def test_prescription_post_bad_request(self):
        response = self.client.post("/prescriptions/")
        self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)

    def test_prescription_post(self):
        response = self.client.post("/prescriptions/", data=json.dumps({
            "clinic": {
                "id": 1
            },
            "physician": {
                "id": 1
            },
            "patient": {
                "id": 1
            },
            "text": "Dipirona 1x ao dia"
        }))
        self.assertEqual(response.status_code, http.HTTPStatus.CREATED)
