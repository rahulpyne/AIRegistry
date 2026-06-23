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

## Cost / tier (prototyping vs production)

Defaults target a **basic, low-cost prototyping** setup for very low traffic:

| Component | Prototype default | Cost |
|---|---|---|
| Cosmos DB for MongoDB | **free tier** (1000 RU/s + 25 GB) | **$0** (one free-tier account per subscription) |
| App Service plan | **B1** Linux | **Free for 12 months** on a new Azure free account (750 B1 hrs/mo), then ~CAD $15/mo |
| Storage (Azure Files) | Standard_LRS, pay-per-use | a few cents/month at this size |

> There is **no truly $0 Azure option** for Budibase — the F1/Free App Service tier
> can't run the container (needs ~2 GB RAM; Free doesn't support Linux containers). B1
> is the cheapest that works. The only fully-free way to run Budibase is **locally with
> Docker** (below), optionally pointed at the free-tier Cosmos in Azure.
>
> For production, override `APP_SKU=P1V3` and `FREE_TIER=false` (script) or `appSku` /
> `cosmosFreeTier` (Bicep).

## 1. Fully-free local option (Docker — $0)

```bash
cp .env.example .env      # fill JWT_SECRET etc. with: openssl rand -base64 32
docker compose up -d
open http://localhost:80  # create the admin account
```

Build and iterate the app here at no cost. For storage you can either use Budibase's
built-in DB, or set `COSMOS_MONGO_CONNECTION_STRING` in `.env` to a free-tier Cosmos
account and connect it as the MongoDB datasource (step 3) — same as the Azure-hosted flow.

## 2. Provision Azure

**One-shot from the Azure Portal terminal (Cloud Shell):** follow
[`azure/cloud-shell-deploy.md`](azure/cloud-shell-deploy.md) — fill your exact names in
`azure/main.parameters.json`, then a single command builds and wires everything (secrets
auto-generated):

```bash
az group create -n <your-rg> -l canadacentral
az deployment group create -g <your-rg> -f azure/main.bicep -p @azure/main.parameters.json
```

**Or via the CLI script** (generates names + secrets, prints them once):

```bash
az login
az account set -s <subscription-id>
bash azure/provision.sh
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
