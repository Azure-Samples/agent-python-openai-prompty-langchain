using './main.bicep'

param environmentName = readEnvironmentVariable('AZURE_ENV_NAME', 'MY_ENV')
param resourceGroupName = readEnvironmentVariable('AZURE_RESOURCE_GROUP', '')
param location = readEnvironmentVariable('AZURE_LOCATION', 'eastus2')
param endpointName = readEnvironmentVariable('AZUREAI_ENDPOINT_NAME', '')
param workspaceName = readEnvironmentVariable('AZURE_WORKSPACE_NAME', '')

