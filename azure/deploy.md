# Deploy — SurveyJS form on Azure App Service → Cosmos DB

A small Node/Express app serves the SurveyJS form and writes submissions to Cosmos DB
(MongoDB API). Because it's a plain Node app (no container, no persistent disk), it runs
on the **free F1 App Service tier** and deploys cleanly.

```
app/
  server.js            # Express: serves the form + POST /api/submit -> Cosmos
  public/index.html    # SurveyJS page
  public/survey.js     # the form model (from docs/intake-fields.md)
  package.json
azure/
  deploy.sh            # one-shot: ensure Cosmos, deploy app, set settings
```

## One-shot deploy (Azure Cloud Shell)

```bash
az account set --subscription "f4c089ff-3083-41b3-a786-f98bd759ce03"
git clone https://github.com/PacifiCan/AIRegistry.git   # or: cd AIRegistry && git pull
cd AIRegistry/app
bash ../azure/deploy.sh
```

This will (creating everything from scratch — safe to run even after the resource group
was deleted):
1. Ensure the `AIRegistry` resource group exists.
2. Ensure the Cosmos DB for MongoDB account `airegistry-cosmos` (free tier) with database
   `airegistry` and collection `registry_entries` exists (reuses it if already there).
3. `az webapp up` — create the `airegistry-form` web app on the **F1 (free)** plan and
   build/upload the Node app.
4. Set the Cosmos connection string + DB/collection as application settings.

Open **https://airegistry-form.azurewebsites.net**, fill the form, submit — then check
the document in Azure Portal → Cosmos `airegistry-cosmos` → Data Explorer →
`registry_entries`.

## Notes

- **Free tier limits:** F1 has no Always On and a daily CPU quota, so the first request
  after idle is a slow cold start. Fine for a low-traffic intake form. For snappier
  response use `SKU=B1 bash ../azure/deploy.sh`.
- **Names** are overridable via env (`APP=`, `COSMOS_ACCT=`, `DB=`, `COLL=`). Defaults
  match the existing PacifiCan setup.
- **Local run:** `cd app && cp .env.example .env` (fill the Cosmos connection string),
  `npm install`, `npm start`, open http://localhost:8080.
- **Data shape:** the server reshapes the flat SurveyJS result into the nested document
  in [`../docs/intake-fields.md`](../docs/intake-fields.md) (`identification`, `overview`,
  `classification`, `aia_prescreen`, `pacifican`), so the future AIA agent can read it
  unchanged.

## Clean up the old Budibase resources

The earlier Budibase attempt left resources that can be deleted (keep the Cosmos account
— it holds the data):

```bash
az webapp delete -g AIRegistry -n airegistry || true
az appservice plan delete -g AIRegistry -n airegistry-plan --yes || true
az storage share-rm delete --storage-account airegistrystore -g AIRegistry -n airegistry-couch --yes || true
# optional, if the storage account isn't used for anything else:
az storage account delete -n airegistrystore -g AIRegistry --yes || true
```
