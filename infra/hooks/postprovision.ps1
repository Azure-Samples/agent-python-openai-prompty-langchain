Write-Host "Starting postprovisioning..."

# Retrieve service names, resource group name, and other values from environment variables
$resourceGroupName = $env:AZURE_RESOURCE_GROUP
Write-Host "resourceGroupName: $resourceGroupName"

$openAiService = $env:AZURE_OPENAI_NAME
Write-Host "openAiService: $openAiService"

$subscriptionId = $env:AZURE_SUBSCRIPTION_ID
Write-Host "subscriptionId: $subscriptionId"

$aiProjectName = $env:AZUREAI_PROJECT_NAME
Write-Host "aiProjectName: $aiProjectName"

$aiEndpointNAme = $env:AZUREAI_ENDPOINT_NAME
Write-Host "aiEndpointNAme: $aiEndpointNAme"

# Ensure all required environment variables are set
if ([string]::IsNullOrEmpty($resourceGroupName) -or [string]::IsNullOrEmpty($subscriptionId))-or [string]::IsNullOrEmpty($aiProjectName)) {
    Write-Host "One or more required environment variables are not set."
    Write-Host "Ensure that AZURE_RESOURCE_GROUP, AZURE_OPENAI_NAME, AZURE_SUBSCRIPTION_ID, and AZUREAI_PROJECT_NAME are set."
    exit 1
}

# Set the environment variables using azd env set
azd env set AZURE_RESOURCE_GROUP $resourceGroupName
azd env set AZURE_SUBSCRIPTION_ID $subscriptionId
azd env set AZUREAI_PROJECT_NAME $aiProjectName
azd env set AZUREAI_ENDPOINT_NAME $aiEndpointNAme


# Output environment variables to .env file using azd env get-values
azd env get-values > ./src/.env

Write-Host "Script execution completed successfully."
#Write-Host 'Installing dependencies from "requirements.txt"'
#python -m pip install -r src/summarizationapp/requirements.txt