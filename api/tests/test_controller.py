import http
from unittest import mock

from prescription.controller import PATIENTS, PHYSICIANS, CLINICS
from prescription.controller.controller import handle_service_response, StatusCode


def test_run_requests():
    pass


def test_handle_service_response():
    service_ok_response_mock = mock.MagicMock()
    type(service_ok_response_mock).status = mock.PropertyMock(return_value=200)
    service_ok_response_mock.json.return_value = "{'blah':'blah'}"

    service_unavailable_response_mock = mock.MagicMock()
    type(service_unavailable_response_mock).status = mock.PropertyMock(return_value=503)
    service_unavailable_response_mock.json.return_value = "{'blah':'blah'}"

    object_not_found_response_mock = mock.MagicMock()
    type(object_not_found_response_mock).status = mock.PropertyMock(return_value=404)
    object_not_found_response_mock.json.return_value = "{'blah':'blah'}"

    patients_service_not_available = {"message": StatusCode.PatientsServiceNotAvailable.message,
                                      "code": StatusCode.PatientsServiceNotAvailable.code,
                                      "response_code": http.HTTPStatus.SERVICE_UNAVAILABLE}, http.HTTPStatus.SERVICE_UNAVAILABLE

    physicians_service_not_available = {"message": StatusCode.PhysicianServiceNotAvailable.message,
                                        "code": StatusCode.PhysicianServiceNotAvailable.code,
                                        "response_code": http.HTTPStatus.SERVICE_UNAVAILABLE}, http.HTTPStatus.SERVICE_UNAVAILABLE

    patients_not_found = {"message": StatusCode.PatientNotFound.message,
                          "code": StatusCode.PatientNotFound.code,
                          "response_code": http.HTTPStatus.NOT_FOUND}, http.HTTPStatus.NOT_FOUND

    physician_not_found = {"message": StatusCode.PhysicianNotFound.message,
                           "code": StatusCode.PhysicianNotFound.code,
                           "response_code": http.HTTPStatus.NOT_FOUND}, http.HTTPStatus.NOT_FOUND

    all_services_ok = {"response_code": http.HTTPStatus.OK}, http.HTTPStatus.OK

    assert patients_service_not_available == handle_service_response(
        {PATIENTS: service_unavailable_response_mock, PHYSICIANS: service_unavailable_response_mock,
         CLINICS: service_unavailable_response_mock})

    assert physicians_service_not_available == handle_service_response(
        {PATIENTS: service_ok_response_mock, PHYSICIANS: service_unavailable_response_mock,
         CLINICS: service_unavailable_response_mock})

    assert patients_not_found == handle_service_response(
        {PATIENTS: object_not_found_response_mock, PHYSICIANS: service_unavailable_response_mock,
         CLINICS: service_ok_response_mock})

    assert physician_not_found == handle_service_response(
        {PATIENTS: service_ok_response_mock, PHYSICIANS: object_not_found_response_mock,
         CLINICS: service_ok_response_mock})

    assert all_services_ok == handle_service_response(
        {PATIENTS: service_ok_response_mock, PHYSICIANS: service_ok_response_mock,
         CLINICS: service_ok_response_mock})
