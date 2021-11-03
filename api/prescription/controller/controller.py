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
    async with CachedSession(
            cache=CacheBackend('clinics_cache', expire_after=services[CLINICS]['cache-ttl'] * HOUR)) as session:
        url = f"{services['host']}{services[CLINICS]['path']}{prescription['clinic']['id']}/"
        return await session.get(url=url,
                                 timeout=services[CLINICS]['timeout'],
                                 headers={'Authorization': services[CLINICS]['token']})


def request_prescription_details(prescription):
    return asyncio.run(run_requests(prescription))


def prepare_metrics_payload(clinic, patient, physician, prescription):
    payload_document = {'patient_id': patient['id'], 'patient_name': patient['name'],
                        'patient_phone': patient['phone'], 'patient_email': patient['email'],
                        'physician_id': physician['id'], 'physician_name': physician['name'],
                        'physician_crm': physician['crm'], 'prescription_id': prescription,
                        'clinic_id': clinic['id'], 'clinic_name': clinic['name']}
    return json.dumps(payload_document)


def handle_service_response(response_dict):
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
    url = f"{services['host']}{services['metrics']['path']}"
    with requests.session() as session:
        return session.post(url, data=payload,
                            timeout=services['metrics']['timeout'],
                            headers={'Authorization': services['metrics']['token'], 'Content-Type': 'application/json'})


def prepare_metrics_response(metrics_json):
    metrics = {"metric": {"id": metrics_json['id']}}
    return metrics


def send_metrics(clinics, patients, physicians, prescription):
    metrics_payload = prepare_metrics_payload(clinics, patients, physicians, prescription)
    metrics_response = call_metrics_server(metrics_payload)
    if not metrics_response:
        return {"message": StatusCode.MetricsServiceNotAvailable.message,
                "code": StatusCode.MetricsServiceNotAvailable.code,
                "response_code": metrics_response.status_code}, metrics_response.status_code
    else:
        return prepare_metrics_response(metrics_response.json()), metrics_response.status_code


async def run_requests(prescription):
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
