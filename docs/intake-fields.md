# AI Registry — Intake Field Spec

Source of truth: **`AI_Registry_Intake_Form_PacifiCan.docx`** (PacifiCan · AI Operating
Lifecycle Artifact, rev 1.0). This is the spec the Budibase intake form is built from
and the shape each submission takes in **Cosmos DB for MongoDB** (`registry_entries`).

Conventions:
- **Req** = required before triage.
- **Type**: `text` (single line), `longtext` (multi-line), `select` (single choice),
  `multiselect` (checkboxes), `bool` (Yes/No), `email`.
- JSON keys are grouped into nested objects (`identification`, `overview`,
  `classification`, `aia_prescreen`, `pacifican`) so the form maps 1:1 to the document
  sections and the future AIA agent can read each section cleanly.

---

## S2 — Identification & Contacts  → `identification`

| Field | JSON key | Type | Req | Notes |
|---|---|---|---|---|
| Use Case Title | `use_case_title` | text | ✔ | Short, product-style name. |
| RDA / Organization | `rda_organization` | text | ✔ | Default `PacifiCan`. |
| Business Area / Program | `business_area` | text | ✔ | Branch/program/corp function (BSP, RIE, CEDD, RTRI, Indigenous ED, HR/CAS). |
| Region | `region` | text | ✔ | Regional office/area. |
| Main Contact — Name | `main_contact_name` | text | ✔ | Primary contact who can explain the idea. |
| Main Contact — Email | `main_contact_email` | email | ✔ | |
| Sector / Program Contact — Email | `sector_contact_email` | email | | |
| SME — Email | `sme_email` | email | | Validates content, rules, AI outputs. |
| Technical Lead — Email | `tech_lead_email` | email | | Assesses technical feasibility. |
| DG Approver — Email | `dg_approver_email` | email | | DG accountable for resourcing / external sharing (e.g. to TBS). |

## S3 — Initiative Overview  → `overview`

| Field | JSON key | Type | Req | Notes |
|---|---|---|---|---|
| Description of the AI Initiative | `description` | longtext | ✔ | Overview of the process/use case. |
| Problem Statement | `problem_statement` | longtext | ✔ | State the pain point before the solution. |
| Expected Outcome / Measurable Result | `expected_outcome` | longtext | ✔ | Measurable/observable success. |
| Program Alignment | `program_alignment` | select | ✔ | PacifiCan program; see enum below. |
| Associated Research Project | `associated_research` | longtext | | Name + brief description if any. |
| Could this be shared with TBS? | `shareable_with_tbs` | bool | | Signals future GC AI Registry candidate. |
| Primary Users | `primary_users` | longtext | | Officers, managers, applicants, analysts, public. |
| Areas of Impact | `areas_of_impact` | longtext | | Labour, time, automation, cost, revenue, client satisfaction. |

**`program_alignment` enum:** `BSP`; `RIE`; `CEDD`; `RTRI`; `Indigenous Economic Development`; `Lytton`; `Other`.

## S4 — Lifecycle, Classification & Feasibility  → `classification`

**4.1 Lifecycle & Governance**

| Field | JSON key | Type | Allowed values |
|---|---|---|---|
| Lifecycle Phase | `lifecycle_phase` | select | Experiment & Innovate; Prototype & Validate; Pilot & Test; Build & Scale; Production & Operate |
| Current Status | `status` | select | New; Under Review; In Prototype; In Pilot; Parked; Retired; Production |
| Solution Type | `solution_type` | select | AI; Automation; Dashboard; Process Redesign; Training; Mixed |
| Business Value Category | `business_value` | select | Service Quality; Operational Efficiency; Risk Reduction; Employee Experience; Policy Delivery; Financial Stewardship |
| IT Involvement Needed | `it_involvement` | select | None; Light Advisory; Advisory; Full Involvement |
| Next Decision Needed | `next_decision` | select | Validate requirements; Approve prototype; Security review; Move to pilot; Stop or park |
| Is this time-sensitive? | `time_sensitive` | bool | + `time_sensitive_driver` (text) if Yes |

**4.2 Data**

| Field | JSON key | Type | Allowed values |
|---|---|---|---|
| Data Source | `data_source` | multiselect | SharePoint; Local HD; Oracle DB; AWS; Azure Storage; GitHub; DevOps; Other |
| Data Type | `data_type` | multiselect | Spreadsheets; CRM; Emails; Customer-support platforms; Word; PDFs; Shape files; Images; Other |
| Data Classification | `data_classification` | select | Unclassified; Protected A; Protected B; Protected C; Unknown |
| Statement of Sensitivity | `sensitivity_assessed` | select | Yes; No; In progress |

**4.3 Feasibility & Tools**

| Field | JSON key | Type | Notes |
|---|---|---|---|
| Feasibility checklist | `feasibility` | multiselect | Options below |
| Tools in use | `tools_in_use` | multiselect | Options below |

`feasibility` options: Data is available and usable; Required AI methods are technically mature; Internal or external expertise can support this; Budget or funding is feasible; Tools/infrastructure/platforms are accessible; Legal or policy issues are manageable; Stakeholder or partner support is realistic; Implementation can begin within 6–12 months.

