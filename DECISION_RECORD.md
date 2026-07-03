# Decision Record — IntelliDoc Engine

> **Note on scope (read first).** The system as built and deployed is a
> **receipt / invoice processing pipeline**: Amazon Textract *AnalyzeExpense*
> extracts vendor, date, totals and line items, which are stored in DynamoDB and
> indexed in OpenSearch for search (see `Backend Architecture Deep Dive.md`, the
> Lambda source in `src/`, and the screenshots). The "legal document" customer
> scenario below was the original *design brief* used to reason about the
> architecture — the same serverless pattern (Textract → DynamoDB → OpenSearch,
> behind API Gateway + Cognito) generalises from receipts to broader document
> types, but the deployed, evidenced implementation is the receipt pipeline.
> The customer is illustrative, not a real client.

---

**Project:** IntelliDoc Engine — AI-Powered Serverless Document Processing  
**Customer (Fictional):** ClearPath Legal Services — UK legal firm processing 10,000+ documents/month  
**Author:** Joshua Barradas  
**Date:** May 2026  

---

## 1. Customer & Context

### Who is the customer?
ClearPath Legal Services is a mid-size UK legal firm processing contracts, court filings, invoices, and client correspondence — roughly 10,000 documents per month. Their current process is entirely manual: physical and scanned documents sit in local file storage, reviewed by paralegals, with no keyword search capability. Finding a specific clause in a contract from 18 months ago takes hours.

### What business problem are they solving?
Two problems with the same root cause — documents are dark data:
1. **Search is impossible.** A paralegal needs to find all contracts that mention a specific termination clause or jurisdiction. Currently this means manually opening hundreds of files.
2. **Processing is slow and error-prone.** Manual data entry from invoices and forms introduces errors and takes paralegals away from higher-value work.

**The ask:** Automate document ingestion, extract the content, and make everything instantly searchable. Target: any document searchable within 30 seconds of upload. Any keyword query returning results in under 2 seconds.

### What constraints are they operating under?
- **Data sensitivity:** Legal documents contain highly sensitive client PII and privileged communications. Security is non-negotiable — encryption at rest and in transit, access controls per user.
- **Compliance:** UK GDPR and professional legal privilege requirements. Data must stay in UK AWS regions.
- **Cost:** The firm has an IT budget of £2,000/month for this system. Must not exceed this.
- **Document volume:** Starts at 10,000 docs/month, could scale to 50,000 as more practice areas onboard.
- **User access:** 50 paralegals and solicitors need authenticated access via a simple web interface. No AWS console access — they need a front-end.

---

## 2. Candidate Architectures

### Option A — AWS Textract + Lambda + DynamoDB + OpenSearch + API Gateway + Cognito *(chosen)*
Fully serverless pipeline. S3 triggers Lambda on document upload. Lambda calls Textract for OCR extraction. Extracted text and metadata stored in DynamoDB. Content indexed in OpenSearch for full-text search. API Gateway exposes upload and search endpoints. Cognito handles user authentication. CloudWatch + X-Ray for observability.

### Option B — Textract + Lambda + RDS (PostgreSQL) with full-text search extension
Replace DynamoDB + OpenSearch with a single PostgreSQL database. PostgreSQL has a full-text search extension (tsvector/tsquery). Simpler stack — fewer services.

### Option C — AWS Textract + SageMaker for classification + OpenSearch
Add an ML classification layer using SageMaker to automatically tag documents by type (invoice, contract, court filing) before indexing. More powerful but more complex.

---

## 3. Chosen Design

**S3 → Lambda (trigger) → Textract → Lambda (processor) → DynamoDB + OpenSearch**, with API Gateway + Cognito exposing the upload and search APIs, and CloudWatch + X-Ray for full observability.

**Flow:**
```
User → API Gateway → Upload Lambda → S3
                                      ↓ (S3 trigger)
                               Textract Processor Lambda
                                      ↓
                    DynamoDB (metadata)   OpenSearch (full-text index)
                                      ↓
                          Search Lambda ← API Gateway ← User query
```

---

## 4. Why I Chose Each AWS Service (Design Reasoning)

### AWS Textract over third-party OCR (Google Vision, Azure Form Recognizer)
Textract extracts structured data from documents — not just raw text, but tables, forms, and key-value pairs. For legal invoices and forms, this structured extraction is valuable: you can extract "Invoice Total: £12,450" as a structured field, not just a string buried in text. It's also AWS-native — same IAM, same billing, same region (UK). Azure Form Recognizer is comparable, but cross-cloud adds latency and complexity. Google Vision is cheaper per page but doesn't extract tables/forms. For structured legal documents, Textract's form and table extraction justified the cost premium.

### OpenSearch over DynamoDB alone for search
DynamoDB is excellent for key-value lookups (give me document metadata by ID), but it can't do full-text keyword search across all 10,000 documents. The only way to search DynamoDB by content is a full table scan — slow and expensive. OpenSearch is purpose-built for full-text search: inverted index, relevance scoring, fuzzy matching, boolean queries. The architecture uses both: DynamoDB as the source of truth for metadata (fast point lookups), OpenSearch as the search index (fast full-text queries).

