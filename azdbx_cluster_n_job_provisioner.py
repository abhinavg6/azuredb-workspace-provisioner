# This is a sample solution for how to provision AAD users and groups into a 
# Azure Databricks workspace in an automated manner. The same action could be done in
# a semi-automated manner via AAD app-based provisioning or in a manual way via
# Databricks admin console.

import os
import json

from azdbx_azure_oauth2_client import AzureOAuth2Client
from azdbx_api_client import DatabricksAPIClient

# Create the Azure OAuth2 client and get AAD tokens to invoke Databricks API
azure_oauth2_client = AzureOAuth2Client()
aad_access_token = azure_oauth2_client.get_aad_access_token()
aad_mgmt_token = azure_oauth2_client.get_aad_mgmt_token()

# Get the Azure Databricks template parameters to get the deployed workspace's name
adb_template_parameters = None
adb_template_params_path = os.path.join(
    os.path.dirname(__file__), 'arm_template_params', 'azure_databricks_npip_template_params.json')
with open(adb_template_params_path, 'r') as adb_template_params_file:
    adb_template_parameters = json.load(adb_template_params_file)

# Form the full resource id of the Azure Databricks workspace
adb_workspace_resource_id = "/subscriptions/" + os.environ.get(
    'AZURE_SUBSCRIPTION_ID', '11111111-1111-1111-1111-111111111111') + "/resourceGroups/" + \
    os.environ.get('AZURE_RESOURCE_GROUP', 'my-adb-e2-rg') + "/providers/Microsoft.Databricks/workspaces/" + \
    adb_template_parameters['workspaceName']
print("The workspace resource id is {}".format(adb_workspace_resource_id))

# Create the Databricks API client
databricks_api_client = DatabricksAPIClient(aad_access_token, aad_mgmt_token, adb_workspace_resource_id)
print("The workspace URL is {}".format(databricks_api_client.get_url_prefix()))

# Create a high-concurrency cluster to analyze processed data
cluster_id = databricks_api_client.create_cluster("high_concurrency_cluster.json")

# Set permissions for users on the cluster
databricks_api_client.set_permission_on_cluster(cluster_id, "a.a@databricks.com", "CAN_MANAGE")
databricks_api_client.set_permission_on_cluster(cluster_id, "ag@gmail.com", "CAN_ATTACH_TO")

# Create a on-demand job to run a notebook
job_id = databricks_api_client.create_job("standard_cluster_job.json")

# Set permissions for users on the job
databricks_api_client.set_permission_on_job(job_id, "a.g@databricks.com", "CAN_MANAGE")
databricks_api_client.set_permission_on_job(job_id, "ag@gmail.com", "CAN_VIEW")
