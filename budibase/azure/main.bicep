// AI Registry infra — Cosmos DB (Mongo API) + Storage (Azure Files) + App Service
// for Containers running self-hosted Budibase.
//
// One-shot deploy (Azure Cloud Shell):
//   az group create -n <your-rg> -l canadacentral
//   az deployment group create -g <your-rg> -f main.bicep -p @main.parameters.json
//
// Secrets default to newGuid() (generated at deploy time) so no secret params are
// required. Resource names default to a unique-suffixed value but can be set in
// main.parameters.json to your exact names. See cloud-shell-deploy.md.

@description('Azure region. Canada Central for Protected B data residency.')
param location string = 'canadacentral'

@description('Short name prefix used for any name not set explicitly below.')
param prefix string = 'airegistry'

// --- exact resource names (override in main.parameters.json; must be globally unique
//     where noted) ---
@description('Cosmos DB account name (globally unique, 3-44 lowercase alphanumeric/hyphen).')
param cosmosAccountName string = '${prefix}-cosmos-${uniqueString(resourceGroup().id)}'

@description('Cosmos Mongo database name.')
param cosmosDbName string = 'airegistry'

@description('Storage account name (globally unique, 3-24 lowercase alphanumeric).')
param storageAccountName string = toLower('${prefix}st${substring(uniqueString(resourceGroup().id), 0, 8)}')

@description('App Service plan name.')
param planName string = '${prefix}-plan'

@description('Web app name (globally unique; becomes <name>.azurewebsites.net).')
param webAppName string = '${prefix}-${uniqueString(resourceGroup().id)}'

@description('App Service plan SKU. B1 = basic/cheap prototyping; P1v3 for production.')
param appSku string = 'B1'

@description('Enable Cosmos free tier ($0, one per subscription). Set false if already used.')
param cosmosFreeTier bool = true

// --- secrets (auto-generated; override only if you need fixed values) ---
@secure()
param jwtSecret string = newGuid()
@secure()
param internalApiKey string = newGuid()
@secure()
param minioAccessKey string = newGuid()
@secure()
param minioSecretKey string = newGuid()
@secure()
param redisPassword string = newGuid()
@secure()
param couchdbPassword string = newGuid()
param couchdbUser string = 'admin'

// Only CouchDB (the app definitions) is persisted. MinIO (object store) CANNOT run on
// an Azure Files SMB mount — it fails with "Unable to write to the backend" — so it runs
// on the container's local disk. Our intake form has no file uploads, so ephemeral MinIO
// is acceptable; note a published app may need re-publishing after an App Service restart.
var fileShareName = 'airegistry-couch'

resource cosmos 'Microsoft.DocumentDB/databaseAccounts@2024-05-15' = {
  name: cosmosAccountName
  location: location
  kind: 'MongoDB'
  properties: {
    apiProperties: { serverVersion: '4.2' }
    databaseAccountOfferType: 'Standard'
    enableFreeTier: cosmosFreeTier
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
  name: storageAccountName
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
}

resource fileShare 'Microsoft.Storage/storageAccounts/fileServices/shares@2023-05-01' = {
  name: '${storageAccountName}/default/${fileShareName}'
  properties: { shareQuota: 50 }
  dependsOn: [ storage ]
}

resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: planName
  location: location
  sku: { name: appSku }
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
      alwaysOn: true
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
        airegistrydata: {
          type: 'AzureFiles'
          accountName: storageAccountName
          shareName: fileShareName
          mountPath: '/data/couch'
          accessKey: storage.listKeys().keys[0].value
        }
      }
    }
  }
}

output budibaseUrl string = 'https://${webApp.properties.defaultHostName}'
output cosmosAccountName string = cosmos.name
output cosmosDbName string = cosmosDbName
@description('Paste this into the Budibase MongoDB datasource. Treat as a secret.')
output cosmosConnectionString string = cosmos.listConnectionStrings().connectionStrings[0].connectionString
