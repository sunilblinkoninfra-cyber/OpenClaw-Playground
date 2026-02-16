variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "container_port" {
  description = "Port exposed by container"
  type        = number
  default     = 8000
}

variable "app_count" {
  description = "Number of Docker containers to run"
  type        = number
  default     = 1
}

variable "task_cpu" {
  description = "Fargate task CPU units"
  type        = string
  default     = "256"
}

variable "task_memory" {
  description = "Fargate task memory in MB"
  type        = string
  default     = "512"
}
