"""Local validation tests for the EC2 monitored web app.

Run before deploying so learners catch problems on their laptop, not on EC2:

    cd src
    python -m pytest test_app.py -v      # if pytest is installed
    python test_app.py                   # plain-Python fallback, no pytest needed
"""
from app import app


def _client():
    app.testing = True
    return app.test_client()


def test_index():
    res = _client().get("/")
    assert res.status_code == 200
    body = res.get_json()
    assert body["service"]
    assert "instance_id" in body


def test_health():
    res = _client().get("/health")
    assert res.status_code == 200
    body = res.get_json()
    assert body["status"] == "healthy"
    assert body["uptime_seconds"] >= 0


def test_info():
    res = _client().get("/api/info")
    assert res.status_code == 200
    assert res.get_json()["python_version"]


def test_load_default():
    res = _client().get("/api/load?seconds=0")
    assert res.status_code == 200
    assert res.get_json()["iterations"] >= 0


def test_load_rejects_bad_input():
    res = _client().get("/api/load?seconds=abc")
    assert res.status_code == 400


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError as exc:
                failures += 1
                print(f"FAIL {name}: {exc}")
    raise SystemExit(1 if failures else 0)
