#!/usr/bin/env bash
# Deploy Budibase on a small Azure VM with Docker — the reliable path.
#
# Why a VM: the Budibase all-in-one image bundles CouchDB + MinIO + Redis, which need a
# real (ext4) filesystem. On App Service the only RW mount is Azure Files (SMB), where
# MinIO fails ("no online disks"/"Unable to write to the backend") and CouchDB is slow.
# On a VM with a normal disk it all just works.
#
# Run in Azure Cloud Shell (Bash). Deploys into an EXISTING resource group.
# Browse http://<public-ip> when done (HTTP only; add TLS/DNS later if needed).

set -euo pipefail

RG="${RG:-AIRegistry}"
LOCATION="${LOCATION:-canadacentral}"
VM="${VM:-airegistry-vm}"
SIZE="${SIZE:-Standard_B2s}"          # 2 vCPU / 4 GB. B1ms (1/2GB) is cheaper but tight.
IMAGE_TAG="${IMAGE_TAG:-3.22.0}"      # pinned pre-LiteLLM (see #18090)
ADMIN="${ADMIN:-azureuser}"

echo "==> cloud-init (install Docker + run Budibase $IMAGE_TAG)"
cat > /tmp/airegistry-cloud-init.yaml <<EOF
#cloud-config
package_update: true
packages:
  - docker.io
runcmd:
  - systemctl enable --now docker
  - mkdir -p /opt/airegistry-data
  - docker run -d --name airegistry --restart unless-stopped -p 80:80 -v /opt/airegistry-data:/data budibase/budibase:${IMAGE_TAG}
EOF

echo "==> Create VM $VM ($SIZE) in $RG"
az vm create -g "$RG" -n "$VM" --image Ubuntu2204 --size "$SIZE" \
  --admin-username "$ADMIN" --generate-ssh-keys \
  --custom-data /tmp/airegistry-cloud-init.yaml --public-ip-sku Standard -o none

echo "==> Open port 80"
az vm open-port -g "$RG" -n "$VM" --port 80 -o none

IP="$(az vm show -g "$RG" -n "$VM" -d --query publicIps -o tsv)"
cat <<EOF

============================================================
 VM created. Docker is installing Budibase in the background.
 Give it ~3-5 min, then open:   http://$IP
============================================================
 SSH if needed:        ssh $ADMIN@$IP
 Watch boot:           ssh $ADMIN@$IP 'sudo docker logs -f airegistry'
 Stop to save cost:    az vm deallocate -g $RG -n $VM
 Start again:          az vm start -g $RG -n $VM   (public IP may change unless Static)
============================================================
 Next: open the URL, create the admin account, then add a
 MongoDB datasource using your Cosmos connection string
 (Cosmos is reached over its public endpoint, same as before).
EOF