### OpenSearch over PostgreSQL full-text search (Option B)
PostgreSQL full-text search works well at small scale but has limitations: no native horizontal scaling, relevance scoring is basic, and running an RDS instance 24/7 costs £50–150/month even when idle. OpenSearch on t3.small is ~£25/month and scales horizontally when needed. For a search-first use case like this, a purpose-built search engine outperforms a relational database's text search extension. The trade-off: two data stores to manage instead of one. Accepted because each does its job well.

### Lambda over ECS/EC2 for document processing
Document processing is bursty: quiet overnight and on weekends, then a batch of 200 documents uploaded Monday morning. Lambda scales to zero when idle and handles bursts automatically. ECS Fargate would cost £30–80/month for a task running 24/7. At 10,000 documents/month (333/day average), each document takes ~3–10 seconds in Textract. That's about 55 minutes of total compute per day — Lambda pays for 55 minutes, not 24 hours.

### Cognito over custom authentication
ClearPath has 50 users needing authenticated access. Building custom authentication (JWT generation, password reset, MFA) would take weeks and introduce security risk if implemented incorrectly. Cognito handles user pools, password policies, MFA, and JWT token issuance out of the box. Integration with API Gateway is native — one Cognito authorizer on the API Gateway, and all routes are protected. The trade-off: Cognito's UI customisation is limited, but for internal business tooling this is acceptable.

### API Gateway over ALB
The interface is a REST API with two endpoints: POST /upload and GET /search. API Gateway's request/response transformation, built-in throttling (rate limit per user via Cognito), and native Lambda integration made it the right choice. An ALB would need a custom Lambda integration layer and doesn't provide the same API key/throttling features. For a simple two-endpoint API, API Gateway is lower ops burden.

### Why NOT add SageMaker classification (Option C) now
A SageMaker classification model to auto-tag documents (invoice vs contract vs court filing) would add significant value. However: it requires training data (labelled documents), MLOps infrastructure, and ongoing model maintenance. ClearPath's immediate pain is search — they need to find documents, not categorise them. Classification is a Phase 2 enhancement once the search foundation is stable. Adding it now would delay time-to-value by 4–6 weeks for a feature the customer didn't ask for initially.

---

## 5. Trade-off Scorecard

| Dimension | Option A (chosen) | Option B: RDS | Option C: + SageMaker |
|---|---|---|---|
| **Search quality** | High (OpenSearch) ✅ | Medium (PG full-text) ⚠️ | High ✅ |
| **Cost at 10k docs/month** | ~£90–150/month ✅ | ~£80–130/month ✅ | ~£200–350/month ❌ |
| **Ops burden** | Low (serverless) ✅ | Medium (RDS maintenance) ⚠️ | High (MLOps) ❌ |
| **Time to first working system** | 2–3 weeks ✅ | 2–3 weeks ✅ | 6–8 weeks ❌ |
| **Scales to 100k docs/month** | Yes ✅ | Needs migration ⚠️ | Yes ✅ |
| **Security** | High (Cognito + IAM) ✅ | High ✅ | High ✅ |

---

## 6. Cost Model

**Assumptions:** 10,000 documents/month, average 3 pages each (30,000 pages), 50 users, 500 searches/day, eu-west-2 (London).

| Service | Unit cost | Volume | Monthly cost |
|---|---|---|---|
| S3 (document storage, 1 year) | $0.023/GB | ~10GB | £2 |
| Textract (forms/tables) | $0.065/page | 30,000 pages | £163 |
| Lambda (processing) | $0.0000166667/GB-s | ~300 processing-hours | £8 |
| DynamoDB (on-demand) | $1.25/million writes | 10,000 writes | £1 |
| OpenSearch (t3.small) | ~$25/month | 1 instance | £20 |
| API Gateway | $3.50/million calls | 15,000 calls/month | £0.50 |
| Cognito | Free up to 50k MAU | 50 users | £0 |
| CloudWatch + X-Ray | ~flat | — | £5 |
| **Total** | | | **~£200/month** |

**Top 3 cost drivers:**
1. **Textract (~£163/month)** — dominates at high page volumes; cost is per page processed
2. **OpenSearch (~£20/month)** — fixed cluster cost regardless of query volume
3. **Lambda (~£8/month)** — grows with document volume, but cheaply

**Well within the £2,000/month budget.** Textract is the dial to watch.

---

## 7. At 10× Scale (100,000 documents/month)

**What breaks first:** Textract cost reaches ~£1,630/month, still manageable. OpenSearch t3.small becomes a bottleneck for query performance and index size — needs to scale up to t3.medium or add replicas (~£60–80/month).

**What I'd change at 10× scale:**

1. **Async Textract with Step Functions.** At high volume, synchronous Textract calls in Lambda can hit timeout limits for large documents. Step Functions orchestrates async Textract jobs: StartDocumentAnalysis → wait → GetDocumentAnalysis → index. This is more reliable for large PDFs.

2. **Textract cost optimisation via page-level sampling.** For documents where full extraction isn't needed (e.g., long appendices that are rarely searched), extract the first 5 pages only. A tagging system on upload (document type = contract/invoice/misc) can drive selective processing.

3. **OpenSearch scaling.** Move from t3.small single-node to a 2-node t3.medium cluster for high availability and better query throughput. Add OpenSearch's UltraWarm for cold storage of older documents at ~80% cost reduction.

4. **S3 Intelligent Tiering for older documents.** Documents older than 90 days move to Infrequent Access automatically, reducing storage costs as the archive grows.
