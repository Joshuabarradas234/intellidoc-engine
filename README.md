# IntelliDoc Engine — AI-Powered Document Processing on AWS

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

---

## 🚀 Executive Summary

**IntelliDoc Engine** is a serverless AI-powered document processing pipeline that automatically extracts text from uploaded documents, classifies them, and makes the content immediately searchable.  

It showcases a **full-stack AWS solution** using **Lambda, Textract, DynamoDB, OpenSearch, API Gateway, and Cognito** for secure, scalable handling of documents.

- **Problem:** Manual document processing is slow, error-prone, and makes it difficult to search through large archives of files.  
- **Solution:** Automate ingestion, OCR text extraction, and indexing into a searchable database.  
- **Outcome:** A scalable, pay-per-use system that processes documents in real time, enabling instant keyword search.

---

## 🏗 Architecture Diagram

![Architecture Diagram](architecture/intellidoc-architecture.png)  
*End-to-end serverless architecture of IntelliDoc Engine.*

---

## ☁ AWS Services Overview

| Service              | Role in IntelliDoc Engine |
|----------------------|---------------------------|
| **Amazon S3**        | Storage for uploaded documents; triggers OCR workflow. |
| **AWS Lambda**       | Orchestrates processing, runs code serverlessly. |
| **Amazon Textract**  | AI OCR service to extract text from documents. |
| **Amazon DynamoDB**  | Stores extracted text + metadata for retrieval. |
| **Amazon OpenSearch**| Indexes text for fast keyword searches. |
| **Amazon API Gateway**| REST API endpoints (`/upload`, `/search`). |
| **Amazon Cognito**   | (Optional) Authentication for secure API access. |
| **Amazon CloudWatch**| Logging, metrics, alarms. |
| **AWS X-Ray**        | Distributed tracing for performance analysis. |

---

## ✨ Key Features

- **Automated OCR & Text Extraction** via Textract  
- **Document Classification Stub** (upgradeable to ML models)  
- **Serverless Processing Pipeline** — auto-scales, no server mgmt  
- **Scalable Storage & Search** with DynamoDB + OpenSearch  
- **Secure API with Auth** (via Cognito)  
- **Monitoring & Observability** (CloudWatch + X-Ray)  
- **IAM & Least Privilege** — security best practices applied  

---

## 🖼 Screenshots

1. **Frontend Upload UI** – `screenshots/01-react-form.png`  
2. **Upload Confirmation** – `screenshots/02-upload-success.png`  
3. **DynamoDB Storage** – `screenshots/03-dynamodb-record.png`  
4. **OpenSearch Query Results** – `screenshots/04-opensearch-results.png`  
5. **X-Ray Trace Visualization** – `screenshots/05-xray-trace.png`  
6. **API Search Test (Postman)** – `screenshots/06-postman-search.png`  

---

## 📂 Repository Structure

```plaintext
IntelliDocEngine/
├── architecture/
│   └── intellidoc-architecture.png
├── screenshots/
│   ├── 01-react-form.png
│   ├── 02-upload-success.png
│   ├── 03-dynamodb-record.png
│   ├── 04-opensearch-results.png
│   ├── 05-xray-trace.png
│   └── 06-postman-search.png
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── App.js
│   │   └── aws-config.js
│   └── package.json
├── lambda/
│   ├── upload_handler/
│   ├── textract_processor/
│   ├── indexer/
│   ├── search_api/
│   └── common/
├── infra/
│   ├── template.yaml
│   └── terraform/
├── tests/
│   ├── postman_collection.json
│   ├── sample-documents/
│   └── integration.test.js
├── .gitignore
├── README.md
└── LICENSE


⸻

⚡ Quick Setup Guide

Prerequisites
	•	AWS Account
	•	AWS CLI or Console Access
	•	(Optional) Node.js/NPM for frontend
	•	(Optional) AWS SAM CLI / Terraform for IaC deployment

Deployment Steps
	1.	Provision AWS Resources — S3, DynamoDB, OpenSearch, API Gateway, Cognito (optional)
	2.	Deploy Lambda Functions — upload_handler, textract_processor, indexer, search_api
	3.	Connect Lambdas to Events — S3 triggers, API Gateway routes
	4.	Configure Frontend — update aws-config.js
	5.	Test the Solution — upload document, search keyword

⸻

🔌 How to Use

Upload Document

curl -X POST "<API_URL>/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/document.pdf"

Search Document

curl "<API_URL>/search?query=invoice"


⸻

🧪 Testing & Results
	•	Verified with Postman (end-to-end upload + search)
	•	CloudWatch Logs confirm successful Textract, DynamoDB, OpenSearch writes
	•	AWS X-Ray traces show full flow & latency breakdown
	•	Error handling for large/invalid files included

⸻

🔒 Security & 💰 Cost Considerations
	•	Least-Privilege IAM Roles for each Lambda
	•	No Hardcoded Secrets — env vars & AWS Secrets Manager
	•	Encryption at Rest + In Transit
	•	Cognito Authentication (optional)
	•	Cost-Efficient Serverless design — scales to zero when idle

⸻

🔮 Future Improvements
	•	Step Functions for orchestration
	•	NLP/ML enrichment with Comprehend, Bedrock, or SageMaker
	•	Semantic search with vector embeddings
	•	Advanced UI with previews and analytics
	•	Structured data extraction from forms/tables

⸻

🎥 Demo Video

📌 (Demo video link/MP4 will be added here once recorded.)

⸻

👤 Credits

Author: Joshua Barradas
	•	GitHub: Joshuabarradas234
	•	LinkedIn: Joshua Barradas

Acknowledgements: Inspired by AWS reference architectures for intelligent document processing.

⸻

📜 License

This project is licensed under the MIT License — see the LICENSE file for details.

---

This version is **GitHub-ready**:
- All headings are in proper Markdown format
- Screenshot placeholders point to `screenshots/` directory
- Architecture diagram placeholder set
- cURL commands are in syntax-highlighted code blocks
- Tables are aligned properly
- Demo video placeholder included for when you add MP4

---
