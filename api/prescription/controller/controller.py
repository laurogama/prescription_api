import asyncio
import http
import json
from enum import Enum

import backoff as backoff
import requests
from aiohttp_client_cache import CachedSession, CacheBackend
from requests import Response

from . import CLINICS, PATIENTS, PHYSICIANS, RESPONSE_KEYS
from ..controller.services import services

HOUR = 3600  # seconds


@backoff.on_exception(
    backoff.expo,
    requests.exceptions.RequestException,
    max_tries=services['patients']['retry'],
    giveup=lambda e: e.response is not None and e.response.status_code < 500
)
async def call_patients(prescription):
    """
    Makes a GET request to Patients service
    :param prescription: a dict containing info necessary for request
    :return: The aiohttp response
    """
    async with CachedSession(
            cache=CacheBackend('patients_cache', expire_after=services[PATIENTS]['cache-ttl'] * HOUR)) as session:
        return await session.get(f"{services['host']}{services['patients']['path']}{prescription['patient']['id']}/",
                                 timeout=services['patients']['timeout'],
                                 headers={'Authorization': services['patients']['token']})


@backoff.on_exception(
    backoff.expo,
    requests.exceptions.RequestException,
    max_tries=services['physicians']['retry'],
    giveup=lambda e: e.response is not None and e.response.status_code < 500
)
async def call_physicians(prescription):
    """
    Makes a GET request to Physician service
    :param prescription: a dict containing info necessary for request
    :return: The aiohttp response
    """
    async with CachedSession(
            cache=CacheBackend('physicians_cache', expire_after=services[PHYSICIANS]['cache-ttl'] * HOUR)) as session:
        return await session.get(f"{services['host']}{services[PHYSICIANS]['path']}{prescription['physician']['id']}/",
                                 timeout=services[PHYSICIANS]['timeout'],
                                 headers={'Authorization': services[PHYSICIANS]['token']})


@backoff.on_exception(
    backoff.expo,
    requests.exceptions.RequestException,
    max_tries=services[CLINICS]['retry'],
    giveup=lambda e: e.response is not None and e.response.status_code < 500
)
async def call_clinics(prescription):
    """
    Makes a GET request to Clinics service
    :param prescription: a dict containing info necessary for request
    :return: The aiohttp response
    """
    async with CachedSession(
            cache=CacheBackend('clinics_cache', expire_after=services[CLINICS]['cache-ttl'] * HOUR)) as session:
        # In a real production environment this CacheBackend should be a RedisBackend
        url = f"{services['host']}{services[CLINICS]['path']}{prescription['clinic']['id']}/"
        return await session.get(url=url,
                                 timeout=services[CLINICS]['timeout'],
                                 headers={'Authorization': services[CLINICS]['token']})


def request_prescription_details(prescription):
    """
    Executes the asynchronous requests using a asyncio loop
    :param prescription: the prescription id
    :return: the response of the requests
    """
    return asyncio.run(run_requests(prescription))


def prepare_metrics_payload(clinic, patient, physician, prescription):
    """

    :param clinic: Dict containing information clinic information
    :param patient: Dict containing information patient information
    :param physician: Dict containing information physician information
    :param prescription: the prescription id created by the API
    :return: a JSON formatted string
    """
    if not clinic:
        clinic = {'id': '', 'name': ''}
    payload_document = {'patient_id': patient['id'], 'patient_name': patient['name'],
                        'patient_phone': patient['phone'], 'patient_email': patient['email'],
                        'physician_id': physician['id'], 'physician_name': physician['name'],
                        'physician_crm': physician['crm'], 'prescription_id': prescription,
                        'clinic_id': clinic['id'], 'clinic_name': clinic['name']}
    return json.dumps(payload_document)


