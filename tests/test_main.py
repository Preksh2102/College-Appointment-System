from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_e2e():
    # Student A1 logs in
    response = client.post("/token", data={"username": "studentA1", "password": "pass"})
    assert response.status_code == 200
    student_token = response.json()["access_token"]

    # Professor P1 logs in
    response = client.post("/token", data={"username": "professorP1", "password": "pass"})
    assert response.status_code == 200
    professor_token = response.json()["access_token"]

    # Professor adds availability
    availability_payload = {"time_slots": ["2025-02-08T10:00:00"]}
    headers = {"Authorization": f"Bearer {professor_token}"}
    response = client.post("/professors/1/availability", json=availability_payload, headers=headers)
    assert response.status_code == 200

    # Student A1 books an appointment
    appointment_payload = {"professor_id": 1, "time_slot": "2025-02-08T10:00:00"}
    headers = {"Authorization": f"Bearer {student_token}"}
    response = client.post("/appointments", json=appointment_payload, headers=headers)
    assert response.status_code == 200

    # Verify appointment booking
    response = client.get(f"/students/studentA1/appointments", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
