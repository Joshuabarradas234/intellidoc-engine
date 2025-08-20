# IntelliDoc Engine — AI-Powered Document Processing on AWS

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Built with AWS Lambda](https://img.shields.io/badge/Built%20with-AWS%20Lambda-orange)](https://aws.amazon.com/lambda/) [![IaC: Terraform](https://img.shields.io/badge/IaC-Terraform-623CE4)](https://www.terraform.io/) [![Frontend: React](https://img.shields.io/badge/Frontend-React-61DAFB)](https://reactjs.org/)

> One-liner: Upload any receipt or document → extract vendor, date, and items → search everything instantly.

---

## Executive Summary

IntelliDoc Engine is a serverless AI-powered document processing pipeline that automatically extracts text from uploaded documents, classifies them, and makes the content immediately searchable.

It showcases a full-stack AWS solution using **Lambda, Textract, DynamoDB, OpenSearch, API Gateway,** and **Cognito** for secure, scalable handling of documents.

- **Problem:** Manual document processing is slow, error-prone, and makes it difficult to search through large archives of files.
- **Solution:** Automate ingestion, OCR text extraction, and indexing into a searchable database.
- **Outcome:** A scalable, pay-per-use system that processes documents in real time, enabling instant keyword search.

---

## AWS Services Overview

| Service | Purpose | Configuration |
|---------|---------|---------------|
| **Lambda** | Document processing, text extraction, indexing | Python 3.9, 512MB memory, 5min timeout |
| **API Gateway** | REST API endpoints for upload/search | CORS enabled, throttling configured |
| **Textract** | OCR text extraction from documents | Async processing for large files |
| **DynamoDB** | Document metadata & extracted text storage | On-demand billing, GSI for search |
| **OpenSearch** | Full-text search engine | t3.small.search instance |
| **S3** | Document file storage | Versioning enabled, lifecycle policies |
| **Cognito** | User authentication (optional) | JWT tokens, federated identity |
| **CloudWatch** | Logging, metrics, alarms | Custom metrics for success/error rates |
| **X-Ray** | Distributed tracing | End-to-end request tracking |

---

## Key Features

- **Automated OCR & Text Extraction** via Textract with clean, structured storage for search.
- **Document classification** stub (upgradeable to ML models).
- **Serverless processing pipeline** that auto-scales with no server management.
- **Scalable storage & search** with DynamoDB + OpenSearch.
- **Secure API** with Auth via Cognito (optional).
- **Monitoring & observability** via CloudWatch and X-Ray.
- **IAM & least privilege** with security best practices applied.

**Why it matters:** Quickly search and analyze invoices/receipts across large archives without manual review.

---

## Architecture Diagram

![Architecture Diagram](screenshots/Architecture%20Diagram.png)

The IntelliDoc Engine follows a serverless microservices architecture with clear separation of concerns across multiple layers:

**Frontend Layer:** React-based upload interface that communicates with the backend via REST API calls, providing users with an intuitive document submission experience.

**API Gateway Layer:** Centralized entry point that handles request routing, authentication, and rate limiting while providing a unified interface for all backend services.

**Processing Layer:** Lambda functions orchestrate the document workflow - from initial upload handling through OCR text extraction via AWS Textract, to final indexing and storage operations.

**Storage Layer:** DynamoDB provides fast, scalable NoSQL storage for document metadata and extracted content, while OpenSearch enables powerful full-text search capabilities across all processed documents.

**Monitoring Layer:** CloudWatch captures comprehensive logs and metrics, while X-Ray provides distributed tracing for performance optimization and debugging.

This architecture enables automatic scaling, cost-effective pay-per-use pricing, and enterprise-grade security through IAM roles and least-privilege access patterns.

---

## Documentation & Screenshots

### [Backend Architecture Deep Dive](Backend%20Architecture%20Deep%20Dive.md)
- [lambda-functions-list.png](lambda-functions-list.png)
- [Lambda Environment Variables.png](Lambda%20Environment%20Variables.png)
- [iam-role-permissions.png](iam-role-permissions.png)
- [iam-policy-json.png](iam-policy-json.png)
- [api-gateway-methods.png](api-gateway-methods.png)
- [dynamodb-item-form.png](dynamodb-item-form.png)

### [Frontend](Frontend.md)
- [frontendUpload Form.png](frontendUpload%20Form.png)
- [network post receipt 200.png](network%20post%20receipt%20200.png)
- [network post receipt details.png](network%20post%20receipt%20details.png)

### [Monitoring_Logging](Monitoring_Logging.md)
- [dynamodb-item-json.png](dynamodb-item-json.png)

### [Testing_Validation](Testing_Validation.md)
- [network post receipt 200.png](network%20post%20receipt%20200.png)
- [network post receipt details.png](network%20post%20receipt%20details.png)

### [Deployment_Security](Deployment_Security.md)
- [api-gateway-methods.png](api-gateway-methods.png)

---

## Quick Setup Guide

**Prerequisites**
- AWS CLI configured with appropriate permissions
- Terraform >= 1.0
- Node.js >= 16 for frontend
- Python 3.9+ for Lambda development

**Deployment Steps**

1. **Provision AWS resources** — S3, DynamoDB, OpenSearch, API Gateway, Cognito (optional).
2. **Deploy Lambda functions** — `upload_handler`, `textract_processor`, `indexer`, `search_api`.
3. **Connect Lambdas to events** — S3 triggers, API Gateway routes.
4. **Configure frontend** — update `aws-config.js`.
5. **Test the solution** — upload document, search keyword.

---

## How to Use

**Upload Document**

```bash
curl -X POST "<API_URL>/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/document.pdf"
Search Document

bash
Copy
curl "<API_URL>/search?query=invoice"
Testing & Results
Verified with Postman (end-to-end upload + search).
CloudWatch logs confirm successful Textract, DynamoDB, OpenSearch writes.
AWS X-Ray traces show full flow and latency breakdown.
Error handling for large/invalid files included.
Security & Cost Considerations
Least-privilege IAM roles for each Lambda.
No hardcoded secrets — env vars & AWS Secrets Manager.
Encryption at rest + in transit.
Cognito authentication (optional).
Cost-efficient serverless design — scales to zero when idle.

Future Improvements
Step Functions for orchestration.
NLP/ML enrichment with Comprehend, Bedrock, or SageMaker.
Semantic search with vector embeddings.
Advanced UI with previews and analytics.
Structured data extraction from forms/tables.
Demo Video
Watch the demo

Credits
Author: Joshua Barradas

GitHub: Joshuabarradas234
LinkedIn: Joshua Barradas

Acknowledgements: Inspired by AWS reference architectures for intelligent document processing.

License
This project is licensed under the MIT License — see the LICENSE file for details.
