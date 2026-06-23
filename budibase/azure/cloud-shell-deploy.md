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

## Notes

- **Re-running the deployment** regenerates the auto `newGuid()` secrets, which can
  invalidate Budibase sessions/asset access. For a stable environment, deploy **once**;
  if you must redeploy, pass fixed values, e.g. add to the command:
  `-p jwtSecret=<fixed> minioAccessKey=<fixed> minioSecretKey=<fixed> couchdbPassword=<fixed>`.
- `cosmosConnectionString` is a secret — it appears in deployment outputs; don't share
  the output dump.
- To tear everything down: `az group delete -n "<your-rg-name>" --yes --no-wait`.
