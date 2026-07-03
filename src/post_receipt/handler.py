"""
PostReceiptFunction — handles POST /receipt.

Flow:
  1. Receive a receipt image (base64 in the request body, or an S3 reference).
  2. Call Textract AnalyzeExpense to extract vendor / date / total / line items.
  3. Store the structured receipt in DynamoDB.
  4. Index the searchable text in OpenSearch.
  5. Return the new receipt id.

The pure extraction logic lives in src/common/receipt_parser.py so it can be
unit tested without AWS.
"""
from __future__ import annotations

import base64
import json
import os
import uuid
from datetime import datetime, timezone

import boto3

from common.receipt_parser import build_search_document, parse_analyze_expense

TABLE_NAME = os.environ.get("RECEIPTS_TABLE", "Receipts")
OPENSEARCH_INDEX = os.environ.get("OPENSEARCH_INDEX", "receipts")
REGION = os.environ.get("AWS_REGION", "eu-west-2")

_textract = boto3.client("textract", region_name=REGION)
_dynamodb = boto3.resource("dynamodb", region_name=REGION)


def _decode_image(event: dict) -> bytes:
    """Pull the receipt image bytes out of the API Gateway event."""
    body = event.get("body")
    if body is None:
        raise ValueError("Request body is empty")
    if event.get("isBase64Encoded"):
        return base64.b64decode(body)
    # If body is a JSON envelope like {"image": "<base64>"}
    try:
        parsed = json.loads(body)
        if isinstance(parsed, dict) and "image" in parsed:
            return base64.b64decode(parsed["image"])
    except (json.JSONDecodeError, TypeError):
        pass
    return base64.b64decode(body)


def _index_opensearch(document: dict) -> None:
    """
    Index the document in OpenSearch. Imported lazily and guarded so the
    handler still stores to DynamoDB even if the search cluster is unavailable
    (search can be back-filled; the source of truth is DynamoDB).
    """
    try:
        from opensearch_client import index_document  # thin wrapper, deploy-time
        index_document(OPENSEARCH_INDEX, document["receipt_id"], document)
    except Exception as exc:  # noqa: BLE001 - never fail the write on index error
        print(f"[warn] OpenSearch indexing failed: {exc}")


def _response(status: int, payload: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(payload),
    }


def handler(event, _context=None):
    try:
        image_bytes = _decode_image(event)
    except (ValueError, Exception) as exc:  # noqa: BLE001
        return _response(400, {"error": f"Invalid image payload: {exc}"})

    # 1. Textract AnalyzeExpense
    try:
        textract_response = _textract.analyze_expense(
            Document={"Bytes": image_bytes}
        )
    except Exception as exc:  # noqa: BLE001
        print(f"[error] Textract failed: {exc}")
        return _response(502, {"error": "Extraction failed"})

    # 2. Parse into our schema (pure, tested)
    parsed = parse_analyze_expense(textract_response)

    receipt_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    item = {
        "receipt_id": receipt_id,
        "created_at": now,
        **parsed,
    }

    # 3. Store in DynamoDB
    try:
        _dynamodb.Table(TABLE_NAME).put_item(Item=item)
    except Exception as exc:  # noqa: BLE001
        print(f"[error] DynamoDB put_item failed: {exc}")
        return _response(500, {"error": "Storage failed"})

    # 4. Index for search (best-effort)
    _index_opensearch(build_search_document(receipt_id, parsed))

    print(f"[info] Stored receipt {receipt_id} vendor={parsed.get('vendor')}")
    return _response(
        201,
        {
            "receipt_id": receipt_id,
            "vendor": parsed.get("vendor"),
            "total": parsed.get("total"),
        },
    )
