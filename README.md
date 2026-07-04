# IntelliDoc Engine — Serverless Receipt Processing on AWS

[![CI](https://github.com/Joshuabarradas234/intellidoc-engine/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Joshuabarradas234/intellidoc-engine/actions/workflows/ci.yml)

A serverless pipeline that turns uploaded receipts/invoices into structured,
searchable data. A receipt is sent to the API, **Amazon Textract (AnalyzeExpense)**
extracts the vendor, date, totals and line items, the structured record is stored
in **DynamoDB**, and the text is indexed in **OpenSearch** for full-text search —
all behind an **API Gateway** REST API authenticated with **Cognito**. Region:
`eu-west-2` (London).

> **What this repo is:** the Infrastructure-as-Code (Terraform) and Lambda source
> for a system I designed and deployed to AWS. The `screenshots/` and `evidence/`
> folders show the deployed resources running. The scenario used to frame the
> design is illustrative, not a real client.


https://github.com/user-attachments/assets/d86a2b77-f042-42a2-b7a1-fde6b32008b1


## Architecture

```
                    POST /receipt (Cognito-authed)
Client -> API Gateway -> PostReceipt Lambda -> Textract (AnalyzeExpense)
                              |                        |
                              |<-------- structured fields
                              +--> DynamoDB   (structured receipt record)
                              +--> OpenSearch (full-text index)

                    GET /receipts?query=...  (Cognito-authed)
Client -> API Gateway -> SearchReceipts Lambda -> OpenSearch (match)
                              +--> DynamoDB BatchGetItem (hydrate results)

                    GET /receipt/{id}
Client -> API Gateway -> GetReceipt Lambda -> DynamoDB GetItem
```

## The three Lambdas

| Function | Route | Responsibility |
|---|---|---|
| **PostReceipt** | `POST /receipt` | Calls Textract AnalyzeExpense, stores the structured record in DynamoDB, indexes text in OpenSearch |
| **GetReceipt** | `GET /receipt/{id}` | Fetches a single structured receipt from DynamoDB |
| **SearchReceipts** | `GET /receipts?query=` | Full-text search in OpenSearch, then hydrates the matches from DynamoDB |

## AWS services & why

| Service | Role | Why |
|---|---|---|
| **Textract (AnalyzeExpense)** | OCR + structured extraction | Purpose-built for receipts/invoices — vendor, date, totals, line items as fields |
| **Lambda** | Processing + API handlers | Event-driven, scales to zero — receipt processing is bursty |
| **DynamoDB** | Structured record store | Key-value access by `receipt_id`; PITR + KMS encryption |
| **OpenSearch** | Full-text index | Purpose-built search; outperforms relational full-text at scale |
| **API Gateway** | REST API | Native Lambda proxy integration, per-method Cognito auth |
| **Cognito** | Authentication | User pools + optional MFA + JWT — no custom auth to build |
| **KMS** | Encryption at rest | Customer-managed key (rotation on) for DynamoDB, S3, OpenSearch |
| **CloudWatch + X-Ray** | Observability | Alarms on error rate; end-to-end request tracing |

## The extraction logic is tested

The Textract-response parsing (money normalisation, summary-field mapping, line
items) is isolated as pure functions in
[`src/common/receipt_parser.py`](src/common/receipt_parser.py) and the search
handler's query logic in
[`src/search_receipts/search_logic.py`](src/search_receipts/search_logic.py),
so both are unit-testable without AWS:

```bash
pip install pytest
pytest tests/ -q      # 23 tests
```

## CI

GitHub Actions runs the unit tests and `terraform validate` + `terraform fmt` on every push (`.github/workflows/ci.yml`).

## Deploy

Everything is Terraform:

```bash
cd terraform
terraform init
terraform apply    # region defaults to eu-west-2
```

Terraform packages the three Lambdas, provisions DynamoDB, OpenSearch, the
Cognito user pool, API Gateway with a Cognito authorizer, the KMS key, and the
CloudWatch alarm — and outputs the API base URL.

## Security & compliance

- **Cognito** user pools with optional MFA and a strong password policy
- **Least-privilege IAM** — PostReceipt writes DynamoDB + calls Textract; Get/Search roles are read-only
- **KMS encryption at rest** across DynamoDB, S3 and OpenSearch; S3 public access fully blocked
- **UK data residency** — everything in `eu-west-2`
- **No PII in logs**; every request traced with X-Ray

## Evidence

`screenshots/` and `evidence/` contain the deployed system running: the Lambda
function list, API Gateway methods, DynamoDB items, the Cognito user pool,
CloudWatch alarms and custom metrics, X-Ray trace map, and Postman request/response
for a successful receipt POST.

## Repository layout

```
src/
  common/receipt_parser.py     # pure Textract-response parser (tested)
  common/opensearch_client.py  # thin SigV4 OpenSearch wrapper
  post_receipt/handler.py      # POST /receipt
  get_receipt/handler.py       # GET /receipt/{id}
  search_receipts/handler.py   # GET /receipts?query=
  search_receipts/search_logic.py  # pure query helpers (tested)
terraform/                     # full stack as IaC
tests/                         # pytest unit tests
screenshots/ , evidence/       # deployed-system evidence
DECISION_RECORD.md             # design rationale + cost model
```

## Contact

**Joshua Barradas** · Leeds, UK
