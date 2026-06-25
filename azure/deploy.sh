#!/usr/bin/env bash
# Deploy the SurveyJS AI Registry form (Node/Express) to Azure App Service and wire it
# to Cosmos DB (MongoDB API). Run from the repo's app/ directory in Azure Cloud Shell:
#
#   cd ~/AIRegistry/app && bash ../azure/deploy.sh
#
# A plain Node web app is lightweight, so it runs on the FREE (F1) App Service tier —
# no container, no Azure Files, none of the heavy-image problems.

set -euo pipefail

RG="${RG:-AIRegistry}"
LOCATION="${LOCATION:-canadacentral}"
APP="${APP:-airegistry-form}"
PLAN="${PLAN:-airegistry-form-plan}"
SKU="${SKU:-F1}"                       # F1 = Free. Use B1 if you want Always On.
COSMOS_ACCT="${COSMOS_ACCT:-airegistry-cosmos}"
DB="${DB:-airegistry}"
COLL="${COLL:-registry_entries}"
FREE_TIER="${FREE_TIER:-true}"

echo "==> Ensure resource group '$RG' ($LOCATION)"
az group create -n "$RG" -l "$LOCATION" -o none

echo "==> Ensure Cosmos DB for MongoDB account '$COSMOS_ACCT' exists"
if ! az cosmosdb show -n "$COSMOS_ACCT" -g "$RG" -o none 2>/dev/null; then
  FREE_FLAG=""; [ "$FREE_TIER" = "true" ] && FREE_FLAG="--enable-free-tier true"
  az cosmosdb create -n "$COSMOS_ACCT" -g "$RG" --kind MongoDB --server-version 4.2 \
    --default-consistency-level Session $FREE_FLAG \
    --locations regionName="$LOCATION" failoverPriority=0 isZoneRedundant=false -o none
fi
az cosmosdb mongodb database create -a "$COSMOS_ACCT" -g "$RG" -n "$DB" -o none 2>/dev/null || true
az cosmosdb mongodb collection create -a "$COSMOS_ACCT" -g "$RG" -d "$DB" -n "$COLL" --shard _id -o none 2>/dev/null || true

echo "==> Fetch Cosmos connection string"
COSMOS_CONN="$(az cosmosdb keys list -n "$COSMOS_ACCT" -g "$RG" --type connection-strings \
  --query 'connectionStrings[0].connectionString' -o tsv)"

# Pick a supported Linux Node runtime (versions available vary by CLI/region).
RUNTIME="${RUNTIME:-}"
if [ -z "$RUNTIME" ]; then
  RUNTIME="$(az webapp list-runtimes --os linux --query "[?runtime=='Node'].config | [0]" -o tsv 2>/dev/null | tr '|' ':')"
  [ -z "$RUNTIME" ] && RUNTIME="NODE:22-lts"
fi
echo "==> Deploy Node app to App Service ($SKU) using runtime '$RUNTIME'"
az webapp up --name "$APP" --resource-group "$RG" --location "$LOCATION" \
  --plan "$PLAN" --sku "$SKU" --os-type Linux --runtime "$RUNTIME"

echo "==> Set application settings (Cosmos + build)"
az webapp config appsettings set -g "$RG" -n "$APP" --settings \
  COSMOS_MONGO_CONNECTION_STRING="$COSMOS_CONN" COSMOS_DB_NAME="$DB" COSMOS_COLLECTION="$COLL" \
  SCM_DO_BUILD_DURING_DEPLOYMENT=true -o none

echo
echo "============================================================"
echo " Deployed: https://$APP.azurewebsites.net"
echo " Data lands in Cosmos: $COSMOS_ACCT / $DB / $COLL"
echo "============================================================"
