# BCE API Caller
Simple Python code to download Euro exchange rates against Dollar and Pound from the BCE API to populate into a raw 
table in a Cloud SQL Database. Table schema is as follows:

```
CREATE SCHEMA bce;

CREATE TABLE bce.EuroaRatio
(
	Fecha DATE PRIMARY KEY,
	Libra NUMERIC(10,4) NOT NULL,
	Dolar NUMERIC(10,4) NOT NULL,
	Created DATE NOT NULL,
	CreatedBy VARCHAR(100) NOT NUll
);
```

Deployed with Terraform as a Cloud Function(GCP) which is triggered by a Pub/Sub Topic. Messages 
are posted to this Pub/Sub Topic by a Cloud Scheduler every day at 00:30 (midnight). The Python code is uploaded into a 
GCP Bucket. A Service Account is created and given Cloud SQL Client role so the Cloud Function can connect to Cloud SQL
instance and Secret Accessor role so it can access Secrets from Secret Manager.

## Terraform
Before Executing the Terraform code, the creation of 5 secrets on Secret Manager is needed to provide connection 
settings and credentials for the Cloud SQL instance. These are: host address, host port, database name, 
username with permission to update raw table and user password. Names for these secrets are open, 
as these names have to be provided on the file _*.tfvars_ which is not included on the repo.
Also, on the same file are provided id of the project, a name for the service account and a name for the cloud function
to create.

```terraform
secret_database_name = ""
secret_port          = ""
secret_server        = ""
secret_db_user       = ""
secret_db_password   = ""
service_account_name = ""
project_id           = ""
cloud_function_name  = ""
```

*The format for the value of the host is: "/cloudsql/{project_id}:{region}:{instance_name}"

Easier way to execute terraform code is to use an admin user. It can be done writing on CLI: 
```commandline
gcloud auth application-default login
```
Several APIs will need to be enabled. If any is not enabled, during deployment a message will be prompted to request the 
activation of the service.

## Testing
To execute the Python tests use next command on the CLI:
```commandline
python -m pytest -vv
```

It is needed a _.env_ file with the next settings and credentials to connect to a Cloud SQL instance. This file is
as follows:

```
HOST = 
DATABASE_NAME = 
USER_NAME = 
USER_PASSWORD = 
DATABASE_PORT = 
```

*In this case, host is just the IP address.