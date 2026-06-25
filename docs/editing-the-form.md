# Editing the form — add or change fields

The form is a single SurveyJS model in **`app/public/survey.js`**. You don't touch the
server to add fields: `server.js` generically reshapes whatever the form submits into the
Cosmos document, driven entirely by the field **names**. Keep
[`intake-fields.md`](intake-fields.md) (the field spec) in sync when you change things.

Repo: <https://github.com/PacifiCan/AIRegistry>

## How the pieces fit

```
app/public/survey.js   ->  the form model (pages -> elements)
app/server.js          ->  splits each field name on "__" and nests it, then inserts to Cosmos
docs/intake-fields.md  ->  the human-readable spec (source of truth)
```

`survey.js` shape:

```js
window.surveyJson = {
  pages: [
    { name: "s4", title: "3 · Lifecycle, Classification & Feasibility",
      elements: [ /* questions, or panels that contain questions */ ] }
  ]
};
```

## The naming rule (this is the important part)

A question's `name` uses **`__`** (double underscore) as a path delimiter. The server
turns `section__subsection__field` into nested JSON:

| Question `name` | Lands in Cosmos as |
|---|---|
| `classification__lifecycle_phase` | `{ classification: { lifecycle_phase: ... } }` |
| `aia_prescreen__risk_profile__material_impact` | `{ aia_prescreen: { risk_profile: { material_impact: ... } } }` |

So to add a field to an existing group, just prefix its name with that group
(`identification__…`, `overview__…`, `classification__…`, `aia_prescreen__<sub>__…`,
`pacifican__<sub>__…`). No server change needed.

## Field types

| Need | `type` | Notes |
|---|---|---|
| Single-line text | `text` | add `inputType: "email"` + `validators: [{ "type": "email" }]` for email |
| Multi-line text | `comment` | |
| Single choice | `dropdown` | add `choices: ["A","B"]` |
| Multiple choice | `checkbox` | add `choices: [...]`; stored as an array |
| Yes / No | `boolean` | stored as `true`/`false` |

Common extras on any element: `isRequired: true`, `defaultValue: "…"`,
`description: "helper text"`, `visibleIf: "<expression>"`.

## Recipes

**Add a text field to an existing section** — add to that page's `elements`:

```js
{ type: "text", name: "classification__cost_estimate", title: "Rough cost estimate (CAD)" }
```

**Add a dropdown:**

```js
{ type: "dropdown", name: "overview__priority", title: "Priority",
  choices: ["Low", "Medium", "High"] }
```

**Make a field conditional** — show only when another answer matches:

```js
{ type: "comment", name: "classification__parking_reason", title: "Why park it?",
  visibleIf: "{classification__next_decision} = 'Stop or park'" }
```
Expressions support `=`, `<>`, `and`, `or`, and `anyof ['x','y']` for checkboxes.

**Add a whole new section** — add a page to `pages`:

```js
{ name: "s7", title: "6 · Costing",
  elements: [
    { type: "boolean", name: "costing__funded", title: "Is funding secured?" },
    { type: "text", name: "costing__amount", title: "Amount (CAD)", visibleIf: "{costing__funded} = true" }
  ] }
```

**Group fields visually inside a page** — wrap them in a panel (panels are display-only;
data still nests by the field name):

```js
{ type: "panel", name: "p_costing", title: "Costing",
  elements: [ { type: "text", name: "costing__amount", title: "Amount" } ] }
```

## Test locally before deploying

```bash
cd app
cp .env.example .env          # add your Cosmos connection string for a real save
npm install
npm start                     # http://localhost:8080
```

Quick model sanity check (no browser needed):

```bash
node -e "global.window={};require('./public/survey.js');const s=window.surveyJson;const n=[];(function w(e){for(const x of e){if(x.elements)w(x.elements);if(x.name&&x.name.includes('__'))n.push(x.name);}})(s.pages.flatMap(p=>p.elements));const d=n.filter((x,i)=>n.indexOf(x)!==i);console.log('fields:',n.length,'duplicates:',d.length?d:'none');"
```
Fix any duplicate names (two questions must never share a `name`).

## Deploy the change

```bash
cd app
RUNTIME="NODE:24-lts" bash ../azure/deploy.sh
```
Then hard-refresh the site (Ctrl+Shift+R) to bypass the cached page.

## Keep the spec in sync

After changing fields, update [`intake-fields.md`](intake-fields.md) so the spec, the
form, and the Cosmos shape stay aligned — and so the future AIA agent (which reads
`aia_prescreen.*`) keeps working.