`tools_in_use` options: Data pipelines/platforms (Databricks, Data Factory, MS Fabric); Modelling & BI (Power BI, SPSS, MATLAB); AI/ML stack (Azure ML, Computer Vision, Hugging Face, Azure AI Foundry); Web front-end (Static Web, Web Apps, React); Coding tools (Anaconda, R Studio, VS Code); Storage (SharePoint, Data Lake, Oracle DB, Azure Blob); Mockup & visualization (Figma, Balsamiq, Visio); Code repos (GitHub, Azure DevOps); Spatial tools (ArcGIS Online, QGIS, GRASS GIS); None — ideation/planning.

## S5 — AIA Pre-Screen  → `aia_prescreen`

> Captured now, **read by the future AIA agent**. Each sub-section is its own nested
> object so the agent can map sub-section → GC AIA area (see "Future AIA mapping").
> Reveal S5 when `aia_prescreen.decision.makes_admin_decision` = Yes **or**
> `classification.data_classification` is Protected A/B/C (matches the doc).

**5.1 `business_drivers`** — `problem_solved` (longtext); `intended_benefits` (longtext); `makes_admin_decision` (bool + `detail`); `current_human_process` (longtext).
**5.2 `risk_profile`** — `vulnerable_or_sensitive` (longtext); `material_impact` (longtext); `reversible` (longtext); `impact_duration` (select: Momentary; Short-term; Long-term); `prior_concern` (longtext).
**5.3 `system`** — `owner_operator` (text); `build_type` (select: In-house; Procured; Managed service) + `platform` (text); `hosting_region` (text); `integrations` (longtext).
**5.4 `algorithm`** — `model_type` (multiselect: Rules; ML; Generative LLM; Retrieval); `explainable` (longtext); `training_data` (longtext); `reasoning_or_citation` (bool).
**5.5 `decision`** — `decision_made` (longtext); `program_area` (text); `human_review` (bool + `detail`).
**5.6 `impact`** — `who_affected` (longtext); `rights_impact` (longtext); `environmental_impact` (longtext); `gba_plus_disadvantage` (longtext); `wrong_outcome_magnitude` (longtext).
**5.7 `data`** — `uses_personal_info` (bool + `elements`); `provenance` (longtext); `classification` (select: Unclassified; Protected A; Protected B; Protected C); `accuracy_currency` (longtext); `retention_disposal` (longtext).
**5.8 `consultations`** — `internal_stakeholders` (longtext: privacy/security/legal/OL/IT); `external_stakeholders` (longtext); `gba_plus_done` (select: Yes; No; Planned).
**5.9 `mitigation`** — for each area, `measures` (longtext, Design → Implementation): `data_quality`, `procedural_fairness`, `privacy`, `human_in_the_loop`, `security_logging`.

## S6 — PacifiCan-Specific  → `pacifican`

**6.1 `mandate`** — `programs_served` (multiselect: BSP; RIE; CEDD; RTRI; Indigenous ED; Lytton); `red_outcomes` (longtext); `reusable` (bool).
**6.2 `official_languages`** — `bilingual_equal_quality` (bool); `wcag_aa` (bool); `plain_language_review` (bool).
**6.3 `residency`** — `data_in_canada` (bool); `approved_for_classification` (bool); `cross_border_excluded` (bool).
**6.4 `accountability`** — `human_accountable_confirmed` (bool); `accountable_role` (text).
**6.5 `indigenous_data`** — `uses_indigenous_data` (bool); `ocap_respected` (longtext).

---

## Cosmos document shape (`registry_entries`)

```jsonc
{
  "_id": "<ObjectId>",
  "submitted_at": "2026-06-23T18:04:00Z",
  "schema_version": 1,
  "identification": { "use_case_title": "...", "rda_organization": "PacifiCan", "...": "..." },
  "overview":       { "description": "...", "problem_statement": "...", "...": "..." },
  "classification": { "lifecycle_phase": "...", "data_classification": "Protected B", "...": "..." },
  "aia_prescreen":  {
    "business_drivers": { "...": "..." }, "risk_profile": { "...": "..." },
    "system": { "...": "..." }, "algorithm": { "...": "..." }, "decision": { "...": "..." },
    "impact": { "...": "..." }, "data": { "...": "..." }, "consultations": { "...": "..." },
    "mitigation": { "...": "..." }
  },
  "pacifican":      { "mandate": { "...": "..." }, "...": "..." },
  "aia_status": "captured"   // future agent sets "assessed"; impact level/report land in aia_results
}
```

## Future AIA mapping (deferred — do not build now)

When the agentic step is added, it reads `aia_prescreen.*` and maps to the GC AIA
questionnaire per the intake doc's **Section 7** table, computes Impact Level **I–IV**
locally (open-source GC `aia-eia-js` logic), and writes the result + report ("TDS
certificate") to a reserved **`aia_results`** collection keyed by entry `_id`.

| Registry section | GC AIA area | AIA scoring dimension |
|---|---|---|
| `aia_prescreen.business_drivers` | Reasons for Automation / Business Drivers | Risk — project |
| `aia_prescreen.risk_profile` | Risk Profile | Risk — project |
| `aia_prescreen.system` | About the System | Risk — system |
| `aia_prescreen.algorithm` | About the Algorithm | Risk — algorithm |
| `aia_prescreen.decision` | About the Decision | Risk — decision |
| `aia_prescreen.impact` | Impact Assessment | Risk — impact |
| `aia_prescreen.data` | About the Data | Risk — data |
| `aia_prescreen.consultations` | Consultations | Mitigation |
| `aia_prescreen.mitigation` | De-risking & Mitigation | Mitigation |
| `pacifican.*` | Mitigation + project context | Mitigation / context |
