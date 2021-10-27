from flask import request
from flask_restful import Resource

from prescription.controller.controller import request_prescription_details


class PrescriptionEndpoint(Resource):
    """
    Prescription endpoint
    """

    def post(self):
        """
        POST method that receives a JSON object
        :return: JSON body with metrics added
        """
        request_data = request.get_json(force=True)
        print(request_data)
        prescription_model = PrescriptionEndpoint
        status, prescription_details = request_prescription_details(request_data)
        if status:

            return {'data': {}}
        else:
            return {'error': {'message': '', 'code': "03"}}, status