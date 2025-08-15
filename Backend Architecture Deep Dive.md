# Backend Architecture Deep Dive

## Backend Architecture Overview

The backend is built using a **serverless architecture on AWS** — primarily **AWS Lambda**, **Amazon API Gateway**, **Amazon Textract**, **Amazon DynamoDB**, and **Amazon OpenSearch Service**.

All infrastructure is defined and deployed via **Terraform**, ensuring consistency across environments and easy reproducibility.

---

## Key AWS Components

- **Amazon API Gateway** — Exposes RESTful API endpoints, integrates directly with Lambda.
- **AWS Lambda** — Executes backend logic for ingestion, retrieval, and search.
- **Amazon Textract** — Performs OCR (AnalyzeExpense API) to extract vendor, date, totals, and line items.
- **Amazon DynamoDB** — Stores structured receipt data.
- **Amazon OpenSearch Service** — Indexes receipt content for full-text search.
- **Amazon S3** *(optional)* — Can store original receipt images.
- **AWS X-Ray** — Traces requests across components.

---

## Lambda Functions and Responsibilities

| Function | Purpose |
|----------|---------|
| **PostReceiptFunction** | Handles `POST /receipt`, calls Textract, stores data in DynamoDB, indexes in OpenSearch. |
| **GetReceiptFunction** | Handles `GET /receipt/{id}`, fetches details from DynamoDB. |
| **SearchReceiptsFunction** | Handles `GET /receipts?query=...`, searches OpenSearch, fetches matching receipts from DynamoDB. |

---

### Terraform snippet for `PostReceiptFunction`

```hcl
resource "aws_lambda_function" "post_receipt" {
  function_name = "PostReceiptFunction"
  runtime       = "python3.9"
  handler       = "handlers/post_receipt.handler"
  memory_size   = 512
  timeout       = 30
  role          = aws_iam_role.lambda_exec.arn
  filename      = "lambda_functions.zip"
  environment {
    variables = {
      TABLE_NAME          = "ReceiptLines"
      OPENSEARCH_ENDPOINT = "https://my-receipts-domainID.eu-west-1.es.amazonaws.com"
      OPENSEARCH_INDEX    = "receipts-index"
    }
  }
}
📸 Screenshot 1 — AWS Lambda list view

Environment Variables
Example for PostReceiptFunction:

ini
Copy
Edit
TABLE_NAME="ReceiptLines"
OPENSEARCH_DOMAIN="receipts-search-domain"
OPENSEARCH_INDEX="receipts-index"
S3_BUCKET="receipt-uploads-bucket"
TABLE_NAME — DynamoDB table name

OPENSEARCH_DOMAIN / OPENSEARCH_INDEX — OpenSearch endpoint and index name

S3_BUCKET — Optional bucket for storing original images

📸 Screenshot 2 — Lambda environment variables panel

IAM Role & Policies
The Lambda execution role grants only the permissions needed:

json
Copy
Edit
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:UpdateItem",
        "dynamodb:Scan",
        "dynamodb:Query"
      ],
      "Resource": "arn:aws:dynamodb:<AWS_REGION>:<ACCOUNT_ID>:table/ReceiptLines"
    },
    {
      "Effect": "Allow",
      "Action": [
        "textract:AnalyzeExpense",
        "textract:DetectDocumentText"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "es:ESHttpPost",
        "es:ESHttpGet"
      ],
      "Resource": "arn:aws:es:<AWS_REGION>:<ACCOUNT_ID>:domain/receipts-search-domain/*"
    }
  ]
}
📸 Screenshot 3 — IAM role → Permissions tab

📸 Screenshot 4 — IAM policy JSON file

API Gateway Routes
Method & Path	Description
POST /receipt	Upload and process a new receipt
GET /receipt/{id}	Retrieve details of a specific receipt
GET /receipts	Search or list receipts, with optional ?query= parameter

📸 Screenshot 5 — API Gateway routes list

DynamoDB Table Structure
Table Name: ReceiptLines
Primary Key: receipt_id (String)

Example item:

json
Copy
Edit
{
  "receipt_id": "123ABC456",
  "vendor": "Coffee Shop LLC",
  "date": "2025-08-13T09:30:00Z",
  "total": 23.45,
  "items": [
    { "description": "Latte", "quantity": 2, "price": 4.50 },
    { "description": "Blueberry Muffin", "quantity": 1, "price": 3.95 }
  ],
  "s3_path": "s3://receipt-uploads-bucket/2025-08-13/receipt123.jpg"
}
📸 Screenshot 6 — DynamoDB item view (Form view)

📸 Screenshot 7 — DynamoDB item view (JSON view)

Backend Workflow
Receipt Ingestion (POST /receipt)
mermaid
Copy
Edit
sequenceDiagram
    autonumber
    participant Client
    participant APIGW as API Gateway
    participant Lambda as Lambda (PostReceiptFunction)
    participant Textract as Amazon Textract
    participant DynamoDB as Amazon DynamoDB
    participant OpenSearch as Amazon OpenSearch
    
    Client->>APIGW: HTTP POST /receipt (image)
    APIGW->>Lambda: Invoke Lambda
    Lambda->>Textract: AnalyzeExpense
    Textract-->>Lambda: Extracted data
    Lambda->>DynamoDB: Store structured receipt
    Lambda->>OpenSearch: Index for search
    Lambda-->>APIGW: Return success
    APIGW-->>Client: 200 OK
Receipt Search (GET /receipts?query=…)
mermaid
Copy
Edit
sequenceDiagram
    autonumber
    participant Client
    participant APIGW as API Gateway
    participant LambdaSearch as Lambda (SearchReceiptsFunction)
    participant OpenSearch as Amazon OpenSearch
    participant DynamoDB as Amazon DynamoDB
    
    Client->>APIGW: GET /receipts?query=coffee
    APIGW->>LambdaSearch: Invoke Lambda
    LambdaSearch->>OpenSearch: Search index
    OpenSearch-->>LambdaSearch: Matching IDs
    LambdaSearch->>DynamoDB: BatchGetItem
    DynamoDB-->>LambdaSearch: Receipt data
    LambdaSearch-->>APIGW: Return results
    APIGW-->>Client: 200 OK
