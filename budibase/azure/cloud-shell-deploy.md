# One-shot deploy from Azure Cloud Shell

For when you only have the **Azure Portal terminal (Cloud Shell)**. This builds every
resource and wires them together with a single `az deployment group create` pointed at
`main.bicep`. Secrets are generated automatically — you don't pass any.

> What Bicep does in one shot: Cosmos DB (Mongo API) + database + `registry_entries` &
> `aia_results` collections, Storage account + Azure Files share, App Service plan, and
> the Budibase Web App **with the `/data` mount and all env/secrets pre-wired**.
> The only manual step left is connecting Budibase to Cosmos inside the Budibase UI
> (one datasource form) — Bicep can't configure an app's internal datasource. The
> connection string you need is printed as a deployment output.

## What you'll provide (your exact names)

Edit `main.parameters.json` with these. Name rules:

| Parameter | Rule |
|---|---|
| `cosmosAccountName` | **globally unique**, 3–44 chars, lowercase letters/numbers/hyphens |
| `storageAccountName` | **globally unique**, 3–24 chars, lowercase letters/numbers only (no hyphens) |
| `webAppName` | **globally unique**, becomes `https://<name>.azurewebsites.net` |
| `planName` | unique within the resource group |
| `cosmosDbName` | keep `airegistry` (the form/queries expect it) |
| `location` | `canadacentral` (Protected B residency) |
| `appSku` | `B1` for prototyping; `P1V3` for production |
| `cosmosFreeTier` | `true` ($0); set `false` if you've already used the free tier on this subscription |

You also choose a **resource group name** and **subscription** at deploy time (below).

## Steps

**1. Open Cloud Shell** (Portal → top bar `>_` icon → **Bash**).

**2. Select your subscription** (use the exact subscription name/ID you'll share):
```bash
az account set --subscription "<your-subscription-name-or-id>"
az account show --query name -o tsv      # confirm
```

**3. Get the code** (Cloud Shell has git):
```bash
git clone https://github.com/rahulpyne/AIRegistry.git
cd AIRegistry/budibase/azure
```

**4. Fill in your names:**
```bash
code main.parameters.json     # Cloud Shell's editor; replace the REPLACE-* values, save (Ctrl+S)
```

**5. Create the resource group** (use your exact RG name):
```bash
az group create -n "<your-rg-name>" -l canadacentral
```

**6. Deploy everything in one shot:**
```bash
az deployment group create \
  -g "<your-rg-name>" \
  -f main.bicep \
  -p @main.parameters.json
```
Takes ~3–5 min. (Add `--what-if` first if you want a dry run.)

**7. Read the outputs** (URL + the Cosmos connection string to connect Budibase):
```bash
az deployment group show -g "<your-rg-name>" -n main \
  --query properties.outputs -o jsonc
```
You'll get `budibaseUrl` and `cosmosConnectionString`.

## Connect & build (Budibase UI)

1. Open `budibaseUrl` → create the admin account (first visit; the container may take a
   couple of minutes to warm up on first boot).
2. **Data → + → MongoDB** → paste `cosmosConnectionString` → database `airegistry` → save.
3. Build the form + confirmation screen per
   [`../app-build-guide.md`](../app-build-guide.md) (it has the queries, the `insertOne`
   mapping, and the screens), then **Publish**.
4. Verify: submit a test entry → Portal → Cosmos → Data Explorer → `registry_entries`.

## Troubleshooting: 502 Bad Gateway on first load

If the site returns **502** and `az webapp log tail` shows
`MinIO ... FATAL Unable to initialize backend: Unable to write to the backend`:

MinIO (Budibase's object store) **cannot run on an Azure Files SMB mount**. The Bicep
here already mounts the share at **`/data/couch`** (CouchDB only) and leaves MinIO on the
container's local disk, which avoids this. If you deployed an older revision that mounted
the whole `/data`, fix it in place:

```bash
RG=AIRegistry; APP=airegistry; SA=airegistrystore
KEY=$(az storage account keys list -n $SA -g $RG --query '[0].value' -o tsv)
az storage share-rm create --storage-account $SA -g $RG -n airegistry-couch --quota 50
az webapp config storage-account delete -g $RG -n $APP --custom-id airegistrydata
az webapp config storage-account add -g $RG -n $APP \
  --custom-id couch --storage-type AzureFiles \
  --account-name $SA --share-name airegistry-couch \
  --access-key "$KEY" --mount-path /data/couch
az webapp restart -g $RG -n $APP
```

Trade-off: MinIO is ephemeral, so after an App Service restart you may need to **re-publish**
the app (one click). The app *design* is safe in CouchDB on the persisted share. The intake
form has no file-upload fields, so no user data lives in MinIO. For full durability of
everything, run Budibase on a small VM with an ext4 data disk instead of App Service.

## Troubleshooting: container start timeout / still 502 after the MinIO fix

If logs show `Container did not start within expected time limit of 230s ... terminated
during site startup`: the Budibase all-in-one stack boots slowly on one CPU. The Bicep
sets `WEBSITES_CONTAINER_START_TIME_LIMIT=1800`; if you deployed an older revision, add it:

```bash
az webapp config appsettings set -g AIRegistry -n airegistry \
  --settings WEBSITES_CONTAINER_START_TIME_LIMIT=1800
```

Then allow 5–10 min on B1. If it still won't serve, B1 (1.75 GB) is underpowered for this
stack — scale up (Budibase's own minimum is ~2 GB):

```bash
az appservice plan update -g AIRegistry -n airegistry-plan --sku B2
```

## Troubleshooting: 502 with LiteLLM Postgres errors (`latest` image)

If logs show `Timed out waiting for internal LiteLLM postgres to start` /
`Can't reach database server at 127.0.0.1:5432` / `relation "public.LiteLLM_Config" does
not exist`: the `budibase/budibase:latest` image bundles a LiteLLM AI service whose
Postgres fails to start on App Service, blocking the main app (Budibase issue #18090).
The Bicep/script here pin to **`budibase/budibase:3.22.0`** (pre-LiteLLM). To fix a running
app deployed on `latest`:

```bash
az webapp config container set -g AIRegistry -n airegistry \
  --container-image-name budibase/budibase:3.22.0
# if CouchDB complains about newer-version data (only if nothing built yet), reset the share:
az webapp stop -g AIRegistry -n airegistry
az storage share-rm delete --storage-account airegistrystore -g AIRegistry -n airegistry-couch --yes
az storage share-rm create --storage-account airegistrystore -g AIRegistry -n airegistry-couch --quota 50
az webapp start -g AIRegistry -n airegistry
```

To move to a newer Budibase later, test a tag locally with `docker compose` first; only
bump past 3.25 once the upstream LiteLLM-on-self-host startup bug is resolved.

## Notes

- **Re-running the deployment** regenerates the auto `newGuid()` secrets, which can
  invalidate Budibase sessions/asset access. For a stable environment, deploy **once**;
  if you must redeploy, pass fixed values, e.g. add to the command:
  `-p jwtSecret=<fixed> minioAccessKey=<fixed> minioSecretKey=<fixed> couchdbPassword=<fixed>`.
- `cosmosConnectionString` is a secret — it appears in deployment outputs; don't share
  the output dump.
- To tear everything down: `az group delete -n "<your-rg-name>" --yes --no-wait`.
