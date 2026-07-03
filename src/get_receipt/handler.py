"""
GetReceiptFunction — handles GET /receipt/{id}.
Fetches a single structured receipt from DynamoDB by id.
"""
from __future__ import annotations

import json
import os

import boto3

TABLE_NAME = os.environ.get("RECEIPTS_TABLE", "Receipts")
REGION = os.environ.get("AWS_REGION", "eu-west-2")

_dynamodb = boto3.resource("dynamodb", region_name=REGION)


def _response(status: int, payload) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(payload, default=str),
    }


def handler(event, _context=None):
    receipt_id = (event.get("pathParameters") or {}).get("id")
    if not receipt_id:
        return _response(400, {"error": "receipt id is required"})

    try:
        result = _dynamodb.Table(TABLE_NAME).get_item(Key={"receipt_id": receipt_id})
    except Exception as exc:  # noqa: BLE001
        print(f"[error] DynamoDB get_item failed: {exc}")
        return _response(500, {"error": "Lookup failed"})

    item = result.get("Item")
    if not item:
        return _response(404, {"error": f"Receipt {receipt_id} not found"})

    return _response(200, item)
