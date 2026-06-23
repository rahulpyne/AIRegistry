// AI Registry infra — Cosmos DB (Mongo API) + Storage (Azure Files) + App Service
// for Containers running self-hosted Budibase.
//
// Deploy:
//   az group create -n rg-airegistry -l canadacentral
//   az deployment group create -g rg-airegistry -f main.bicep \
//     -p jwtSecret=... internalApiKey=... minioAccessKey=... minioSecretKey=... \
//        redisPassword=... couchdbPassword=...
// (generate each secret with: openssl rand -base64 32)

@description('Azure region. Canada Central for Protected B data residency.')
param location string = 'canadacentral'

@description('Short name prefix for resources.')
param prefix string = 'airegistry'

@description('Cosmos Mongo database name.')
param cosmosDbName string = 'airegistry'

// --- secrets (no defaults; pass at deploy time) ---
@secure()
param jwtSecret string
@secure()
param internalApiKey string
@secure()
param minioAccessKey string
@secure()
param minioSecretKey string
@secure()
param redisPassword string
@secure()
param couchdbPassword string
param couchdbUser string = 'admin'

var suffix = uniqueString(resourceGroup().id)
var cosmosName = '${prefix}-cosmos-${suffix}'
var storageName = toLower('${prefix}st${substring(suffix, 0, 8)}')
var planName = '${prefix}-plan'
var webAppName = '${prefix}-budibase-${suffix}'
var fileShareName = 'budibase-data'

resource cosmos 'Microsoft.DocumentDB/databaseAccounts@2024-05-15' = {
  name: cosmosName
  location: location
  kind: 'MongoDB'
  properties: {
    apiProperties: { serverVersion: '4.2' }
    databaseAccountOfferType: 'Standard'
    consistencyPolicy: { defaultConsistencyLevel: 'Session' }
    locations: [ { locationName: location, failoverPriority: 0, isZoneRedundant: false } ]
  }
}

resource cosmosDb 'Microsoft.DocumentDB/databaseAccounts/mongodbDatabases@2024-05-15' = {
  parent: cosmos
  name: cosmosDbName
  properties: { resource: { id: cosmosDbName } }
}

resource entries 'Microsoft.DocumentDB/databaseAccounts/mongodbDatabases/collections@2024-05-15' = {
  parent: cosmosDb
  name: 'registry_entries'
  properties: { resource: { id: 'registry_entries', shardKey: { _id: 'Hash' } } }
}

// reserved for the future AIA agent (created now, unused)
resource aiaResults 'Microsoft.DocumentDB/databaseAccounts/mongodbDatabases/collections@2024-05-15' = {
  parent: cosmosDb
  name: 'aia_results'
  properties: { resource: { id: 'aia_results', shardKey: { _id: 'Hash' } } }
}

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageName
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
}

resource fileShare 'Microsoft.Storage/storageAccounts/fileServices/shares@2023-05-01' = {
  name: '${storageName}/default/${fileShareName}'
  properties: { shareQuota: 50 }
  dependsOn: [ storage ]
}

resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: planName
  location: location
  sku: { name: 'P1v3', tier: 'PremiumV3' }
  kind: 'linux'
  properties: { reserved: true }
}

resource webApp 'Microsoft.Web/sites@2023-12-01' = {
  name: webAppName
  location: location
  properties: {
    serverFarmId: plan.id
    siteConfig: {
      linuxFxVersion: 'DOCKER|budibase/budibase:latest'
      appSettings: [
        { name: 'WEBSITES_PORT', value: '80' }
        { name: 'WEBSITES_ENABLE_APP_SERVICE_STORAGE', value: 'true' }
        { name: 'MAIN_PORT', value: '80' }
        { name: 'APP_PORT', value: '4002' }
        { name: 'WORKER_PORT', value: '4003' }
        { name: 'JWT_SECRET', value: jwtSecret }
        { name: 'INTERNAL_API_KEY', value: internalApiKey }
        { name: 'MINIO_ACCESS_KEY', value: minioAccessKey }
        { name: 'MINIO_SECRET_KEY', value: minioSecretKey }
        { name: 'REDIS_PASSWORD', value: redisPassword }
        { name: 'COUCHDB_USER', value: couchdbUser }
        { name: 'COUCHDB_PASSWORD', value: couchdbPassword }
      ]
      azureStorageAccounts: {
        budibasedata: {
          type: 'AzureFiles'
          accountName: storageName
          shareName: fileShareName
          mountPath: '/data'
          accessKey: storage.listKeys().keys[0].value
        }
      }
    }
  }
}

output budibaseUrl string = 'https://${webApp.properties.defaultHostName}'
output cosmosAccountName string = cosmos.name
output cosmosDbName string = cosmosDbName
