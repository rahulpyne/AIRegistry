# AI Registry (PacifiCan)

A low-code **Budibase** intake application, self-hosted on **Azure App Service for
Containers**, that captures AI Registry submissions — all PacifiCan registry fields
**plus the AIA pre-screen** — and stores each as a JSON document in **Azure Cosmos DB
for MongoDB**. After submitting, the user sees a confirmation summary of everything
received.

Source of truth for fields: `AI_Registry_Intake_Form_PacifiCan.docx`.

## Layout

```
budibase/                 # the current implementation
  README.md               # build & Azure deployment guide
  app-build-guide.md      # step-by-step Budibase app build (datasource, queries, screens)
  docker-compose.yml      # self-hosted Budibase (single image)
  .env.example            # secrets template
  azure/                  # provision.sh (az CLI) + main.bicep
  app-export/             # exported Budibase app (.tar.gz)
docs/
  intake-fields.md        # full field spec + Cosmos doc shape + future-AIA mapping
archive/                  # retired implementations (not deployed)
  legacy-flask-app/       # original Flask app (form + idea graph + lifecycle board)
  legacy-graph-spa/       # standalone Cytoscape/Design-Component idea graph
```

## Quick start

1. Build the field understanding: [`docs/intake-fields.md`](docs/intake-fields.md).
2. Provision Azure + Budibase: [`budibase/README.md`](budibase/README.md).
3. Build the form: [`budibase/app-build-guide.md`](budibase/app-build-guide.md).

## Scope

**Built:** intake form (registry + AIA pre-screen) → Cosmos DB → confirmation screen.

**Deferred (designed-for, not built):** the agentic step that auto-fills the GC AIA
questionnaire, computes the Impact Level (I–IV) locally, and generates the GC AIA report
(the "TDS certificate"). The form already captures the full AIA pre-screen into
`aia_prescreen`, and an `aia_results` Cosmos collection is reserved for it. See the
mapping table at the end of `docs/intake-fields.md`.
