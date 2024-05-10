targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('The Azure resource group where new resources will be deployed')
param resourceGroupName string = ''
@description('The Azure ML Workspace name. If ommited will be generated')
param workspaceName string = ''
@description('The name of the machine learning online endpoint. If ommited will be generated')
param endpointName string = ''
@description('The name of the azd service to use for the machine learning endpoint')
param endpointServiceName string = 'chat'

var abbrs = loadJsonContent('./abbreviations.json')
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var tags = { 'azd-env-name': environmentName }
var deploymentName =  'langchain-prompty-elasticsearch'

// Organize resources in a resource group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' existing= {
  name: resourceGroupName
}

module machineLearningEndpoint './core/host/ml-online-endpoint.bicep' = {
  name: 'endpoint'
  scope: rg
  params: {
    name: !empty(endpointName) ? endpointName : 'mloe-azd-${resourceToken}'
    location: location
    tags: tags
    serviceName: endpointServiceName
    workspaceName: workspaceName
  }
}
var MIR_PrincipalId = machineLearningEndpoint.outputs.principalId
module cognitiveServicesUser 'core/security/role.bicep' = {
  name: 'cognitive-services-user'
  scope: rg
  params: {
    principalId: MIR_PrincipalId
    roleDefinitionId: 'a97b65f3-24c7-4388-baec-2e87135dc908'
    principalType: 'ServicePrincipal'
  }
}
module mlServiceRoleDataScientist 'core/security/role.bicep' = {
  name: 'ml-service-role-data-scientist'
  scope: rg
  params: {
    principalId: MIR_PrincipalId
    roleDefinitionId: 'f6c7c914-8db3-469d-8ca1-694a8f32e121'
    principalType: 'ServicePrincipal'
  }
}


// output the names of the resources
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_RESOURCE_GROUP string = rg.name

output AZUREAI_ENDPOINT_NAME string = machineLearningEndpoint.outputs.name
output AZUREAI_ENDPOINT_SCORING_URL string = machineLearningEndpoint.outputs.scoringEndpoint
output AZURE_OPENAI_CHAT_DEPLOYMENT string = deploymentName
