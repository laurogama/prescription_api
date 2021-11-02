from prescription.models.dao import Prescription


def test_new_prescription():
    prescription = Prescription(1, 1, 1, 'Test')
    assert prescription.patient_id == 1
    assert prescription.clinic_id == 1
    assert prescription.physician_id == 1
    assert prescription.text == 'Test'
