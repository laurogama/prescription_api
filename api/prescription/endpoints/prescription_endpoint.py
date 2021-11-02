import http

from flask import request
from flask_restful import Resource
from schema import Schema

from ..controller.api_utils import validate_json, validate_schema
from ..controller.controller import request_prescription_details, StatusCode
from ..models.dao import Prescription


class PrescriptionEndpoint(Resource):
    """
    Prescription endpoint
    """

    def post(self):
        """
        POST method that receives a JSON object
        :return: JSON body with metrics added
        """
        raw_data = request.get_data(as_text=True)
        # checks if payload is a valid json
        is_valid_request = validate_json(raw_data)
        if not is_valid_request:
            return {'error': {'message': StatusCode.MalformedRequest.message,
                              'code': StatusCode.MalformedRequest.code}}, http.HTTPStatus.BAD_REQUEST
        request_data = request.get_json(force=True)
        # Checks if the json document is compliant with endpoint expected schema
        is_valid_schema = validate_schema(self.get_payload_schema, request_data)
        if is_valid_schema:
            prescription_model = Prescription(clinic=request_data['clinic']['id'],
                                              physician=request_data['physician']['id'],
                                              patient=request_data['patient']['id'], text=request_data['text'])
            prescription_model.save()
            request_data['prescription_id'] = prescription_model.id
            prescription_details, status = request_prescription_details(request_data)
            if status > http.HTTPStatus.ACCEPTED:
                prescription_model.rollback()
                return {'error': {'message': prescription_details['message'],
                                  'code': prescription_details['code']}}, status
            else:
                response = request.get_json(force=True)
                response['metric'] = prescription_details['metric']
                response['id'] = prescription_model.id
                del response['prescription_id']
                prescription_model.commit()
                return {'data': response}, status
        else:
            return {'error': {'message': StatusCode.MalformedRequest.message,
                              'code': StatusCode.MalformedRequest.code}}, http.HTTPStatus.BAD_REQUEST

    @property
    def get_payload_schema(self):
        return Schema({"text": str, "clinic": {"id": int}, "patient": {"id": int}, "physician": {"id": int}})
