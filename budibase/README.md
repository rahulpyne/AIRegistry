# AI Registry — Budibase build & deployment

Self-hosted **Budibase** app on **Azure App Service for Containers**, storing AI
Registry submissions as JSON in **Azure Cosmos DB for MongoDB**.

- Field spec the form is built from: [`../docs/intake-fields.md`](../docs/intake-fields.md)
- Source of truth for fields: `AI_Registry_Intake_Form_PacifiCan.docx`

## What's here

```
budibase/
  docker-compose.yml   # single-image budibase/budibase (local test + the container Azure runs)
  .env.example         # secrets template (copy -> .env, never commit real values)
  azure/
    provision.sh       # one-shot az CLI: Cosmos + Azure Files + App Service + Budibase
    main.bicep         # same infra as IaC
  app-export/          # the exported Budibase app (.tar.gz) — committed after the app is built
```

## 1. (Optional) run Budibase locally first

```bash
cp .env.example .env      # fill JWT_SECRET etc. with: openssl rand -base64 32
docker compose up -d
open http://localhost:80  # create the admin account
```

This is handy to build/iterate the app before pushing to Azure.

## 2. Provision Azure

```bash
az login
az account set -s <subscription-id>
# Option A — script:
bash azure/provision.sh
# Option B — Bicep:
az group create -n rg-airegistry -l canadacentral
az deployment group create -g rg-airegistry -f azure/main.bicep \
  -p jwtSecret=$(openssl rand -base64 32) internalApiKey=$(openssl rand -base64 32) \
     minioAccessKey=$(openssl rand -base64 32) minioSecretKey=$(openssl rand -base64 32) \
     redisPassword=$(openssl rand -base64 32) couchdbPassword=$(openssl rand -base64 32)
```

Both create: Cosmos DB for MongoDB (`airegistry` db with `registry_entries` +
reserved `aia_results` collections), a Storage account + Azure Files share mounted at
**`/data`** (so CouchDB/MinIO persist across restarts — the key self-host requirement),
and the App Service web app running `budibase/budibase:latest`. The script prints the
Budibase URL and the Cosmos connection string at the end.

> **Persistence gotcha:** without the `/data` Azure Files mount, an App Service restart
> wipes the Budibase app. The mount is configured by both provisioning paths above;
> verify with `az webapp config storage-account list -g rg-airegistry -n <webapp>`.

## 3. Build the app

Open the Budibase URL, create the admin account, then follow
**[`app-build-guide.md`](app-build-guide.md)** to add the Cosmos MongoDB datasource and
build the intake form + confirmation screen.

## 4. Version-control the app

Budibase → app → **Export** (include or exclude rows as needed) → save the `.tar.gz`
into `app-export/` and commit. To restore on a fresh instance, **Import** that file.

## Future (deferred)

The agentic AIA step (auto-fill GC AIA, compute Impact Level I–IV, generate the report
/ "TDS certificate") is **not built**. The form already captures the full AIA pre-screen
into `aia_prescreen`, and `aia_results` is reserved for it. See the mapping table at the
end of `../docs/intake-fields.md`.
