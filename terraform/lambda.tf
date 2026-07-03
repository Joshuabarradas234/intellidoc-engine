###############################################################################
# Lambda functions + IAM (least privilege per function)
###############################################################################

# ─── Shared assume-role policy ────────────────────────────────────────────────
data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

# ─── PostReceipt role: Textract + DynamoDB write + KMS + logs + xray ──────────
data "aws_iam_policy_document" "post_receipt" {
  statement {
    actions   = ["textract:AnalyzeExpense"]
    resources = ["*"]
  }
  statement {
    actions   = ["dynamodb:PutItem"]
    resources = [aws_dynamodb_table.receipts.arn]
  }
  statement {
    actions   = ["kms:GenerateDataKey", "kms:Decrypt"]
    resources = [aws_kms_key.main.arn]
  }
  statement {
    actions   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["arn:aws:logs:${var.region}:${data.aws_caller_identity.current.account_id}:*"]
  }
  statement {
    actions   = ["xray:PutTraceSegments", "xray:PutTelemetryRecords"]
    resources = ["*"]
  }
}

resource "aws_iam_role" "post_receipt" {
  name               = "${local.name_prefix}-post-receipt"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

resource "aws_iam_role_policy" "post_receipt" {
  role   = aws_iam_role.post_receipt.id
  policy = data.aws_iam_policy_document.post_receipt.json
}

# ─── GetReceipt / SearchReceipts role: DynamoDB read + KMS + logs ─────────────
data "aws_iam_policy_document" "read_receipt" {
  statement {
    actions   = ["dynamodb:GetItem", "dynamodb:BatchGetItem"]
    resources = [aws_dynamodb_table.receipts.arn]
  }
  statement {
    actions   = ["kms:Decrypt"]
    resources = [aws_kms_key.main.arn]
  }
  statement {
    actions   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["arn:aws:logs:${var.region}:${data.aws_caller_identity.current.account_id}:*"]
  }
  statement {
    actions   = ["xray:PutTraceSegments", "xray:PutTelemetryRecords"]
    resources = ["*"]
  }
}

resource "aws_iam_role" "read_receipt" {
  name               = "${local.name_prefix}-read-receipt"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

resource "aws_iam_role_policy" "read_receipt" {
  role   = aws_iam_role.read_receipt.id
  policy = data.aws_iam_policy_document.read_receipt.json
}

# ─── Package + deploy the three functions ─────────────────────────────────────
# The handlers import from a shared `common/` package. We stage each function's
# own code + a copy of `common/` into a build dir, then zip that, so the shared
# module is present in every Lambda package at runtime.
locals {
  lambdas = {
    post_receipt = {
      source = "post_receipt"
      role   = aws_iam_role.post_receipt.arn
    }
    get_receipt = {
      source = "get_receipt"
      role   = aws_iam_role.read_receipt.arn
    }
    search_receipts = {
      source = "search_receipts"
      role   = aws_iam_role.read_receipt.arn
    }
  }
}

# Stage function code + shared common/ into build/<fn>/ before archiving.
resource "terraform_data" "stage" {
  for_each = local.lambdas

  triggers_replace = {
    fn_hash     = sha1(join("", [for f in fileset("${path.module}/../src/${each.value.source}", "**") : filesha1("${path.module}/../src/${each.value.source}/${f}")]))
    common_hash = sha1(join("", [for f in fileset("${path.module}/../src/common", "**") : filesha1("${path.module}/../src/common/${f}")]))
  }

  provisioner "local-exec" {
    interpreter = ["bash", "-c"]
    command     = <<-CMD
      set -e
      dest="${path.module}/build/${each.key}"
      rm -rf "$dest" && mkdir -p "$dest/common"
      cp ${path.module}/../src/${each.value.source}/*.py "$dest/"
      cp ${path.module}/../src/common/*.py "$dest/common/"
    CMD
  }
}

data "archive_file" "lambda" {
  for_each   = local.lambdas
  type       = "zip"
  source_dir = "${path.module}/build/${each.key}"
  output_path = "${path.module}/dist/${each.key}.zip"

  depends_on = [terraform_data.stage]
}

resource "aws_lambda_function" "fn" {
  for_each         = local.lambdas
  function_name    = "${local.name_prefix}-${replace(each.key, "_", "-")}"
  role             = each.value.role
  handler          = "handler.handler"
  runtime          = "python3.12"
  timeout          = 30
  memory_size      = 256
  filename         = data.archive_file.lambda[each.key].output_path
  source_code_hash = data.archive_file.lambda[each.key].output_base64sha256

  tracing_config { mode = "Active" } # X-Ray

  environment {
    variables = {
      RECEIPTS_TABLE      = aws_dynamodb_table.receipts.name
      OPENSEARCH_INDEX    = "receipts"
      OPENSEARCH_ENDPOINT = aws_opensearch_domain.search.endpoint
    }
  }
}

resource "aws_cloudwatch_log_group" "lambda" {
  for_each          = local.lambdas
  name              = "/aws/lambda/${local.name_prefix}-${replace(each.key, "_", "-")}"
  retention_in_days = 90
}
