import os
import tempfile
import pytest

@pytest.fixture()
def client():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.environ["DB_PATH"] = path
    os.environ["TOTAL_SLOTS"] = "4"
    import app as parking_app
    parking_app.DB_PATH = path
    parking_app.TOTAL_SLOTS = 4
    parking_app.app.config.update(TESTING=True, SECRET_KEY="test-secret")
    with parking_app.app.test_client() as client:
        with parking_app.app.app_context():
            parking_app.init_db()
        yield client
    try:
        os.remove(path)
    except OSError:
        pass


def test_dashboard_loads_and_shows_slots(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"P-01" in response.data
    assert b"Smart Parking" in response.data


def test_health_endpoint_returns_json(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"


def test_reserve_and_release_slot(client):
    response = client.post("/reserve/1", data={"vehicle_number": "tn 01 ab 1234", "reserved_by": "Test Driver"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"P-01 is reserved" in response.data
    slots = client.get("/api/slots").get_json()
    assert slots[0]["status"] == "reserved"
    response = client.post("/release/1", follow_redirects=True)
    assert response.status_code == 200
    slots = client.get("/api/slots").get_json()
    assert slots[0]["status"] == "available"
    assert slots[0]["vehicle_number"] is None


def test_cannot_reserve_same_slot_twice(client):
    client.post("/reserve/1", data={"vehicle_number": "TN01AA1111", "reserved_by": "A"})
    client.post("/reserve/1", data={"vehicle_number": "TN01BB2222", "reserved_by": "B"})
    slots = client.get("/api/slots").get_json()
    assert slots[0]["vehicle_number"] == "TN01AA1111"


def test_admin_and_summary_api(client):
    assert client.get("/admin").status_code == 200
    summary = client.get("/api/summary").get_json()
    assert summary["total"] == 4
    assert summary["available"] == 4


def test_inventory_csv_export(client):
    response = client.get('/admin/export.csv')
    assert response.status_code == 200
    assert response.mimetype == 'text/csv'
    assert b'Bay ID,Status,Vehicle Number,Driver,Last Updated' in response.data
    assert b'P-01' in response.data
