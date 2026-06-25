# Auto-deployment (CI/CD) — GitHub → Azure App Service

Pushes to `main` in **PacifiCan/AIRegistry** automatically deploy the `app/` folder to the
**airegistry-form** web app, via the GitHub Actions workflow
[`.github/workflows/azure-deploy.yml`](../.github/workflows/azure-deploy.yml).

Target App Service:
- Subscription `f4c089ff-3083-41b3-a786-f98bd759ce03`
- Resource group `airegistry` · Web app `airegistry-form`

## One-time setup

### 1. Get the publish profile (Cloud Shell or local `az`)

```bash
az webapp deployment list-publishing-profiles \
  -g airegistry -n airegistry-form --xml
```

Copy the entire XML output.

> If this errors with *"basic authentication is disabled"*, enable SCM basic auth
> (needed for publish-profile deploys), then re-run the command:
> ```bash
> az resource update -g airegistry --namespace Microsoft.Web \
>   --resource-type basicPublishingCredentialsPolicies --name scm \
>   --parent sites/airegistry-form --set properties.allow=true
> ```

### 2. Add it as a GitHub secret

In **github.com/PacifiCan/AIRegistry → Settings → Secrets and variables → Actions →
New repository secret**:
- Name: `AZURE_WEBAPP_PUBLISH_PROFILE`
- Value: the XML from step 1

### 3. Tell App Service not to rebuild on deploy

The workflow already runs `npm ci`, so the deployed package includes `node_modules` —
turn off the server-side build to avoid a redundant rebuild:

```bash
az webapp config appsettings set -g airegistry -n airegistry-form \
  --settings SCM_DO_BUILD_DURING_DEPLOYMENT=false
```

(The Cosmos connection-string app settings stay as they are — deployments don't change
application settings.)

## Use it

- Push any change under `app/` to `main` → the **Actions** tab shows the run → it deploys
  to `airegistry-form`.
- You can also trigger manually: **Actions → Deploy to Azure App Service → Run workflow**.
- After it succeeds, hard-refresh https://airegistry-form.azurewebsites.net.

## Notes & alternatives

- **First run** will fail until the `AZURE_WEBAPP_PUBLISH_PROFILE` secret exists. Add it,
  then re-run the job (or push again).
- **Portal alternative:** App Service → **Deployment Center** → Source: GitHub → authorize
  → select `PacifiCan/AIRegistry` / `main`. It wires auth automatically but generates its
  own workflow assuming the repo root — if you use it, set the build/start to the `app/`
  folder or keep this workflow instead (don't run both).
- **OIDC alternative (no publish profile):** if the org disables SCM basic auth, switch to
  federated credentials — create an Entra app registration with a federated credential for
  this repo, give it the *Website Contributor* role on `airegistry-form`, and replace the
  publish-profile step with `azure/login@v2` (client-id/tenant-id/subscription-id secrets)
  + `azure/webapps-deploy@v3` without a publish profile. Needs permission to create the app
  registration.
