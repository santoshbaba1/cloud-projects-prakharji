"""Quotes API — a first REST API on API Gateway + Lambda (proxy integration).

A deliberately tiny app so the focus stays on API Gateway: resources, methods,
stages, and — later — safe deployment strategies (rolling, canary, blue-green).

The function is wired to API Gateway as a **Lambda proxy integration**, so the
whole HTTP request arrives as `event` and API Gateway expects a response shaped
like `{statusCode, headers, body}`. This handler does its own path + method
routing, exactly the kind of code a proxy integration carries.

Endpoints:
  GET  /quotes        -> list all quotes
  GET  /quotes/{id}   -> one quote by id
  POST /quotes        -> add a quote (body: {"text": "...", "author": "..."})
  GET  /version       -> reports APP_VERSION (so you can SEE which version a
                         canary/blue-green deploy is serving)

State note: quotes live in memory and reset on every cold start. That is fine —
this project teaches API Gateway deployment, not persistence. Project 2
(api-gateway-http-dynamodb-crud) adds a real DynamoDB store.
"""
import os
import json

APP_VERSION = os.environ.get("APP_VERSION", "1.0.0")

QUOTES = [
    {"id": 1, "text": "Premature optimization is the root of all evil.", "author": "Knuth"},
    {"id": 2, "text": "Simplicity is prerequisite for reliability.", "author": "Dijkstra"},
]


def _response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def _method(event):
    # REST API proxy events carry the verb at httpMethod.
    return event.get("httpMethod") or event.get("requestContext", {}).get(
        "http", {}
    ).get("method", "GET")


def _path(event):
    return event.get("path") or event.get("resource") or "/"


def _quote_id(event):
    params = event.get("pathParameters") or {}
    raw = params.get("id")
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def list_quotes():
    return _response(200, {"version": APP_VERSION, "count": len(QUOTES), "quotes": QUOTES})


def get_quote(event):
    qid = _quote_id(event)
    for q in QUOTES:
        if q["id"] == qid:
            return _response(200, q)
    return _response(404, {"error": f"no quote with id {qid}"})


def add_quote(event):
    try:
        payload = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return _response(400, {"error": "body must be valid JSON"})

    text = (payload.get("text") or "").strip()
    if not text:
        return _response(400, {"error": "field 'text' is required"})

    new_quote = {
        "id": max((q["id"] for q in QUOTES), default=0) + 1,
        "text": text,
        "author": (payload.get("author") or "Anonymous").strip(),
    }
    QUOTES.append(new_quote)
    return _response(201, new_quote)


def version():
    return _response(200, {"version": APP_VERSION})


def handler(event, context):
    method = _method(event)
    path = _path(event)

    if path.rstrip("/") == "/version":
        return version()

    if path.startswith("/quotes"):
        if method == "GET" and (event.get("pathParameters") or {}).get("id"):
            return get_quote(event)
        if method == "GET":
            return list_quotes()
        if method == "POST":
            return add_quote(event)
        return _response(405, {"error": f"{method} not allowed on {path}"})

    return _response(404, {"error": f"no route for {method} {path}"})
