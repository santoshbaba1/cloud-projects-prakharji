"""Local validation for the serverless handler — no AWS needed.

Simulates API Gateway HTTP API v2 events so learners catch routing/JSON bugs on
their laptop before deploying.

    cd src
    python -m pytest test_app.py -v      # if pytest is installed
    python test_app.py                   # plain-Python fallback, no pytest needed
"""
import json

from app import handler


def event(path, query=None):
    return {
        "rawPath": path,
        "requestContext": {"http": {"path": path, "method": "GET"}},
        "queryStringParameters": query,
    }


def body(resp):
    return json.loads(resp["body"])


def test_index():
    resp = handler(event("/"), None)
    assert resp["statusCode"] == 200
    assert body(resp)["compute"] == "AWS Lambda"


def test_health():
    resp = handler(event("/health"), None)
    assert resp["statusCode"] == 200
    assert body(resp)["status"] == "healthy"


def test_info():
    resp = handler(event("/api/info"), None)
    assert resp["statusCode"] == 200
    assert body(resp)["runtime"] == "lambda"


def test_load_ok():
    resp = handler(event("/api/load", {"seconds": "0"}), None)
    assert resp["statusCode"] == 200
    assert body(resp)["iterations"] >= 0


def test_load_bad_input():
    resp = handler(event("/api/load", {"seconds": "abc"}), None)
    assert resp["statusCode"] == 400


def test_unknown_route():
    resp = handler(event("/nope"), None)
    assert resp["statusCode"] == 404


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
