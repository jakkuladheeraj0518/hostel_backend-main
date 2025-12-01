from app.main import app


def test_rooms_export_and_room_id_paths_present():
    schema = app.openapi()
    paths = schema.get("paths", {})
    # Ensure static export and dynamic {room_id} are present
    assert any(p.endswith("/admin/rooms/export") for p in paths)
    assert any(p.endswith("/admin/rooms/{room_id}") for p in paths)


def test_students_export_and_student_id_paths_present():
    schema = app.openapi()
    paths = schema.get("paths", {})
    assert any(p.endswith("/admin/students/export") for p in paths)
    assert any(p.endswith("/admin/students/{student_id}") for p in paths)


def test_no_double_api_v1_prefixes():
    schema = app.openapi()
    paths = list(schema.get("paths", {}).keys())
    # There should be no paths containing the duplicated prefix /api/v1/api/v1
    assert not any("/api/v1/api/v1/" in p for p in paths), "Found duplicated /api/v1/api/v1 prefix in OpenAPI paths"


def test_students_history_correct_path():
    schema = app.openapi()
    paths = schema.get("paths", {})
    assert "/api/v1/admin/students/{student_id}/history" in paths
