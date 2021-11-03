import logging

from flask import Flask
from flask_restful import Api

from .endpoints.prescription_endpoint import PrescriptionEndpoint
from .models.dao import init_db

app = Flask(__name__)
app.config.from_object("prescription.config.Config")
db = init_db(app)
api = Api(app)

api.add_resource(PrescriptionEndpoint, '/prescriptions', strict_slashes=False, resource_class_kwargs={
    'logger': logging.getLogger('prescription_logger')
})
