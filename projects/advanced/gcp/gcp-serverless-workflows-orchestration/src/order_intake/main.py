"""order-intake — the API's front door. Starts a workflow execution per order.

Sits behind API Gateway. It does the least possible work: validate the request has
an order_id, then kick off an asynchronous `order-fulfillment` workflow execution and
return 202 with the execution name so the caller can poll for status. All the real
orchestration (validate → charge → ship, with retries + compensation) lives in the
workflow, not here.
"""
import json
import os

import functions_framework
from google.cloud.workflows import executions_v1
from google.cloud.workflows.executions_v1 import Execution

PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT")
LOCATION = os.environ.get("WORKFLOW_LOCATION", "us-east1")
WORKFLOW = os.environ.get("WORKFLOW_NAME", "order-fulfillment")

_client = executions_v1.ExecutionsClient()


def _log(severity, message, **fields):
    print(json.dumps({"severity": severity, "message": message, **fields}))


@functions_framework.http
def order_intake(request):
    order = request.get_json(silent=True) or {}
    if "order_id" not in order:
        return {"error": "request body must be a JSON order containing order_id"}, 400

    parent = _client.workflow_path(PROJECT, LOCATION, WORKFLOW)
    execution = Execution(argument=json.dumps(order))
    response = _client.create_execution(parent=parent, execution=execution)

    _log("INFO", "workflow execution started",
         order_id=order["order_id"], execution=response.name)
    return {
        "order_id": order["order_id"],
        "execution": response.name,
        "state": response.state.name,
        "message": "order accepted; fulfillment started",
    }, 202
