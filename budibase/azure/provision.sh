#!/usr/bin/env bash
# Provision AI Registry on Azure: Cosmos DB (Mongo API) + Azure Files + App Service
# for Containers running self-hosted Budibase.
#
# Prereqs: `az login` done, correct subscription selected (`az account set -s <sub>`).
# Region defaults to Canada Central for data residency (Protected B).
#
# Secrets are generated locally and printed once at the end — store them in a vault.
# Nothing here embeds long-lived secrets in source.

set -euo pipefail

# ---- config (override via env before running) ----
LOCATION="${LOCATION:-canadacentral}"
RG="${RG:-rg-airegistry}"
PREFIX="${PREFIX:-airegistry}"
COSMOS_ACCT="${COSMOS_ACCT:-${PREFIX}-cosmos-$RANDOM}"
COSMOS_DB="${COSMOS_DB:-airegistry}"
STORAGE_ACCT="${STORAGE_ACCT:-${PREFIX}store$RANDOM}"   # 3-24 lowercase alnum
FILE_SHARE="${FILE_SHARE:-budibase-data}"
PLAN="${PLAN:-${PREFIX}-plan}"
WEBAPP="${WEBAPP:-${PREFIX}-budibase-$RANDOM}"
IMAGE="budibase/budibase:latest"

# ---- secrets (generated) ----
gen() { openssl rand -base64 32 | tr -d '\n'; }
JWT_SECRET="$(gen)"; MINIO_ACCESS_KEY="$(gen)"; MINIO_SECRET_KEY="$(gen)"
REDIS_PASSWORD="$(gen)"; INTERNAL_API_KEY="$(gen)"; COUCHDB_PASSWORD="$(gen)"
COUCHDB_USER="admin"

echo "==> Resource group $RG ($LOCATION)"
az group create -n "$RG" -l "$LOCATION" -o none

echo "==> Cosmos DB for MongoDB account $COSMOS_ACCT"
az cosmosdb create -n "$COSMOS_ACCT" -g "$RG" --kind MongoDB \
  --server-version 4.2 --default-consistency-level Session \
  --locations regionName="$LOCATION" failoverPriority=0 isZoneRedundant=false -o none

echo "==> Cosmos database + collections"
az cosmosdb mongodb database create -a "$COSMOS_ACCT" -g "$RG" -n "$COSMOS_DB" -o none
az cosmosdb mongodb collection create -a "$COSMOS_ACCT" -g "$RG" -d "$COSMOS_DB" \
  -n registry_entries --shard _id -o none
# reserved for the future AIA agent (created now, unused)
az cosmosdb mongodb collection create -a "$COSMOS_ACCT" -g "$RG" -d "$COSMOS_DB" \
  -n aia_results --shard _id -o none

echo "==> Storage account + Azure Files share (Budibase /data persistence)"
az storage account create -n "$STORAGE_ACCT" -g "$RG" -l "$LOCATION" \
  --sku Standard_LRS --kind StorageV2 -o none
STORAGE_KEY="$(az storage account keys list -n "$STORAGE_ACCT" -g "$RG" --query '[0].value' -o tsv)"
az storage share-rm create --storage-account "$STORAGE_ACCT" -g "$RG" \
  -n "$FILE_SHARE" --quota 50 -o none

echo "==> App Service plan (Linux) + web app for container"
az appservice plan create -n "$PLAN" -g "$RG" --is-linux --sku P1V3 -o none
az webapp create -n "$WEBAPP" -g "$RG" -p "$PLAN" --container-image-name "$IMAGE" -o none

echo "==> Mount Azure Files at /data and set port"
az webapp config storage-account add -g "$RG" -n "$WEBAPP" \
  --custom-id budibasedata --storage-type AzureFiles \
  --account-name "$STORAGE_ACCT" --share-name "$FILE_SHARE" \
  --access-key "$STORAGE_KEY" --mount-path /data -o none
az webapp config appsettings set -g "$RG" -n "$WEBAPP" --settings \
  WEBSITES_PORT=80 WEBSITES_ENABLE_APP_SERVICE_STORAGE=true \
  JWT_SECRET="$JWT_SECRET" MINIO_ACCESS_KEY="$MINIO_ACCESS_KEY" \
  MINIO_SECRET_KEY="$MINIO_SECRET_KEY" REDIS_PASSWORD="$REDIS_PASSWORD" \
  INTERNAL_API_KEY="$INTERNAL_API_KEY" COUCHDB_USER="$COUCHDB_USER" \
  COUCHDB_PASSWORD="$COUCHDB_PASSWORD" MAIN_PORT=80 APP_PORT=4002 WORKER_PORT=4003 \
  -o none

COSMOS_CONN="$(az cosmosdb keys list -n "$COSMOS_ACCT" -g "$RG" \
  --type connection-strings --query 'connectionStrings[0].connectionString' -o tsv)"

cat <<EOF

============================================================
 PROVISIONED. Store these secrets in a vault — shown once.
============================================================
 Budibase URL          : https://$WEBAPP.azurewebsites.net
 JWT_SECRET            : $JWT_SECRET
 INTERNAL_API_KEY      : $INTERNAL_API_KEY
 MINIO_ACCESS_KEY      : $MINIO_ACCESS_KEY
 MINIO_SECRET_KEY      : $MINIO_SECRET_KEY
 REDIS_PASSWORD        : $REDIS_PASSWORD
 COUCHDB_USER/PASSWORD : $COUCHDB_USER / $COUCHDB_PASSWORD

 Cosmos DB name        : $COSMOS_DB  (collections: registry_entries, aia_results)
 Cosmos Mongo conn str : $COSMOS_CONN
============================================================
 Next: open the Budibase URL, create the admin account, then add a
 MongoDB datasource using the Cosmos connection string above.
 See ../README.md and ../../docs/intake-fields.md.
EOF
