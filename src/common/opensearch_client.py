"""
Thin OpenSearch client wrapper (SigV4-signed) shared by the post and search
Lambdas. Isolated here so the handlers' business logic stays testable without
a live cluster.
"""
from __future__ import annotations

import os

import boto3
from opensearchpy import AWSV4SignerAuth, OpenSearch, RequestsHttpConnection

REGION = os.environ.get("AWS_REGION", "eu-west-2")
ENDPOINT = os.environ.get("OPENSEARCH_ENDPOINT", "")


def _client() -> OpenSearch:
    credentials = boto3.Session().get_credentials()
    auth = AWSV4SignerAuth(credentials, REGION, "es")
    return OpenSearch(
        hosts=[{"host": ENDPOINT.replace("https://", ""), "port": 443}],
        http_auth=auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
    )


def index_document(index: str, doc_id: str, document: dict) -> None:
    _client().index(index=index, id=doc_id, body=document, refresh=True)


def search(index: str, query: str) -> dict:
    body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["content", "vendor"],
            }
        }
    }
    return _client().search(index=index, body=body)
