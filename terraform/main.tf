###############################################################################
# IntelliDoc Engine — serverless receipt processing pipeline
# Textract (AnalyzeExpense) -> DynamoDB -> OpenSearch, behind API Gateway,
# authenticated with Cognito. Region: eu-west-2 (London).
###############################################################################

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }
}

provider "aws" {
  region = var.region
}

data "aws_caller_identity" "current" {}

locals {
  name_prefix = "intellidoc-${var.environment}"
}

# ─── KMS ──────────────────────────────────────────────────────────────────────
resource "aws_kms_key" "main" {
  description             = "IntelliDoc — encrypts receipts at rest"
  enable_key_rotation     = true
  deletion_window_in_days = 7
}

resource "aws_kms_alias" "main" {
  name          = "alias/${local.name_prefix}"
  target_key_id = aws_kms_key.main.key_id
}

# ─── DynamoDB ─────────────────────────────────────────────────────────────────
resource "aws_dynamodb_table" "receipts" {
  name         = "${local.name_prefix}-receipts"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "receipt_id"

  attribute {
    name = "receipt_id"
    type = "S"
  }

  point_in_time_recovery { enabled = true }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.main.arn
  }

  tags = { Project = "IntelliDoc" }
}

# ─── S3 (original receipt images) ─────────────────────────────────────────────
resource "aws_s3_bucket" "receipts" {
  bucket = "${local.name_prefix}-receipts-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_public_access_block" "receipts" {
  bucket                  = aws_s3_bucket.receipts.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "receipts" {
  bucket = aws_s3_bucket.receipts.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.main.arn
    }
  }
}