def handle_service_response(response_dict):
    """
    Handles the response of dependent services of the prescription endpoint
    :param response_dict: the dict with the aiohttp Response
    :return: the dict with the error or success message
    """
    if response_dict[PATIENTS].status == http.HTTPStatus.SERVICE_UNAVAILABLE:
        return {"message": StatusCode.PatientsServiceNotAvailable.message,
                "code": StatusCode.PatientsServiceNotAvailable.code,
                "response_code": http.HTTPStatus.SERVICE_UNAVAILABLE}, http.HTTPStatus.SERVICE_UNAVAILABLE

    elif response_dict[PATIENTS].status == http.HTTPStatus.NOT_FOUND:
        return {"message": StatusCode.PatientNotFound.message,
                "code": StatusCode.PatientNotFound.code,
                "response_code": http.HTTPStatus.NOT_FOUND}, http.HTTPStatus.NOT_FOUND

    elif response_dict[PHYSICIANS].status == http.HTTPStatus.SERVICE_UNAVAILABLE:
        return {"message": StatusCode.PhysicianServiceNotAvailable.message,
                "code": StatusCode.PhysicianServiceNotAvailable.code,
                "response_code": http.HTTPStatus.SERVICE_UNAVAILABLE}, http.HTTPStatus.SERVICE_UNAVAILABLE

    elif response_dict[PHYSICIANS].status == http.HTTPStatus.NOT_FOUND:
        return {"message": StatusCode.PhysicianNotFound.message,
                "code": StatusCode.PhysicianNotFound.code,
                "response_code": http.HTTPStatus.NOT_FOUND}, http.HTTPStatus.NOT_FOUND
    else:
        return {"response_code": http.HTTPStatus.OK}, http.HTTPStatus.OK


@backoff.on_exception(
    backoff.expo,
    requests.exceptions.RequestException,
    max_tries=services['metrics']['retry'],
    giveup=lambda e: e.response is not None and e.response.status_code < 500
)
def call_metrics_server(payload) -> Response:
    """
    Requests a POST to metrics service
    :param payload: the json body of the request
    :return: a Requests Response object
    """
    url = f"{services['host']}{services['metrics']['path']}"
    with requests.session() as session:
        return session.post(url, data=payload,
                            timeout=services['metrics']['timeout'],
                            headers={'Authorization': services['metrics']['token'], 'Content-Type': 'application/json'})


def prepare_metrics_response(metrics_json):
    """
    Converts the metrics service response to the expected format
    :param metrics_json: the body of the metrics service response
    :return: a dict with metrics response id
    """
    metrics = {"metric": {"id": metrics_json['id']}}
    return metrics


def send_metrics(clinics, patients, physicians, prescription):
    """
    Sends a POST request to metrics service
    :param clinics: Dict containing information clinic information
    :param patients: Dict containing information patient information
    :param physicians: Dict containing information physician information
    :param prescription: the prescription id created by the API
    :return: A dict containing the metrics service response or error code
    """
    metrics_payload = prepare_metrics_payload(clinics, patients, physicians, prescription)
    metrics_response = call_metrics_server(metrics_payload)
    if not metrics_response:
        return {"message": StatusCode.MetricsServiceNotAvailable.message,
                "code": StatusCode.MetricsServiceNotAvailable.code,
                "response_code": metrics_response.status_code}, metrics_response.status_code
    else:
        return prepare_metrics_response(metrics_response.json()), metrics_response.status_code


async def run_requests(prescription):
    """
    Executes the service requests
    :param prescription: dict containing the user request body
    :return: the response of the API endpoint
    """
    clinics = await call_clinics(prescription)
    patients = await call_patients(prescription)
    physicians = await call_physicians(prescription)
    response_dict = dict(zip(RESPONSE_KEYS, [clinics, patients, physicians]))
    response, status = handle_service_response(response_dict)
    if status is http.HTTPStatus.OK:
        return send_metrics(await clinics.json(), await patients.json(),
                            await physicians.json(),
                            prescription['prescription_id'])
    else:
        return response, status


class StatusCode(Enum):
    """This Enum contains status code related to prescription endpoint """

    def __init__(self, code, message):
        self.code = code
        self.message = message

    MalformedRequest = '01', 'malformed request'
    PhysicianNotFound = '02', 'physician not found'
    PatientNotFound = '03', 'patient not found'
    MetricsServiceNotAvailable = '04', 'metrics service not available'
    PhysicianServiceNotAvailable = '05', 'physicians service not available'
    PatientsServiceNotAvailable = '06', 'patients service not available'
