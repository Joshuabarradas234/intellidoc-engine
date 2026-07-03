"""
Tests for handler-level pure logic (request parsing, response shaping) that
doesn't require AWS. We import the handler modules with boto3 clients stubbed so
import succeeds without credentials.
"""
import base64
import importlib
import json
import os
import sys
import types

import pytest

SRC = os.path.join(os.path.dirname(__file__), "..", "src")


@pytest.fixture(autouse=True)
def _stub_boto3(monkeypatch):
    """Stub boto3 so handler modules import without AWS credentials/network."""
    fake = types.ModuleType("boto3")

    class _Res:
        def Table(self, *_a, **_k):
            return self
        def put_item(self, *_a, **_k):
            return {}
        def get_item(self, *_a, **_k):
            return {}
        def batch_get_item(self, *_a, **_k):
            return {}

    fake.client = lambda *a, **k: object()
    fake.resource = lambda *a, **k: _Res()
    fake.Session = lambda *a, **k: types.SimpleNamespace(get_credentials=lambda: None)
    monkeypatch.setitem(sys.modules, "boto3", fake)
    yield


def _load(module_dir, module_name):
    path = os.path.join(SRC, module_dir)
    # `src` on path so `common` is importable as a package (matches deploy bundling)
    for p in (os.path.abspath(SRC), os.path.abspath(path)):
        if p not in sys.path:
            sys.path.insert(0, p)
    if module_name in sys.modules:
        del sys.modules[module_name]
    return importlib.import_module(module_name)


# ── post_receipt._decode_image ────────────────────────────────────────────────

def test_decode_image_base64_flag():
    handler = _load("post_receipt", "handler")
    raw = b"hello-bytes"
    event = {"body": base64.b64encode(raw).decode(), "isBase64Encoded": True}
    assert handler._decode_image(event) == raw

def test_decode_image_json_envelope():
    handler = _load("post_receipt", "handler")
    raw = b"image-data"
    event = {"body": json.dumps({"image": base64.b64encode(raw).decode()})}
    assert handler._decode_image(event) == raw

def test_decode_image_empty_raises():
    handler = _load("post_receipt", "handler")
    with pytest.raises(ValueError):
        handler._decode_image({"body": None})


# ── response shaping ──────────────────────────────────────────────────────────

def test_post_response_shape():
    handler = _load("post_receipt", "handler")
    resp = handler._response(201, {"receipt_id": "abc"})
    assert resp["statusCode"] == 201
    assert resp["headers"]["Content-Type"] == "application/json"
    assert json.loads(resp["body"])["receipt_id"] == "abc"


# ── get_receipt: missing id → 400 ─────────────────────────────────────────────

def test_get_receipt_missing_id():
    handler = _load("get_receipt", "handler")
    resp = handler.handler({"pathParameters": {}})
    assert resp["statusCode"] == 400


# ── search: missing query → 400 ───────────────────────────────────────────────

def test_search_missing_query():
    handler = _load("search_receipts", "handler")
    resp = handler.handler({"queryStringParameters": None})
    assert resp["statusCode"] == 400
