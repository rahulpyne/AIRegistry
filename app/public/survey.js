/* PacifiCan AI Registry intake — SurveyJS model.
 * Built from docs/intake-fields.md (S2–S6 incl. the AIA pre-screen).
 * Question names use "__" as a path delimiter (e.g. aia_prescreen__risk_profile__material_impact);
 * the server unflattens them into the nested Cosmos document. */
window.surveyJson = {
  title: "AI Registry Intake Form",
  description:
    "Inventory an AI idea, experiment, prototype, or pilot. Fields marked * are required before triage.",
  showProgressBar: "top",
  progressBarType: "pages",
  showQuestionNumbers: "off",
  widthMode: "responsive",
  completedHtml: "<h3>Thank you — your AI Registry submission has been received.</h3>",
  pages: [
    {
      name: "s2",
      title: "1 · Identification & Contacts",
      elements: [
        { type: "text", name: "identification__use_case_title", title: "Use Case Title", isRequired: true, description: "Short, product-style name." },
        { type: "text", name: "identification__rda_organization", title: "RDA / Organization", defaultValue: "PacifiCan", isRequired: true },
        { type: "text", name: "identification__business_area", title: "Business Area / Program", isRequired: true, description: "Branch, program, or corporate function (BSP, RIE, CEDD, RTRI, Indigenous ED, HR/CAS)." },
        { type: "text", name: "identification__region", title: "Region", isRequired: true },
        { type: "text", name: "identification__main_contact_name", title: "Main Contact — Name", isRequired: true },
        { type: "text", name: "identification__main_contact_email", title: "Main Contact — Email", isRequired: true, inputType: "email", validators: [{ type: "email" }] },
        { type: "text", name: "identification__sector_contact_email", title: "Sector / Program Contact — Email", inputType: "email", validators: [{ type: "email" }] },
        { type: "text", name: "identification__sme_email", title: "Subject Matter Expert — Email", inputType: "email", validators: [{ type: "email" }] },
        { type: "text", name: "identification__tech_lead_email", title: "Technical Lead — Email", inputType: "email", validators: [{ type: "email" }] },
        { type: "text", name: "identification__dg_approver_email", title: "DG Approver — Email", inputType: "email", validators: [{ type: "email" }] }
      ]
    },
    {
      name: "s3",
      title: "2 · Initiative Overview",
      elements: [
        { type: "comment", name: "overview__description", title: "Description of the AI Initiative", isRequired: true },
        { type: "comment", name: "overview__problem_statement", title: "Problem Statement", isRequired: true, description: "State the pain point before the solution." },
        { type: "comment", name: "overview__expected_outcome", title: "Expected Outcome / Measurable Result", isRequired: true },
        { type: "dropdown", name: "overview__program_alignment", title: "Program Alignment", isRequired: true,
          choices: ["BSP", "RIE", "CEDD", "RTRI", "Indigenous Economic Development", "Lytton", "Other"] },
        { type: "comment", name: "overview__associated_research", title: "Associated Research Project (name + brief description, if any)" },
        { type: "boolean", name: "overview__shareable_with_tbs", title: "Could this be shared with TBS?" },
        { type: "comment", name: "overview__primary_users", title: "Primary Users" },
        { type: "comment", name: "overview__areas_of_impact", title: "Areas of Impact (labour, time, automation, cost, revenue, client satisfaction)" }
      ]
    },
    {
      name: "s4",
      title: "3 · Lifecycle, Classification & Feasibility",
      elements: [
        { type: "dropdown", name: "classification__lifecycle_phase", title: "Lifecycle Phase",
          choices: ["Experiment & Innovate", "Prototype & Validate", "Pilot & Test", "Build & Scale", "Production & Operate"] },
        { type: "dropdown", name: "classification__status", title: "Current Status",
          choices: ["New", "Under Review", "In Prototype", "In Pilot", "Parked", "Retired", "Production"] },
        { type: "dropdown", name: "classification__solution_type", title: "Solution Type",
          choices: ["AI", "Automation", "Dashboard", "Process Redesign", "Training", "Mixed"] },
        { type: "dropdown", name: "classification__business_value", title: "Business Value Category",
          choices: ["Service Quality", "Operational Efficiency", "Risk Reduction", "Employee Experience", "Policy Delivery", "Financial Stewardship"] },
        { type: "dropdown", name: "classification__it_involvement", title: "IT Involvement Needed",
          choices: ["None", "Light Advisory", "Advisory", "Full Involvement"] },
        { type: "dropdown", name: "classification__next_decision", title: "Next Decision Needed",
          choices: ["Validate requirements", "Approve prototype", "Security review", "Move to pilot", "Stop or park"] },
        { type: "boolean", name: "classification__time_sensitive", title: "Is this time-sensitive?" },
        { type: "text", name: "classification__time_sensitive_driver", title: "Time-sensitivity driver / date", visibleIf: "{classification__time_sensitive} = true" },
        { type: "checkbox", name: "classification__data_source", title: "Data Source",
          choices: ["SharePoint", "Local HD", "Oracle DB", "AWS", "Azure Storage", "GitHub", "DevOps", "Other"] },
        { type: "checkbox", name: "classification__data_type", title: "Data Type",
          choices: ["Spreadsheets", "CRM", "Emails", "Customer-support platforms", "Word", "PDFs", "Shape files", "Images", "Other"] },
        { type: "dropdown", name: "classification__data_classification", title: "Data Classification",
          choices: ["Unclassified", "Protected A", "Protected B", "Protected C", "Unknown"] },
        { type: "dropdown", name: "classification__sensitivity_assessed", title: "Statement of Sensitivity (assessed?)",
          choices: ["Yes", "No", "In progress"] },
        { type: "checkbox", name: "classification__feasibility", title: "Feasibility (check all that apply)",
          choices: [
            "Data is available and usable", "Required AI methods are technically mature",
            "Internal or external expertise can support this", "Budget or funding is feasible",
            "Tools/infrastructure/platforms are accessible", "Legal or policy issues are manageable",
            "Stakeholder or partner support is realistic", "Implementation can begin within 6–12 months"] },
        { type: "checkbox", name: "classification__tools_in_use", title: "Tools in use (check all that apply)",
          choices: [
            "Data pipelines/platforms (Databricks, Data Factory, MS Fabric)",
            "Modelling & BI (Power BI, SPSS, MATLAB)",
            "AI/ML stack (Azure ML, Computer Vision, Hugging Face, Azure AI Foundry)",
            "Web front-end (Static Web, Web Apps, React)",
            "Coding tools (Anaconda, R Studio, VS Code)",
            "Storage (SharePoint, Data Lake, Oracle DB, Azure Blob)",
            "Mockup & visualization (Figma, Balsamiq, Visio)",
            "Code repos (GitHub, Azure DevOps)",
            "Spatial tools (ArcGIS Online, QGIS, GRASS GIS)",
            "None — ideation/planning"] },
        { type: "boolean", name: "classification__aia_required",
          title: "Does this involve a real or contemplated administrative decision, or Protected data?",
          description: "If yes (or Protected data above), the AIA Pre-Screen section will appear next." }
      ]
    },
    {
      name: "s5",
      title: "4 · Algorithmic Impact Assessment (AIA) Pre-Screen",
      visibleIf: "{classification__aia_required} = true or {classification__data_classification} anyof ['Protected A','Protected B','Protected C']",
      elements: [
        { type: "panel", name: "p_business_drivers", title: "5.1 Business Drivers", elements: [
          { type: "comment", name: "aia_prescreen__business_drivers__problem_solved", title: "What client- or program-facing problem is this meant to solve?" },
          { type: "comment", name: "aia_prescreen__business_drivers__intended_benefits", title: "Intended benefits (speed, consistency, capacity, accuracy)?" },
          { type: "boolean", name: "aia_prescreen__business_drivers__makes_admin_decision", title: "Does it make, or assist in making, an administrative decision about a client/business?" },
          { type: "text", name: "aia_prescreen__business_drivers__makes_admin_decision_detail", title: "If yes, describe", visibleIf: "{aia_prescreen__business_drivers__makes_admin_decision} = true" },
          { type: "comment", name: "aia_prescreen__business_drivers__current_human_process", title: "Would a human do this task today? What is the current process?" }
        ]},
        { type: "panel", name: "p_risk_profile", title: "5.2 Risk Profile", elements: [
          { type: "comment", name: "aia_prescreen__risk_profile__vulnerable_or_sensitive", title: "Are the line of business / clients especially vulnerable, or the matter sensitive?" },
          { type: "comment", name: "aia_prescreen__risk_profile__material_impact", title: "Could the decision materially impact rights, economic interests, or access to services?" },
          { type: "comment", name: "aia_prescreen__risk_profile__reversible", title: "Is the decision reversible? How is it corrected if wrong?" },
          { type: "dropdown", name: "aia_prescreen__risk_profile__impact_duration", title: "How long does the impact last?", choices: ["Momentary", "Short-term", "Long-term"] },
          { type: "comment", name: "aia_prescreen__risk_profile__prior_concern", title: "Has this type of system raised public/ethical/legal concern before?" }
        ]},
        { type: "panel", name: "p_system", title: "5.3 About the System", elements: [
          { type: "text", name: "aia_prescreen__system__owner_operator", title: "Who owns and operates the system (program, IT, vendor)?" },
          { type: "dropdown", name: "aia_prescreen__system__build_type", title: "Build type", choices: ["In-house", "Procured", "Managed service"] },
          { type: "text", name: "aia_prescreen__system__platform", title: "Platform name" },
          { type: "text", name: "aia_prescreen__system__hosting_region", title: "Where is it hosted / data processed (region)?" },
          { type: "comment", name: "aia_prescreen__system__integrations", title: "What systems does it integrate with (CRM, case management, storage)?" }
        ]},
        { type: "panel", name: "p_algorithm", title: "5.4 About the Algorithm", elements: [
          { type: "checkbox", name: "aia_prescreen__algorithm__model_type", title: "Model / approach", choices: ["Rules", "ML", "Generative LLM", "Retrieval"] },
          { type: "comment", name: "aia_prescreen__algorithm__explainable", title: "Can the output be explained to the affected client in plain language?" },
          { type: "comment", name: "aia_prescreen__algorithm__training_data", title: "What data was the model trained or grounded on, and who provided it?" },
          { type: "boolean", name: "aia_prescreen__algorithm__reasoning_or_citation", title: "Is human-understandable reasoning or a citation provided with each output?" }
        ]},
        { type: "panel", name: "p_decision", title: "5.5 About the Decision", elements: [
          { type: "comment", name: "aia_prescreen__decision__decision_made", title: "What specific decision does the system make or recommend?" },
          { type: "text", name: "aia_prescreen__decision__program_area", title: "Which program / decision area (e.g., grants & contributions)?" },
          { type: "boolean", name: "aia_prescreen__decision__human_review", title: "Does a human review/approve the output before it takes effect?" },
          { type: "text", name: "aia_prescreen__decision__human_review_detail", title: "Describe the review step", visibleIf: "{aia_prescreen__decision__human_review} = true" }
        ]},
        { type: "panel", name: "p_impact", title: "5.6 Impact Assessment", elements: [
          { type: "comment", name: "aia_prescreen__impact__who_affected", title: "Who is affected and how (individuals, businesses, communities)?" },
          { type: "comment", name: "aia_prescreen__impact__rights_impact", title: "Impact on rights, health/economic well-being, or dignity?" },
          { type: "comment", name: "aia_prescreen__impact__environmental_impact", title: "Are there environmental impacts?" },
          { type: "comment", name: "aia_prescreen__impact__gba_plus_disadvantage", title: "Could it disadvantage particular groups (GBA Plus lens)?" },
          { type: "comment", name: "aia_prescreen__impact__wrong_outcome_magnitude", title: "Magnitude and duration of a wrong or biased outcome?" }
        ]},
        { type: "panel", name: "p_data", title: "5.7 About the Data", elements: [
          { type: "boolean", name: "aia_prescreen__data__uses_personal_info", title: "Does the system use personal information?" },
          { type: "text", name: "aia_prescreen__data__personal_info_elements", title: "Describe the elements", visibleIf: "{aia_prescreen__data__uses_personal_info} = true" },
          { type: "comment", name: "aia_prescreen__data__provenance", title: "Source and provenance of the data?" },
          { type: "dropdown", name: "aia_prescreen__data__classification", title: "Data classification", choices: ["Unclassified", "Protected A", "Protected B", "Protected C"] },
          { type: "comment", name: "aia_prescreen__data__accuracy_currency", title: "How accurate, current, and representative is the data?" },
          { type: "comment", name: "aia_prescreen__data__retention_disposal", title: "Retention and disposal arrangements?" }
        ]},
        { type: "panel", name: "p_consultations", title: "5.8 Consultations", elements: [
          { type: "comment", name: "aia_prescreen__consultations__internal_stakeholders", title: "Internal stakeholders consulted (privacy, security, legal, OL, IT)?" },
          { type: "comment", name: "aia_prescreen__consultations__external_stakeholders", title: "External stakeholders or affected communities engaged?" },
          { type: "dropdown", name: "aia_prescreen__consultations__gba_plus_done", title: "Has a GBA Plus analysis been conducted or planned?", choices: ["Yes", "No", "Planned"] }
        ]},
        { type: "panel", name: "p_mitigation", title: "5.9 De-risking & Mitigation (Design → Implementation)", elements: [
          { type: "comment", name: "aia_prescreen__mitigation__data_quality", title: "Data quality (validation, bias testing, documentation)" },
          { type: "comment", name: "aia_prescreen__mitigation__procedural_fairness", title: "Procedural fairness (recourse, notice, contest, human review, explanation)" },
          { type: "comment", name: "aia_prescreen__mitigation__privacy", title: "Privacy (privacy-by-design, minimization, PIA status, access, retention)" },
          { type: "comment", name: "aia_prescreen__mitigation__human_in_the_loop", title: "Human-in-the-loop (who reviews and is accountable for each output)" },
          { type: "comment", name: "aia_prescreen__mitigation__security_logging", title: "Security & logging (access control, audit trail, monitoring, incident handling)" }
        ]}
      ]
    },
    {
      name: "s6",
      title: "5 · PacifiCan-Specific Considerations",
      elements: [
        { type: "panel", name: "p_mandate", title: "6.1 Program & Mandate Alignment", elements: [
          { type: "checkbox", name: "pacifican__mandate__programs_served", title: "Which PacifiCan program(s) does this serve?", choices: ["BSP", "RIE", "CEDD", "RTRI", "Indigenous ED", "Lytton"] },
          { type: "comment", name: "pacifican__mandate__red_outcomes", title: "How does it advance regional economic development outcomes?" },
          { type: "boolean", name: "pacifican__mandate__reusable", title: "Is the capability reusable across programs or regions?" }
        ]},
        { type: "panel", name: "p_ol", title: "6.2 Official Languages & Accessibility", elements: [
          { type: "boolean", name: "pacifican__official_languages__bilingual_equal_quality", title: "Outputs delivered in English and French with equal quality?" },
          { type: "boolean", name: "pacifican__official_languages__wcag_aa", title: "User surfaces meet WCAG 2.1 AA?" },
          { type: "boolean", name: "pacifican__official_languages__plain_language_review", title: "Plain-language review planned for client-facing output?" }
        ]},
        { type: "panel", name: "p_residency", title: "6.3 Data Residency & Protected B", elements: [
          { type: "boolean", name: "pacifican__residency__data_in_canada", title: "All data stored and processed inside Canada?" },
          { type: "boolean", name: "pacifican__residency__approved_for_classification", title: "Environment approved for the data classification used (up to Protected B)?" },
          { type: "boolean", name: "pacifican__residency__cross_border_excluded", title: "Cross-border inference / global endpoints excluded?" }
        ]},
        { type: "panel", name: "p_accountability", title: "6.4 Human Accountability", elements: [
          { type: "boolean", name: "pacifican__accountability__human_accountable_confirmed", title: "Confirm a human remains accountable for any decision." },
          { type: "text", name: "pacifican__accountability__accountable_role", title: "Accountable officer/role for outputs affecting clients" }
        ]},
        { type: "panel", name: "p_indigenous", title: "6.5 Indigenous Data Considerations", elements: [
          { type: "boolean", name: "pacifican__indigenous_data__uses_indigenous_data", title: "Does it use data about Indigenous individuals, communities, or businesses?" },
          { type: "comment", name: "pacifican__indigenous_data__ocap_respected", title: "If yes, how are OCAP® principles and data-governance agreements respected?", visibleIf: "{pacifican__indigenous_data__uses_indigenous_data} = true" }
        ]}
      ]
    }
  ]
};
