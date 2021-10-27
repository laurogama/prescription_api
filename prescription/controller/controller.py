from concurrent.futures import as_completed
from enum import Enum

import backoff as backoff
import requests
from requests_futures.sessions import FuturesSession

from services import services


@backoff.on_exception(
    backoff.expo,
    requests.exceptions.RequestException,
    max_tries=services['patients']['retry'],
    giveup=lambda e: e.response is not None and e.response.status_code < 500
)
def call_patients(prescription, session):
    session.get(f"{services['host']}{services['clinics']['path']}/{prescription['clinic']['id']}",
                timeout=services['clinics']['timeout'], headers={'Authorization': services['patients']['token']})


@backoff.on_exception(
    backoff.expo,
    requests.exceptions.RequestException,
    max_tries=services['physicians']['retry'],
    giveup=lambda e: e.response is not None and e.response.status_code < 500
)
def call_physicians(prescription, session):
    return session.get(f"{services['host']}{services['physicians']['path']}/{prescription['physician']['id']}",
                       timeout=services['clinics']['timeout'],
                       headers={'Authorization': services['physicians']['token']})


@backoff.on_exception(
    backoff.expo,
    requests.exceptions.RequestException,
    max_tries=services['clinics']['retry'],
    giveup=lambda e: e.response is not None and e.response.status_code < 500
)
def call_clinics(prescription, session):
    return session.get(f"{services['host']}{services['clinics']['path']}/{prescription['clinic']['id']}",
                       timeout=services['clinics']['timeout'], headers={'Authorization': services['clinics']['token']})


def request_prescription_details(prescription):
    session = FuturesSession()
    futures = [call_clinics(prescription, session), call_patients(prescription, session),
               call_physicians(prescription, session)]
    for future in as_completed(futures):
        print(future.result())


class StatusCode(Enum):
    """This Enum contains status code related to prescription endpoint """
    MalformedRequest = 1, 'malformed request'
    PhysicianNotFound = 2, 'physician not found'
    PatientNotFound = 3, 'patient not found'
    MetricsServiceNotAvailable = 4, 'metrics service not available'
    PhysicianServiceNotAvailable = 5, 'physicians service not available'
    PatientsServiceNotAvailable = 6, 'patients service not available'
