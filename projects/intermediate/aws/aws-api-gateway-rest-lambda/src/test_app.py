"""Local validation for the Quotes API handler — no AWS, no pytest required.

Run:  python test_app.py

Each test builds a fake API Gateway **proxy** event and calls handler() directly,
so you can confirm routing works before you ever click in the console.
"""
import json
import app


def event(method="GET", path="/quotes", path_params=None, body=None):
    return {
        "httpMethod": method,
        "path": path,
        "pathParameters": path_params,
        "body": body,
    }


def check(name, got, want):
    ok = got == want
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: got {got!r}, want {want!r}")
    return ok


def main():
    passed = 0
    total = 0

    print("list_quotes")
    r = app.handler(event("GET", "/quotes"), None)
    total += 1; passed += check("status", r["statusCode"], 200)
    body = json.loads(r["body"])
    total += 1; passed += check("has 2 quotes", body["count"], 2)

    print("random_quote (v2 feature)")
    r = app.handler(event("GET", "/quotes/random", {"id": "random"}), None)
    total += 1; passed += check("status", r["statusCode"], 200)
    rq = json.loads(r["body"])
    total += 1; passed += check("returns a real quote id", rq["id"] in {q["id"] for q in app.QUOTES}, True)

    print("get_quote (found)")
    r = app.handler(event("GET", "/quotes/1", {"id": "1"}), None)
    total += 1; passed += check("status", r["statusCode"], 200)

    print("get_quote (missing)")
    r = app.handler(event("GET", "/quotes/999", {"id": "999"}), None)
    total += 1; passed += check("status", r["statusCode"], 404)

    print("add_quote (valid)")
    r = app.handler(event("POST", "/quotes", body=json.dumps({"text": "Talk is cheap."})), None)
    total += 1; passed += check("status", r["statusCode"], 201)

    print("add_quote (missing text)")
    r = app.handler(event("POST", "/quotes", body=json.dumps({})), None)
    total += 1; passed += check("status", r["statusCode"], 400)

    print("version")
    r = app.handler(event("GET", "/version"), None)
    total += 1; passed += check("status", r["statusCode"], 200)

    print(f"\n{passed}/{total} checks passed")
    raise SystemExit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
