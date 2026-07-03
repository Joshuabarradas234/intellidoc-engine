"""Pure helpers for the search handler — no AWS, unit-testable."""
from __future__ import annotations

from typing import Optional


def extract_query(query_params: Optional[dict]) -> Optional[str]:
    """Pull and normalise the ?query= parameter. Returns None if absent/blank."""
    if not query_params:
        return None
    raw = query_params.get("query")
    if raw is None:
        return None
    cleaned = raw.strip()
    return cleaned or None


def ids_from_opensearch_hits(hits: dict) -> list[str]:
    """
    Extract receipt ids from an OpenSearch response body.
    Accepts the standard { "hits": { "hits": [ {"_id": ...}, ... ] } } shape.
    """
    inner = (hits or {}).get("hits", {}).get("hits", [])
    ids: list[str] = []
    for hit in inner:
        rid = hit.get("_id") or (hit.get("_source") or {}).get("receipt_id")
        if rid:
            ids.append(rid)
    return ids
