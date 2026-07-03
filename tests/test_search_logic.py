"""Unit tests for the search handler's pure helpers."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "search_receipts"))

from search_logic import extract_query, ids_from_opensearch_hits  # noqa: E402


def test_extract_query_normal():
    assert extract_query({"query": "coffee"}) == "coffee"

def test_extract_query_trims_whitespace():
    assert extract_query({"query": "  coffee  "}) == "coffee"

def test_extract_query_absent():
    assert extract_query(None) is None
    assert extract_query({}) is None
    assert extract_query({"query": "   "}) is None

def test_ids_from_hits():
    body = {"hits": {"hits": [{"_id": "a"}, {"_id": "b"}]}}
    assert ids_from_opensearch_hits(body) == ["a", "b"]

def test_ids_from_hits_source_fallback():
    body = {"hits": {"hits": [{"_source": {"receipt_id": "x"}}]}}
    assert ids_from_opensearch_hits(body) == ["x"]

def test_ids_from_empty():
    assert ids_from_opensearch_hits({}) == []
    assert ids_from_opensearch_hits({"hits": {"hits": []}}) == []
