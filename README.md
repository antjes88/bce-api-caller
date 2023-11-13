# BCE API Caller

This is a solution designed to interact with the European Central Bank (ECB) API for fetching exchange rates. 
This Ecb Exchange Rates are latter appended into a destination table in BigQuery.

## Terraform Code

The provided Terraform code automates the deployment of the python solution to fetch exchange rates from ECB API 
as a Cloud Function on Google Cloud Platform (GCP). It begins by configuring the necessary GCP provider settings, 
such as the project ID and region. The code then creates a service account for the Cloud Function, 
assigning it specific roles for interacting with BigQuery. 
It also establishes a Cloud Storage bucket to store the Cloud Function's source code, archives the source code, 
and uploads it to the designated bucket. Additionally, the configuration sets up a Pub/Sub topic and a 
Cloud Scheduler job, allowing the Cloud Function to be triggered periodically. 
Finally, it defines the Cloud Function itself. This Terraform setup streamlines the deployment process and 
ensures a consistent environment for the IRR calculator on GCP.


To execute the Python tests use next command on the CLI:

```commandline
python -m pytest -vv
```

It is needed a _.env_ file with the next settings:

```
PROJECT=
DESTINATION_TABLE=
DATASET=
```

You will also need to provide a Service Account credentials or to use a user account with the right permissions to 
interact with BigQuery.

### Python environment
To execute these tests within your machine you will need an environment with python 3.10.0 and the libraries listed in 
requirements.txt. In case you do not have such environment, you can create it as follows with conda:
 
```
conda create -n [] python=3.10.0 pip
pip install -r cloud_function/requirements.txt
```

You also need to install pytest==7.4.3 & python-dotenv==0.14.0

## GitHub Workflow
GitHub workflow automates Python testing for the project, triggered on every push  or pull requests to the main branch. 
Operating on the latest Ubuntu environment, it employs a matrix strategy to test against Python 3.10. 
The workflow initializes Python, installs project dependencies, including Pytest and Python-dotenv, 
and executes Pytest. 
Key environment variables, such as project details and service account JSON, are securely managed using GitHub Secrets. 
