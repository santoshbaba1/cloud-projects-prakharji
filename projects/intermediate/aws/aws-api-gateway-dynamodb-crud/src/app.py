"""Tasks API — a CRUD service on API Gateway (HTTP API) + Lambda + DynamoDB.

Project 2 of the API Gateway series. Where Project 1 used a REST API with in-memory
state, this one uses the newer, cheaper **HTTP API** and stores tasks in a real
**DynamoDB** table — so the full set of HTTP verbs maps to real persistence:

  GET    /tasks          -> list all tasks
  GET    /tasks/{id}     -> one task
  POST   /tasks          -> create a task   (body: {"title": "...", "done": false})
  PUT    /tasks/{id}     -> update a task   (body: any of title/done)
  DELETE /tasks/{id}     -> delete a task
  GET    /version        -> APP_VERSION (watch which release serves a canary/blue-green flip)

HTTP API uses **payload format v2.0**: the method is at
event["requestContext"]["http"]["method"] and the path at event["rawPath"].

Deployment note: the HTTP API has no native canary release (that's a REST-only
feature). Every deployment strategy in this project — rolling, canary, blue-green —
is done at the **Lambda alias** level. See steps/05–07.
"""
import os
import json
import uuid

import boto3

TABLE_NAME = os.environ.get("TABLE_NAME", "tasks")
APP_VERSION = os.environ.get("APP_VERSION", "1.0.0")

_table = boto3.resource("dynamodb").Table(TABLE_NAME)


def _response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def _method(event):
    return event.get("requestContext", {}).get("http", {}).get("method", "GET")


def _path(event):
    return event.get("rawPath") or "/"


def _task_id(event):
    return (event.get("pathParameters") or {}).get("id")


def list_tasks():
    items = _table.scan().get("Items", [])
    return _response(200, {"version": APP_VERSION, "count": len(items), "tasks": items})


def get_task(event):
    tid = _task_id(event)
    item = _table.get_item(Key={"id": tid}).get("Item")
    if not item:
        return _response(404, {"error": f"no task with id {tid}"})
    return _response(200, item)


def create_task(event):
    try:
        payload = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return _response(400, {"error": "body must be valid JSON"})

    title = (payload.get("title") or "").strip()
    if not title:
        return _response(400, {"error": "field 'title' is required"})

    item = {"id": str(uuid.uuid4()), "title": title, "done": bool(payload.get("done", False))}
    _table.put_item(Item=item)
    return _response(201, item)


def update_task(event):
    tid = _task_id(event)
    if not _table.get_item(Key={"id": tid}).get("Item"):
        return _response(404, {"error": f"no task with id {tid}"})

    try:
        payload = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return _response(400, {"error": "body must be valid JSON"})

    updates = {}
    if "title" in payload:
        updates["title"] = str(payload["title"]).strip()
    if "done" in payload:
        updates["done"] = bool(payload["done"])
    if not updates:
        return _response(400, {"error": "nothing to update (send title and/or done)"})

    expr = "SET " + ", ".join(f"#{k} = :{k}" for k in updates)
    names = {f"#{k}": k for k in updates}
    values = {f":{k}": v for k, v in updates.items()}
    result = _table.update_item(
        Key={"id": tid},
        UpdateExpression=expr,
        ExpressionAttributeNames=names,
        ExpressionAttributeValues=values,
        ReturnValues="ALL_NEW",
    )
    return _response(200, result["Attributes"])


def delete_task(event):
    tid = _task_id(event)
    _table.delete_item(Key={"id": tid})
    return _response(204, {})


def version():
    return _response(200, {"version": APP_VERSION})


def handler(event, context):
    method = _method(event)
    path = _path(event)

    if path.rstrip("/") == "/version":
        return version()

    has_id = bool(_task_id(event))

    if path.startswith("/tasks"):
        if method == "GET" and has_id:
            return get_task(event)
        if method == "GET":
            return list_tasks()
        if method == "POST":
            return create_task(event)
        if method == "PUT" and has_id:
            return update_task(event)
        if method == "DELETE" and has_id:
            return delete_task(event)
        return _response(405, {"error": f"{method} not allowed on {path}"})

    return _response(404, {"error": f"no route for {method} {path}"})
