output "api_base_url" {
  description = "Base URL for the receipt API"
  value       = aws_api_gateway_stage.prod.invoke_url
}

output "receipts_table" {
  description = "DynamoDB table name"
  value       = aws_dynamodb_table.receipts.name
}

output "opensearch_endpoint" {
  description = "OpenSearch domain endpoint"
  value       = aws_opensearch_domain.search.endpoint
}

output "cognito_user_pool_id" {
  description = "Cognito user pool id"
  value       = aws_cognito_user_pool.users.id
}
