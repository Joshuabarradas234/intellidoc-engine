"""
SearchReceiptsFunction — handles GET /receipts?query=...

Searches the OpenSearch full-text index, then hydrates the matching receipts
from DynamoDB (BatchGetItem) so the response contains full structured records.
"""
from __future__ import annotations

import json
import os

import boto3

from search_logic import extract_query, ids_from_opensearch_hits

TABLE_NAME = os.environ.get("RECEIPTS_TABLE", "Receipts")
OPENSEARCH_INDEX = os.environ.get("OPENSEARCH_INDEX", "receipts")
REGION = os.environ.get("AWS_REGION", "eu-west-2")

_dynamodb = boto3.resource("dynamodb", region_name=REGION)


def _response(status: int, payload) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(payload, default=str),
    }


def _search_opensearch(query: str) -> list[str]:
    from opensearch_client import search  # deploy-time thin wrapper
    hits = search(OPENSEARCH_INDEX, query)
    return ids_from_opensearch_hits(hits)


def handler(event, _context=None):
    query = extract_query(event.get("queryStringParameters"))
    if not query:
        return _response(400, {"error": "query parameter is required"})

    try:
        ids = _search_opensearch(query)
    except Exception as exc:  # noqa: BLE001
        print(f"[error] OpenSearch query failed: {exc}")
        return _response(502, {"error": "Search failed"})

    if not ids:
        return _response(200, {"query": query, "count": 0, "results": []})

    # Hydrate full records from DynamoDB
    try:
        keys = [{"receipt_id": rid} for rid in ids]
        resp = _dynamodb.batch_get_item(RequestItems={TABLE_NAME: {"Keys": keys}})
        results = resp.get("Responses", {}).get(TABLE_NAME, [])
    except Exception as exc:  # noqa: BLE001
        print(f"[error] DynamoDB batch_get_item failed: {exc}")
        return _response(500, {"error": "Result hydration failed"})

    return _response(200, {"query": query, "count": len(results), "results": results})
