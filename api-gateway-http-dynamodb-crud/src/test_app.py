"""Local validation for the Tasks API handler — no AWS, no pytest required.

Run:  python3 test_app.py

DynamoDB is replaced with a tiny in-memory fake, so the handler's routing and
CRUD logic are exercised without touching AWS. Each test builds a fake API
Gateway **HTTP API (payload v2.0)** event.
"""
import os
import json

os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")  # let boto3.resource() init

import app


class FakeTable:
    def __init__(self):
        self.items = {}

    def scan(self):
        return {"Items": list(self.items.values())}

    def get_item(self, Key):
        item = self.items.get(Key["id"])
        return {"Item": item} if item else {}

    def put_item(self, Item):
        self.items[Item["id"]] = Item

    def update_item(self, Key, ExpressionAttributeValues, **kwargs):
        item = self.items[Key["id"]]
        for vk, val in ExpressionAttributeValues.items():
            item[vk.lstrip(":")] = val
        return {"Attributes": item}

    def delete_item(self, Key):
        self.items.pop(Key["id"], None)


app._table = FakeTable()


def event(method="GET", path="/tasks", path_params=None, body=None):
    return {
        "rawPath": path,
        "requestContext": {"http": {"method": method, "path": path}},
        "pathParameters": path_params,
        "body": body,
    }


def check(name, got, want):
    ok = got == want
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: got {got!r}, want {want!r}")
    return ok


def main():
    passed = total = 0

    print("create_task (valid)")
    r = app.handler(event("POST", "/tasks", body=json.dumps({"title": "write tests"})), None)
    total += 1; passed += check("status", r["statusCode"], 201)
    new_id = json.loads(r["body"])["id"]

    print("create_task (missing title)")
    r = app.handler(event("POST", "/tasks", body=json.dumps({})), None)
    total += 1; passed += check("status", r["statusCode"], 400)

    print("list_tasks")
    r = app.handler(event("GET", "/tasks"), None)
    total += 1; passed += check("status", r["statusCode"], 200)
    total += 1; passed += check("count", json.loads(r["body"])["count"], 1)

    print("get_task (found)")
    r = app.handler(event("GET", f"/tasks/{new_id}", {"id": new_id}), None)
    total += 1; passed += check("status", r["statusCode"], 200)

    print("get_task (missing)")
    r = app.handler(event("GET", "/tasks/nope", {"id": "nope"}), None)
    total += 1; passed += check("status", r["statusCode"], 404)

    print("update_task")
    r = app.handler(event("PUT", f"/tasks/{new_id}", {"id": new_id}, json.dumps({"done": True})), None)
    total += 1; passed += check("status", r["statusCode"], 200)
    total += 1; passed += check("done flag", json.loads(r["body"])["done"], True)

    print("delete_task")
    r = app.handler(event("DELETE", f"/tasks/{new_id}", {"id": new_id}), None)
    total += 1; passed += check("status", r["statusCode"], 204)

    print("version")
    r = app.handler(event("GET", "/version"), None)
    total += 1; passed += check("status", r["statusCode"], 200)

    print(f"\n{passed}/{total} checks passed")
    raise SystemExit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
