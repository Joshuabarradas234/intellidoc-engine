variable "region" {
  description = "AWS region (UK data residency)"
  type        = string
  default     = "eu-west-2"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "prod"
}
