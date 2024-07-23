#!/bin/sh

echo "Starting postprovisioning..."
# Retrieve service names, resource group name, and other values from environment variables
resourceGroupName=$AZURE_RESOURCE_GROUP
echo resourceGroupName: $AZURE_RESOURCE_GROUP

openAiService=$AZURE_OPENAI_NAME
echo openAiService: $openAiService

subscriptionId=$AZURE_SUBSCRIPTION_ID
echo subscriptionId: $subscriptionId

aiProjectName=$AZUREAI_PROJECT_NAME
echo aiProjectName: $aiProjectName

aiEndpointName=$AZUREAI_ENDPOINT_NAME
echo aiEndpointName: $aiEndpointName


# Ensure all required environment variables are set
if [ -z "$resourceGroupName" ] || [ -z "$openAiService" ] || [ -z "$subscriptionId" ] || [ -z "$aiProjectName" ]; then
    echo "One or more required environment variables are not set."
    echo "Ensure that AZURE_RESOURCE_GROUP, AZURE_OPENAI_NAME, AZURE_SUBSCRIPTION_ID, and AZUREAI_PROJECT_NAME are set."
    exit 1
fi

# Retrieve the keys

# Set the environment variables using azd env set
azd env set AZURE_RESOURCE_GROUP $resourceGroupName
azd env set AZURE_OPENAI_NAME $openAiService
azd env set AZURE_SUBSCRIPTION_ID $subscriptionId
azd env set AZUREAI_PROJECT_NAME $aiProjectName
azd env set AZUREAI_ENDPOINT_NAME $aiEndpointName

# Output environment variables to .env file using azd env get-values
azd env get-values > ./src/.env

echo "Script execution completed successfully."