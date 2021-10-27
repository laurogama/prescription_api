from flask import Flask
from flask_restful import Api

from prescription.endpoints.prescriptionendpoint import PrescriptionEndpoint
from prescription.models.dao import init_db

app = Flask(__name__)
api = Api(app)
app.config.from_object("prescription.config.Config")
init_db(app)

api.add_resource(PrescriptionEndpoint, '/prescriptions')
