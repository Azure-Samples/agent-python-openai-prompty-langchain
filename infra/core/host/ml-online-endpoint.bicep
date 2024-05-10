metadata description = 'Creates an Azure Container Registry.'
param name string
param serviceName string
param location string = resourceGroup().location
param tags object = {}
param workspaceName string
param kind string = 'Managed'
param authMode string = 'Key'

resource workspace 'Microsoft.MachineLearningServices/workspaces@2023-08-01-preview' existing = {
  name: workspaceName
}
resource endpoint 'Microsoft.MachineLearningServices/workspaces/onlineEndpoints@2023-10-01' = {
  name: name
  location: location
  parent: workspace
  kind: kind
  tags: union(tags, { 'azd-service-name': serviceName })
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    authMode: authMode
  }
}



output name string = endpoint.name
output scoringEndpoint string = endpoint.properties.scoringUri
output swaggerEndpoint string = endpoint.properties.swaggerUri
output principalId string = endpoint.identity.principalId
