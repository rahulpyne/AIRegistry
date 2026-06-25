# Deploy Budibase on an Azure VM (reliable path)

Use this if App Service keeps 502-ing. The Budibase all-in-one image needs a real
filesystem for its bundled CouchDB + MinIO + Redis; on App Service the only RW mount is
Azure Files (SMB), where MinIO fails and CouchDB is slow. A VM with a normal disk runs
the whole stack as Budibase intends.

## One-shot (Azure Cloud Shell)

```bash
az account set --subscription "f4c089ff-3083-41b3-a786-f98bd759ce03"
git clone https://github.com/rahulpyne/AIRegistry.git   # or: cd AIRegistry && git pull
cd AIRegistry/budibase/azure
bash vm-deploy.sh
```

Deploys into the existing `AIRegistry` resource group: an Ubuntu 22.04 VM
(`Standard_B2s`, 2 vCPU / 4 GB) that installs Docker via cloud-init and runs
`budibase/budibase:3.22.0` on port 80, with data persisted on the VM disk at
`/opt/airegistry-data`. The script prints the public IP.

Open `http://<public-ip>` after ~3–5 minutes → Budibase setup screen.

## Connect Cosmos + build

Same as before — Cosmos is reached over its public endpoint:
1. Create the admin account.
2. **Data → + → MongoDB** → paste your Cosmos `cosmosConnectionString` → database `airegistry`.
3. Build the form per [`../app-build-guide.md`](../app-build-guide.md).

## Cost control

- `Standard_B2s` ≈ CAD $40/mo running 24/7; `Standard_B1ms` (1 vCPU / 2 GB) is ~half but
  tight. Override: `SIZE=Standard_B1ms bash vm-deploy.sh`.
- **Stop when idle** (you only pay for the disk while deallocated):
  `az vm deallocate -g AIRegistry -n airegistry-vm` / `az vm start -g AIRegistry -n airegistry-vm`.
- The public IP can change on start/stop. Make it static if you want a stable address:
  `az network public-ip update -g AIRegistry -n airegistry-vmPublicIP --allocation-method Static`.

## Notes

- HTTP only. For HTTPS/a custom domain, point a DNS name at the IP and put Caddy/Nginx
  with Let's Encrypt in front (or use Azure Front Door). Not needed for a prototype.
- Tear down: `az vm delete -g AIRegistry -n airegistry-vm --yes` (plus its disk/NIC/IP),
  or delete the whole RG if nothing else lives there.
- You can delete the failed App Service plan + web app to stop its billing:
  `az webapp delete -g AIRegistry -n airegistry` and
  `az appservice plan delete -g AIRegistry -n airegistry-plan --yes`.
