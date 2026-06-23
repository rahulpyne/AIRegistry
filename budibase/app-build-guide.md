# Budibase app build guide — AI Registry intake

Build the intake form + confirmation screen against the Cosmos **MongoDB** datasource.
Field names, types, enums and the nested JSON shape come from
[`../docs/intake-fields.md`](../docs/intake-fields.md) — keep that open alongside this.

> Budibase's MongoDB connector is **query-based** (not auto-bound tables like SQL).
> So we define a few queries, then drive them from a form. The `insertOne` document
> below is the important artifact — it builds the exact nested shape the future AIA
> agent expects.

## 1. Add the datasource

1. **Data → + → MongoDB.**
2. **Connection string:** paste the Cosmos `COSMOS_MONGO_CONNECTION_STRING`
   (Portal → Cosmos account → Connection strings → PRIMARY). It already includes
   `ssl=true` + `retrywrites=false`, which Cosmos requires.
3. **Database:** `airegistry`. Save & verify the connection.

## 2. Create the queries

Under the datasource, add three queries against collection **`registry_entries`**:

### `createEntry` — Create (insertOne)
Set "Function" = **insertOne**, collection = `registry_entries`, and the **JSON** body to
the document below. Each `{{ binding }}` is a query binding you'll map to a form field in
step 4. Booleans/numbers: leave unquoted; everything else quoted.

```json
{
  "submitted_at": "{{ submitted_at }}",
  "schema_version": 1,
  "aia_status": "captured",
  "identification": {
    "use_case_title": "{{ use_case_title }}",
    "rda_organization": "{{ rda_organization }}",
    "business_area": "{{ business_area }}",
    "region": "{{ region }}",
    "main_contact_name": "{{ main_contact_name }}",
    "main_contact_email": "{{ main_contact_email }}",
    "sector_contact_email": "{{ sector_contact_email }}",
    "sme_email": "{{ sme_email }}",
    "tech_lead_email": "{{ tech_lead_email }}",
    "dg_approver_email": "{{ dg_approver_email }}"
  },
  "overview": {
    "description": "{{ description }}",
    "problem_statement": "{{ problem_statement }}",
    "expected_outcome": "{{ expected_outcome }}",
    "program_alignment": "{{ program_alignment }}",
    "associated_research": "{{ associated_research }}",
    "shareable_with_tbs": {{ shareable_with_tbs }},
    "primary_users": "{{ primary_users }}",
    "areas_of_impact": "{{ areas_of_impact }}"
  },
  "classification": {
    "lifecycle_phase": "{{ lifecycle_phase }}",
    "status": "{{ status }}",
    "solution_type": "{{ solution_type }}",
    "business_value": "{{ business_value }}",
    "it_involvement": "{{ it_involvement }}",
    "next_decision": "{{ next_decision }}",
    "time_sensitive": {{ time_sensitive }},
    "time_sensitive_driver": "{{ time_sensitive_driver }}",
    "data_source": {{ data_source }},
    "data_type": {{ data_type }},
    "data_classification": "{{ data_classification }}",
    "sensitivity_assessed": "{{ sensitivity_assessed }}",
    "feasibility": {{ feasibility }},
    "tools_in_use": {{ tools_in_use }}
  },
  "aia_prescreen": {
    "business_drivers": {
      "problem_solved": "{{ ap_problem_solved }}",
      "intended_benefits": "{{ ap_intended_benefits }}",
      "makes_admin_decision": {{ ap_makes_admin_decision }},
      "makes_admin_decision_detail": "{{ ap_makes_admin_decision_detail }}",
      "current_human_process": "{{ ap_current_human_process }}"
    },
    "risk_profile": {
      "vulnerable_or_sensitive": "{{ ap_vulnerable_or_sensitive }}",
      "material_impact": "{{ ap_material_impact }}",
      "reversible": "{{ ap_reversible }}",
      "impact_duration": "{{ ap_impact_duration }}",
      "prior_concern": "{{ ap_prior_concern }}"
    },
    "system": {
      "owner_operator": "{{ ap_owner_operator }}",
      "build_type": "{{ ap_build_type }}",
      "platform": "{{ ap_platform }}",
      "hosting_region": "{{ ap_hosting_region }}",
      "integrations": "{{ ap_integrations }}"
    },
    "algorithm": {
      "model_type": {{ ap_model_type }},
      "explainable": "{{ ap_explainable }}",
      "training_data": "{{ ap_training_data }}",
      "reasoning_or_citation": {{ ap_reasoning_or_citation }}
    },
    "decision": {
      "decision_made": "{{ ap_decision_made }}",
      "program_area": "{{ ap_program_area }}",
      "human_review": {{ ap_human_review }},
      "human_review_detail": "{{ ap_human_review_detail }}"
    },
    "impact": {
      "who_affected": "{{ ap_who_affected }}",
      "rights_impact": "{{ ap_rights_impact }}",
      "environmental_impact": "{{ ap_environmental_impact }}",
      "gba_plus_disadvantage": "{{ ap_gba_plus_disadvantage }}",
      "wrong_outcome_magnitude": "{{ ap_wrong_outcome_magnitude }}"
    },
    "data": {
      "uses_personal_info": {{ ap_uses_personal_info }},
      "personal_info_elements": "{{ ap_personal_info_elements }}",
      "provenance": "{{ ap_provenance }}",
      "classification": "{{ ap_data_classification }}",
      "accuracy_currency": "{{ ap_accuracy_currency }}",
      "retention_disposal": "{{ ap_retention_disposal }}"
    },
    "consultations": {
      "internal_stakeholders": "{{ ap_internal_stakeholders }}",
      "external_stakeholders": "{{ ap_external_stakeholders }}",
      "gba_plus_done": "{{ ap_gba_plus_done }}"
    },
    "mitigation": {
      "data_quality": "{{ ap_m_data_quality }}",
      "procedural_fairness": "{{ ap_m_procedural_fairness }}",
      "privacy": "{{ ap_m_privacy }}",
      "human_in_the_loop": "{{ ap_m_human_in_the_loop }}",
      "security_logging": "{{ ap_m_security_logging }}"
    }
  },
  "pacifican": {
    "mandate": {
      "programs_served": {{ pc_programs_served }},
      "red_outcomes": "{{ pc_red_outcomes }}",
      "reusable": {{ pc_reusable }}
    },
    "official_languages": {
      "bilingual_equal_quality": {{ pc_bilingual_equal_quality }},
      "wcag_aa": {{ pc_wcag_aa }},
      "plain_language_review": {{ pc_plain_language_review }}
    },
    "residency": {
      "data_in_canada": {{ pc_data_in_canada }},
      "approved_for_classification": {{ pc_approved_for_classification }},
      "cross_border_excluded": {{ pc_cross_border_excluded }}
    },
    "accountability": {
      "human_accountable_confirmed": {{ pc_human_accountable_confirmed }},
      "accountable_role": "{{ pc_accountable_role }}"
    },
    "indigenous_data": {
      "uses_indigenous_data": {{ pc_uses_indigenous_data }},
      "ocap_respected": "{{ pc_ocap_respected }}"
    }
  }
}
```

