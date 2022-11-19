provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_service_account" "default" {
  account_id = var.service_account_name
  display_name = "ECB API Caller Cloud Function SA"
}

resource "google_project_iam_binding" "project" {
  project = var.project_id
  role    = "roles/cloudsql.client"

  members = [
    "serviceAccount:${google_service_account.default.email}",
  ]
}

# If needed creates GCP Bucket where source code zip file is going to be uploaded
resource "google_storage_bucket" "source_code" {
  name                        = "ecb-api-caller-source-code-location"
  storage_class               = "STANDARD"
  location                    = var.region
  uniform_bucket_level_access = false
}

# Compress source code for GCP Function
data "archive_file" "source" {
  type        = "zip"
  source_dir  = "${path.root}/cloud_function"
  output_path = "${path.root}/zip_to_cloud_function.zip"
}

# Upload source code to Bucket
resource "google_storage_bucket_object" "zip" {
  name   = "cloud-function-source-code-for-${var.cloud_function_name}.zip"
  bucket = google_storage_bucket.source_code.name
  source = data.archive_file.source.output_path
}

# pubsub topic
resource "google_pubsub_topic" "default" {
  name = "cloud-function-${var.cloud_function_name}"
}

resource "google_cloud_scheduler_job" "default" {
  name = "cloud-function-${var.cloud_function_name}"
  description = "Scheduler to trigger the cloud function: ${var.cloud_function_name}"
  schedule = "30 0 * * *"

  pubsub_target {
    topic_name = google_pubsub_topic.default.id
    data = base64encode("Trigger Cloud Function")
    attributes = {
      days_to_register = 10
    }
  }
}

# Secrets definition
data "google_secret_manager_secret_version" "database_name" {
  secret = var.secret_database_name
}

data "google_secret_manager_secret_version" "port" {
  secret = var.secret_port
}

data "google_secret_manager_secret_version" "server" {
  secret = var.secret_server
}

data "google_secret_manager_secret_version" "db_user" {
  secret = var.secret_db_user
}

data "google_secret_manager_secret_version" "db_password" {
  secret = var.secret_db_password
}

# Create Cloud Function
resource "google_cloudfunctions_function" "ecb" {
  name                  = var.cloud_function_name
#  project               = var.project_id
  runtime               = "python38"
  available_memory_mb   = 512
  timeout               = 120
  source_archive_bucket = google_storage_bucket.source_code.name
  source_archive_object = google_storage_bucket_object.zip.name
  entry_point           = var.function_entry_point
  service_account_email = google_service_account.default.email

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = google_pubsub_topic.default.name
  }

  environment_variables = {
    DATABASE_NAME = data.google_secret_manager_secret_version.database_name.secret_data
    DATABASE_PORT_N = data.google_secret_manager_secret_version.port.secret_data
    SERVER_HOST = data.google_secret_manager_secret_version.server.secret_data
    USER_NAME = data.google_secret_manager_secret_version.db_user.secret_data
    USER_PASSWORD = data.google_secret_manager_secret_version.db_password.secret_data
  }
}