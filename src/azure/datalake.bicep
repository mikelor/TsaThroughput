param pProjectName string {
  default: 'datalake'
  minLength: 1
  maxLength: 11
}

param pEnvironment string {
  default: 'dev'
}

param pSkuName string {
  default: 'Standard_LRS'
}

param pLocation string = resourceGroup().location

var uniqueId = uniqueString(resourceGroup().id)
var storageAccountName = '${toLower(pProjectName)}${toLower(pEnvironment)}${uniqueId}'
var storageContainerName = 'root'

resource storageAccountResource 'Microsoft.Storage/storageAccounts@2019-06-01' = {
  name: storageAccountName
  location: pLocation
  kind: 'StorageV2'
  sku: {
    name: pSkuName
  }
  properties: {
    isHnsEnabled: true
  }
}
 
resource storageAccountContainerResource 'Microsoft.Storage/storageAccounts/blobServices/containers@2019-06-01' = {
  name: '${storageAccountResource.name}/default/${storageContainerName}'
  dependsOn: [
    storageAccountResource
  ]
}
