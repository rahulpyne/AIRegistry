# Archive — superseded implementations

These are **retired** implementations of the AI Registry, kept for reference only.
They are **not deployed** and are no longer maintained. The current implementation
is the **Budibase** application — see [`../budibase/`](../budibase/) and the field
spec in [`../docs/intake-fields.md`](../docs/intake-fields.md).

## `legacy-flask-app/`

The original Flask + server-rendered-templates app (gunicorn on Azure App Service):
the AI Registry form, the TF-IDF/Cytoscape **Idea Visualizer** graph, and the
**AI Operating Lifecycle** board, with a `LocalJSONStore` / `SupabaseStore` /
`CosmosStore` storage abstraction. Superseded by the Budibase build, which captures
the fuller PacifiCan intake (incl. the AIA pre-screen) and stores to Cosmos DB.

## `legacy-graph-spa/`

The standalone client-rendered **Idea Graph** (a self-bootstrapping Design Component:
`index.html`, an Obsidian-style canvas force-directed mesh). Was deployed as a static
site on Vercel. Superseded along with the Flask app.

> Why kept: the graph clustering approach and the lifecycle model may be revived as
> views over the Cosmos data once the Budibase intake is in production.
