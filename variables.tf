variable "project_id" {
  type        = string
  description = "Name of the Google Project"
}

variable "region" {
  type        = string
  default     = "europe-west2"
  description = "Location for the resources"
}

variable "cloud_function_name" {
  type        = string
  description = "Name of the ECB Api Caller Cloud Function"
}

variable "function_entry_point" {
  type        = string
  default     = "function_entry_point"
  description = "Name of the function entry point for the Python solution at main.py"
}

variable "secret_database_name" {
  type        = string
  description = "Keyword of secret database name"
}

variable "secret_port" {
  type        = string
  description = "Keyword of secret database port"
}

variable "secret_server" {
  type        = string
  description = "Keyword of secret database address"
}

variable "secret_db_user" {
  type        = string
  description = "Keyword of secret for database user name"
}

variable "secret_db_password" {
  type        = string
  description = "Keyword of secret for database user password"
}

variable "service_account_name" {
  type        = string
  description = "Name of the Service Account"
}