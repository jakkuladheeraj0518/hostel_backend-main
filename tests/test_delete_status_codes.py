import pytest


def test_model_student_delete_returns_200(monkeypatch):
    # Patch the service to simulate successful delete without DB
    monkeypatch.setattr(
        'app.api.v1.admin.students.service_delete_student',
        lambda db, sid: True
    )

    from app.api.v1.admin.students import delete_student

    resp = delete_student('STU001', db=None)
    assert hasattr(resp, 'status_code')
    assert resp.status_code == 200


def test_model_supervisor_delete_returns_200(monkeypatch):
    monkeypatch.setattr(
        'app.api.v1.admin.supervisors.service_delete_supervisor',
        lambda db, eid: True
    )

    from app.api.v1.admin.supervisors import delete_supervisor

    resp = delete_supervisor('EMP001', db=None)
    assert hasattr(resp, 'status_code')
    assert resp.status_code == 200