> **Multiselect/boolean bindings** (`data_source`, `data_type`, `feasibility`,
> `tools_in_use`, `model_type`, `programs_served`, and all `bool` fields) are inserted
> **unquoted** so they land as JSON arrays / true|false. Budibase multiselect fields
> return a JSON array string — bind directly. For booleans, bind the checkbox/Yes-No
> value (true/false).

### `getEntry` — Read (findOne)
Function = **findOne**, JSON: `{ "_id": { "$oid": "{{ id }}" } }`. Binding `id`.
Used by the confirmation screen.

### `listEntries` — Read (find), optional admin view
Function = **find**, JSON `{}`, sort `{ "submitted_at": -1 }`. (Not required for this
build, but handy for an admin/triage table later.)

## 3. Build the "Submit Idea" screen

1. **Design → Screens → + → Blank**, route `/submit`.
2. Add a **Multi-step Form Block** (or a Form + Section headers). Create one step per
   document section: **S2 Identification**, **S3 Overview**, **S4 Classification**,
   **S5 AIA Pre-Screen**, **S6 PacifiCan**.
3. Add field components matching the spec — use the right type per
   `intake-fields.md`: Text, Long Form Text, Select (single), Multi-select, and
   Boolean (Options/“Yes/No”). Set the **enum options** exactly as listed there.
4. Mark the **Req** fields as required; set `rda_organization` default `PacifiCan`.
5. **Conditional S5:** on the S5 step (or its fields), add a condition to show only when
   `ap_makes_admin_decision` is true **OR** `data_classification` is one of
   `Protected A / Protected B / Protected C` (matches the doc's "complete once a real
   decision or Protected data").

## 4. Wire the submit action

On the form's **Submit** button → **Actions**:
1. **Validate Form.**
2. **Execute Query → `createEntry`.** Map each query binding to its form field
   (e.g. `use_case_title` → the Use Case Title field's value). For `submitted_at`, bind
   the handlebars helper `{{ date now }}` (ISO timestamp).
3. **Save the new id:** set a State variable `newEntryId` to the query result's inserted
   id (`{{ Execute Query.insertedId }}` / `{{ Execute Query.rows.0._id }}` — confirm the
   exact path from the query's preview output).
4. **Navigate To** `/confirmation?id={{ State.newEntryId }}`.

## 5. Build the "Submission confirmation" screen

1. New screen, route `/confirmation`, reads the `id` URL param.
2. **Data Provider → `getEntry`**, binding `id = {{ URL.id }}`.
3. Inside it, lay out read-only text components showing every submitted field grouped by
   section (mirror the form), e.g. `{{ Data Provider.Rows.0.identification.use_case_title }}`,
   `{{ Data Provider.Rows.0.aia_prescreen.risk_profile.material_impact }}`, etc.
4. Show the id and `submitted_at` at the top, plus a "Submit another" link back to `/submit`.

## 6. Verify, then export

- Publish the app. Submit a test entry. In Azure Portal (Cosmos → Data Explorer) or
  `mongosh`, confirm a `registry_entries` document with the full nested shape incl.
  `aia_prescreen`. Confirm the confirmation screen renders every field.
- **Export** the app (app → Export) and save the `.tar.gz` to `app-export/`; commit.
