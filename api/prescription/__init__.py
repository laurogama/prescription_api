import logging

from flask import Flask, send_from_directory
from flask_restful import Api
from flask_swagger_ui import get_swaggerui_blueprint

from .endpoints.prescription_endpoint import PrescriptionEndpoint
from .models.dao import init_db

app = Flask(__name__, static_url_path='')
app.config.from_object("prescription.config.Config")
db = init_db(app)
api = Api(app)

api.add_resource(PrescriptionEndpoint, '/prescriptions', strict_slashes=False, resource_class_kwargs={
    'logger': logging.getLogger('prescription_logger')
})


@app.route('/spec')
def get_spec():
    return send_from_directory(app.static_url_path, 'swagger.yaml')


SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/swagger.yaml'  # Our API url (can of course be a local resource)

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Iclinic Challenge Prescription API"
    },
)

app.register_blueprint(swaggerui_blueprint)
