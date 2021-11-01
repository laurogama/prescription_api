from flask import Flask
from flask_restful import Api

from prescription.endpoints.prescription_endpoint import PrescriptionEndpoint
from prescription.models.dao import init_db

app = Flask(__name__)
app.config.from_object("prescription.config.Config")
db = init_db(app)
api = Api(app)

api.add_resource(PrescriptionEndpoint, '/prescriptions')
