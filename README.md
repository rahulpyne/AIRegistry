# AI Registry (PacifiCan)

A **SurveyJS** intake form, served by a small Node/Express app on **Azure App Service**,
that captures AI Registry submissions — all PacifiCan registry fields **plus the AIA
pre-screen** — and stores each as a JSON document in **Azure Cosmos DB** (MongoDB API).
After submitting, the user sees a confirmation with the saved reference id.

Source of truth for fields: `AI_Registry_Intake_Form_PacifiCan.docx`.

## Layout

```
app/                      # the SurveyJS application
  server.js               # Express: serves the form + POST /api/submit -> Cosmos
  public/index.html       # SurveyJS page
  public/survey.js         # the form model (S2–S6 incl. AIA pre-screen)
  package.json
  .env.example
azure/
  deploy.sh               # one-shot: ensure Cosmos, deploy app, set settings
  deploy.md               # deployment guide (Azure Cloud Shell)
docs/
  intake-fields.md        # full field spec + Cosmos doc shape + future-AIA mapping
archive/                  # retired implementations (not deployed)
  legacy-flask-app/       # original Flask app (form + idea graph + lifecycle board)
  legacy-graph-spa/       # standalone Cytoscape/Design-Component idea graph
```

## Quick start

1. Understand the fields: [`docs/intake-fields.md`](docs/intake-fields.md).
2. Run locally: `cd app && cp .env.example .env` (add your Cosmos connection string),
   `npm install && npm start`, open http://localhost:8080.
3. Deploy to Azure: [`azure/deploy.md`](azure/deploy.md).

## Stack

- **SurveyJS** (`survey-core` + `survey-js-ui` from CDN) renders the form from
  `public/survey.js`.
- **Express** serves the static page and a single `POST /api/submit` endpoint that
  reshapes the flat survey result into the nested document in `docs/intake-fields.md` and
  inserts it into Cosmos DB via the MongoDB driver.
- **Azure App Service** (free F1 tier works — it's a stateless Node app) + **Cosmos DB
  for MongoDB**.

## Scope

**Built:** SurveyJS intake form (registry + AIA pre-screen) → Cosmos DB → confirmation.

**Deferred (designed-for, not built):** the agentic step that auto-fills the GC AIA
questionnaire, computes the Impact Level (I–IV) locally, and generates the GC AIA report.
The form already captures the full AIA pre-screen into `aia_prescreen`, and an
`aia_results` Cosmos collection is reserved for it. See the mapping table at the end of
`docs/intake-fields.md`.
