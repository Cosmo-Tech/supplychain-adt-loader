
@description('Specify the name of the function application')
param functionAppName string = 'schadtldr${uniqueString(resourceGroup().id)}'

@description('Location for the resources to be created (Function App, App Service plan and Storage Account)')
param location string = resourceGroup().location

@description('Specify the name of the storage account')
param storageAccountName string = 'schadtldr${uniqueString(resourceGroup().id)}'
// prefix 11 car + 13 unique string = 24 car max for storage name

@description('Specify the URL of the package')
param packageAddress string = 'https://github.com/Cosmo-Tech/supplychain-adt-loader/releases/download/2.3.3/artifact.zip'

@description('Specify the input container name')
param inputStorageContainer string = 'dataset-input'

@description('Specify the connection string of the ouput container (DT Injector)')
param outputStorageConnection string = ''

@description('Specify the output queue name (DT Injector)')
param outputStorageQueueName string = 'json-queue'


var hostingPlanName = functionAppName


resource storageAccount 'Microsoft.Storage/storageAccounts@2022-05-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    supportsHttpsTrafficOnly: true
    accessTier: 'Hot'
  }
}

resource storageAccountContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2022-05-01' = {
  name: '${storageAccount.name}/default/${inputStorageContainer}'
  properties: {}
}

resource hostingPlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: hostingPlanName
  kind: 'app,linux'
  location: location
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
  }
  properties: {
    reserved: true
  }
}

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: functionAppName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
  }
}

resource functionApp 'Microsoft.Web/sites@2022-03-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: hostingPlan.id
    reserved: true
    siteConfig: {
      linuxFxVersion: 'python|3.9'
      appSettings: [
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'WEBSITE_CONTENTSHARE'
          value: toLower(functionAppName)
        }        
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: applicationInsights.properties.InstrumentationKey
        }
        {
          name: 'WEBSITE_RUN_FROM_PACKAGE'
          value: packageAddress
        }
        {
          name: 'INPUT_STORAGE_CONNECTION'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'INPUT_STORAGE_CONTAINER'
          value: inputStorageContainer
        }
        {
          name: 'OUTPUT_STORAGE_CONNECTION'
          value: outputStorageConnection
        }
        {
          name: 'OUTPUT_STORAGE_QUEUE_NAME'
          value: outputStorageQueueName
        }
      ]
      ftpsState: 'FtpsOnly'
      minTlsVersion: '1.2'
    }
    httpsOnly: true
  }  
}
