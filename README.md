# AI Registry

A lightweight, organization-wide app for PacifiCan to **inventory AI ideas**, **see emerging
patterns** across them, and **track each idea through the AI Operating Lifecycle**. Built to mirror
the `pacifican-bsp` stack (Flask + server-rendered templates + vanilla JS, gunicorn on Azure App
Service) so it migrates to Azure with no rework.

Grounded in two source documents: `AI Registry Form Template` (Section 1 fields) and the
`Product Management Plan for AI Operating Framework` (Section 3 phases, artifact map, and AIA/PIA gates).

## Three sections

1. **Submit Idea** (`/form`) — the AI Registry Form. Captures the idea as a JSON document and stores it.
2. **Idea Graph** (`/graph`) — an Obsidian-style semantic graph. Ideas cluster into categories →
   sub-categories → individual ideas; larger nodes are recurring themes. Recomputed on each load so
   it adapts as new ideas arrive. For executives spotting emerging patterns.
3. **Lifecycle** (`/lifecycle/<id>`) — the 5 AI Operating Lifecycle phases as color-coded blocks for a
   given idea, with per-phase artifact/template links, Business & IT approval toggles, and document
   uploads showing status `UPLOADED → IN-REVIEW → APPROVED`.

## Run locally (zero config)

```bash
pip install -r requirements.txt
python app.py            # http://localhost:8000
```

With no Supabase keys set, the app uses **LocalJSONStore** (`./data/*.json`) and auto-seeds ~16 dummy
PacifiCan ideas so the graph is populated immediately. Uploaded files go to `./uploads`.

## Use Supabase

1. Create a dedicated Supabase project.
2. Run [`supabase_schema.sql`](supabase_schema.sql) in the SQL editor (creates `registry_entries`,
   `documents`, `approvals`).
3. Storage → New bucket → `airegistry-documents`.
4. Copy `.env.example` → `.env` and set:
   ```
   SUPABASE_URL=https://<project>.supabase.co
   SUPABASE_KEY=<service_role secret>   # server-side; bypasses RLS
   ```
5. Restart. The app now reads/writes Supabase (selected automatically when both vars are present).

## Architecture

| File | Responsibility |
|------|----------------|
| `app.py` | Flask routes (pages + JSON APIs) |
| `storage.py` | Storage abstraction — `SupabaseStore`, `LocalJSONStore`, `CosmosStore` (stub) |
| `graph_builder.py` | TF-IDF + agglomerative clustering → 3-level graph JSON |
| `lifecycle.py` | Lifecycle model: phases, artifact map, AIA/PIA gates (from the PMP doc) |
| `seed_data.py` | ~16 dummy PacifiCan ideas across 5 clusters |

All three backends in `storage.py` implement the same 8 methods, so swapping stores is one class.

## Azure migration (later)

- **Storage:** implement `CosmosStore` (containers keyed by `entryId`) — same pattern as
  `pacifican-bsp/cosmos_client.py`. Uploaded files → Azure Blob Storage.
- **Graph / semantics:** replace `graph_builder._vectorize` (TF-IDF) with **Azure OpenAI**
  `text-embedding-3-small` embeddings and store vectors in **Azure AI Search**; cluster on the
  embeddings and cache results. The graph-assembly code is unchanged.
- **Hosting:** `startup.sh` already runs gunicorn for Azure App Service. Set the same env vars as
  App Service application settings.

## API reference

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/registry` | Create a registry entry (JSON body) |
| GET | `/api/graph` | Cytoscape graph elements for current entries |
| POST | `/api/entries/<id>/documents` | Upload a document (multipart: file, phase, artifact) |
| PATCH | `/api/documents/<doc_id>` | Set status `UPLOADED`/`IN-REVIEW`/`APPROVED` |
| PATCH | `/api/entries/<id>/approvals` | Set `BUSINESS`/`IT` approval for a phase |
