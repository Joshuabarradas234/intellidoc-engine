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

## Architecture Diagram

![Architecture Diagram](Lambda%20Environment%20Variables.png)

The IntelliDoc Engine follows a serverless microservices architecture with clear separation of concerns across multiple layers:

**Frontend Layer:** React-based upload interface that communicates with the backend via REST API calls, providing users with an intuitive document submission experience.

**API Gateway Layer:** Centralized entry point that handles request routing, authentication, and rate limiting while providing a unified interface for all backend services.

**Processing Layer:** Lambda functions orchestrate the document workflow - from initial upload handling through OCR text extraction via AWS Textract, to final indexing and storage operations.

**Storage Layer:** DynamoDB provides fast, scalable NoSQL storage for document metadata and extracted content, while OpenSearch enables powerful full-text search capabilities across all processed documents.

**Monitoring Layer:** CloudWatch captures comprehensive logs and metrics, while X-Ray provides distributed tracing for performance optimization and debugging.

This architecture enables automatic scaling, cost-effective pay-per-use pricing, and enterprise-grade security through IAM roles and least-privilege access patterns.

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

## Documentation & Screenshots

### Core Documentation
- **[Backend Architecture Deep Dive](Backend%20Architecture%20Deep%20Dive.md)** — Lambda functions, IAM roles, DynamoDB structure
- **[Frontend Implementation](Frontend.md)** — React upload form and API integration
- **[Monitoring & Logging](Monitoring_Logging.md)** — CloudWatch metrics, alarms, and X-Ray tracing
- **[Testing & Validation](Testing_Validation.md)** — Postman API tests and validation
- **[Deployment & Security](Deployment_Security.md)** — Infrastructure setup and security configuration

### Key Screenshots
- **[Frontend Upload Form](frontendUpload%20Form.png)** — React-based document upload interface
- **[Lambda Functions List](lambda-functions-list.png)** — AWS Lambda function overview
- **[Lambda Environment Variables](Lambda%20Environment%20Variables.png)** — Configuration and environment setup
- **[IAM Role Permissions](iam-role-permissions.png)** — Security and access control
- **[IAM Policy JSON](iam-policy-json.png)** — Detailed permission policies
- **[API Gateway Methods](api-gateway-methods.png)** — REST API endpoint configuration
- **[DynamoDB Item Form](dynamodb-item-form.png)** — Document metadata storage
- **[DynamoDB Item JSON](dynamodb-item-json.png)** — Structured data format
- **[Network POST Receipt](network%20post%20receipt%20200.png)** — Successful API response
- **[Network POST Receipt Details](network%20post%20receipt%20details.png)** — Detailed request/response

---

## Repository Structure
