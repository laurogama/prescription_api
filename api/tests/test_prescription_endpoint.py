import http
import json
import logging
import os
import tempfile
from unittest import mock

from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_testing import TestCase
from prescription import init_db
from prescription.endpoints.prescription_endpoint import PrescriptionEndpoint
from schema import Schema


@mock.patch.dict(os.environ, {"DATABASE_URL": "sqlite://", })
class TestPrescriptionEndpoint(TestCase):
    db = SQLAlchemy()

    def setUp(self):
        self.db.create_all()

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db_fd, db_path = tempfile.mkstemp()
        app.config['DATABASE'] = db_path
        self.db = init_db(app)
        api = Api(app)

        api.add_resource(PrescriptionEndpoint, '/prescriptions', strict_slashes=False, resource_class_kwargs={
            'logger': logging.getLogger('prescription_logger')
        })
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
