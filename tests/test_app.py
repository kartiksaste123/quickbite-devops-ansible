import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "roles", "app", "files", "quickbite"))
os.environ.pop("DB_HOST", None)

from app import app  # noqa: E402


def test_index():
    client = app.test_client()
    res = client.get("/")
    assert res.status_code == 200
    assert res.get_json()["app"] == "QuickBite Food Delivery API"


def test_health_without_db():
    # no database in CI, so health should report 503
    os.environ["DB_HOST"] = "127.0.0.1"
    os.environ["DB_PORT"] = "1"
    res = app.test_client().get("/health")
    assert res.status_code == 503
    assert res.get_json()["database"] == "down"
