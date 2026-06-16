"""
Dummy PacifiCan AI Registry entries.

~16 ideas drawn from prior PacifiCan work, designed to form ~5 natural clusters
in the Idea Visualizer:

    * Document & Grants Processing
    * HR & Corporate Services
    * Knowledge & Search
    * Analytics & Executive Insight
    * Client Service Delivery

Each entry uses the AI Registry Form field names (see form.html / storage.py).
`seed(store)` is idempotent: it only seeds when the store has no entries.
"""
from __future__ import annotations

PHASES = [
    "1 · Experiment & Innovate",
    "2 · Prototype & Validate",
    "3 · Pilot & Test",
    "4 · Build & Scale",
    "5 · Production & Operate",
]


def _e(**kw) -> dict:
    base = {
        "rda_organization": "PacifiCan",
        "notes": "",
        "aia_trigger": False,
        "pia_trigger": False,
    }
    base.update(kw)
    return base


ENTRIES = [
    # ── Document & Grants Processing ──────────────────────────────────────
    _e(use_case_title="BSP Intake Co-Pilot",
       business_area="Business Scale-up & Productivity (BSP)",
       contact_person="Rahul Pyne",
       problem_statement="Program officers manually read large grant application packages and extract organization, project, and funding details from PDFs and spreadsheets, which is slow and inconsistent.",
       expected_outcome="Automatically parse application documents and extract structured fields with confidence scores, cutting intake time per application by 70%.",
       ai_tool="Azure AI Foundry agents, Azure Blob Storage, Cosmos DB, Flask",
       security_privacy="Protected B applicant data; human-in-the-loop review before decisions; access restricted to program officers.",
       lifecycle_phase=PHASES[3], status="In Pilot", data_classification="Protected B",
       solution_type="AI", business_value="Operational Efficiency",
       it_involvement="Full Involvement", next_decision="Move to pilot",
       aia_trigger=True, pia_trigger=True,
       notes="Pipeline of doc-intake, completeness, and eligibility agents validated end-to-end."),
    _e(use_case_title="Eligibility Assessment Assistant",
       business_area="Regional Programs",
       contact_person="Program Analyst",
       problem_statement="Determining whether grant applicants meet eligibility criteria requires cross-checking many rules against extracted application data by hand.",
       expected_outcome="Apply eligibility rules automatically and surface pass/fail verdicts with rationale for officer review.",
       ai_tool="Azure AI Foundry, rules engine, Python",
       security_privacy="Protected B; final eligibility decisions remain with officers.",
       lifecycle_phase=PHASES[2], status="In Prototype", data_classification="Protected B",
       solution_type="AI", business_value="Operational Efficiency",
       it_involvement="Advisory", next_decision="Move to pilot", aia_trigger=True, pia_trigger=True),
    _e(use_case_title="Document Completeness Checker",
       business_area="Regional Programs",
       contact_person="Intake Coordinator",
       problem_statement="Applications often arrive missing required documents, and officers discover gaps late in the review.",
       expected_outcome="Verify required documents are present at submission and flag missing items immediately.",
       ai_tool="Azure AI Foundry, document classification",
       security_privacy="Protected B; no decisions, only a presence checklist.",
       lifecycle_phase=PHASES[3], status="In Pilot", data_classification="Protected B",
       solution_type="AI", business_value="Service Quality",
       it_involvement="Advisory", next_decision="Validate requirements", aia_trigger=False, pia_trigger=True),
    _e(use_case_title="Grant Application Triage",
       business_area="Regional Programs",
       contact_person="Intake Lead",
       problem_statement="Incoming grant applications are not prioritized, so high-value or time-sensitive files wait in the same queue as everything else.",
       expected_outcome="Automatically route and prioritize applications by program fit and completeness.",
       ai_tool="Azure AI Foundry, classification model",
       security_privacy="Protected B; routing suggestions reviewed by staff.",
       lifecycle_phase=PHASES[1], status="Under Review", data_classification="Protected B",
       solution_type="AI", business_value="Operational Efficiency",
       it_involvement="Light Advisory", next_decision="Approve prototype", aia_trigger=True, pia_trigger=True),
    _e(use_case_title="Funding Report Generator",
       business_area="Finance & Reporting",
       contact_person="Finance Officer",
       problem_statement="Quarterly funding and disbursement reports are assembled manually from multiple grant records.",
       expected_outcome="Generate draft funding reports automatically from approved application data.",
       ai_tool="Azure OpenAI, Power BI, Python",
       security_privacy="Protected B financial data; drafts reviewed before release.",
       lifecycle_phase=PHASES[1], status="New", data_classification="Protected B",
       solution_type="Automation", business_value="Financial Stewardship",
       it_involvement="Light Advisory", next_decision="Validate requirements"),

    # ── HR & Corporate Services ───────────────────────────────────────────
    _e(use_case_title="HR/CAS Concierge Assistant",
       business_area="HR & Corporate Administrative Services",
       contact_person="Joey Seto",
       problem_statement="Managers repeatedly ask HR and Corporate Administrative Services questions where answers already exist in internal guidance.",
       expected_outcome="Reduce repeated inquiry burden and improve employee self-service with an answer assistant grounded in approved guidance.",
       ai_tool="Microsoft AI Foundry, Azure AI Search, Azure Container Apps, OpenWebUI",
       security_privacy="Use approved internal guidance only; no personal HR case details.",
       lifecycle_phase=PHASES[1], status="In Prototype", data_classification="Protected A",
       solution_type="AI", business_value="Employee Experience",
       it_involvement="Light Advisory", next_decision="Approve prototype", pia_trigger=True,
       notes="Prototype built for stakeholder validation; next step is answer-quality testing."),
    _e(use_case_title="Employee Onboarding Q&A Bot",
       business_area="HR & Corporate Administrative Services",
       contact_person="HR Generalist",
       problem_statement="New employees ask the same onboarding questions about benefits, systems access, and policies during their first weeks.",
       expected_outcome="Provide a self-serve onboarding assistant that answers common questions and links to the right forms.",
       ai_tool="Azure AI Search, Azure OpenAI",
       security_privacy="Protected A; grounded in approved onboarding material only.",
       lifecycle_phase=PHASES[0], status="New", data_classification="Protected A",
       solution_type="AI", business_value="Employee Experience",
       it_involvement="None", next_decision="Validate requirements", pia_trigger=True),
    _e(use_case_title="Staffing Process Helper",
       business_area="HR & Corporate Administrative Services",
       contact_person="Staffing Advisor",
       problem_statement="Hiring managers are unsure which staffing process and templates to use, leading to delays and back-and-forth with HR.",
       expected_outcome="Guide managers through the correct staffing path and surface the right templates automatically.",
       ai_tool="Power Automate, Azure OpenAI",
       security_privacy="Protected B; no candidate personal information processed.",
       lifecycle_phase=PHASES[1], status="Under Review", data_classification="Protected B",
       solution_type="Mixed", business_value="Operational Efficiency",
       it_involvement="Advisory", next_decision="Approve prototype", pia_trigger=True),

    # ── Knowledge & Search ────────────────────────────────────────────────
    _e(use_case_title="Internal Policy Search",
       business_area="Corporate Secretariat",
       contact_person="Policy Analyst",
       problem_statement="Staff struggle to find current policy and directive content scattered across SharePoint and shared drives.",
       expected_outcome="Provide semantic search over approved policies with cited sources.",
       ai_tool="Azure AI Search, Azure OpenAI embeddings",
       security_privacy="Protected A; results limited to approved, publishable policy.",
       lifecycle_phase=PHASES[2], status="In Pilot", data_classification="Protected A",
       solution_type="AI", business_value="Service Quality",
       it_involvement="Advisory", next_decision="Move to pilot"),
    _e(use_case_title="Program Guidance Finder",
       business_area="Regional Programs",
       contact_person="Program Officer",
       problem_statement="Officers spend time locating the right program guidance and eligibility rules for each funding stream.",
       expected_outcome="Answer program guidance questions with citations to the source documents.",
       ai_tool="Azure AI Search, retrieval-augmented generation",
       security_privacy="Protected A; grounded in approved program guidance.",
       lifecycle_phase=PHASES[1], status="In Prototype", data_classification="Protected A",
       solution_type="AI", business_value="Service Quality",
       it_involvement="Light Advisory", next_decision="Approve prototype"),
    _e(use_case_title="Briefing Note Drafter",
       business_area="Executive Office",
       contact_person="Executive Assistant",
       problem_statement="Drafting briefing notes from background material is repetitive and time-consuming for executive support staff.",
       expected_outcome="Produce first-draft briefing notes from supplied source material in the standard format.",
       ai_tool="Azure OpenAI, Microsoft 365 Copilot",
       security_privacy="Protected B; drafts reviewed and approved by humans before use.",
       lifecycle_phase=PHASES[0], status="New", data_classification="Protected B",
       solution_type="AI", business_value="Operational Efficiency",
       it_involvement="None", next_decision="Validate requirements"),

    # ── Analytics & Executive Insight ─────────────────────────────────────
    _e(use_case_title="AI Registry Idea Visualizer / Opportunity Pattern Graph",
       business_area="AI Adoption / Transformation / Enterprise Strategy",
       contact_person="AI Adoption Team",
       problem_statement="As AI ideas and prototypes are submitted across the organization, it is difficult for leadership to identify common themes, duplicated ideas, recurring pain points, and priority opportunities from a standard table alone.",
       expected_outcome="Create a centralized visual analytics layer that turns registry entries into a semantic idea graph so similar ideas cluster and larger nodes reveal recurring pain points and high-value opportunities.",
       ai_tool="AI Registry, semantic embeddings, clustering, Obsidian-style graph, Azure AI Search, Power BI",
       security_privacy="Entries should avoid sensitive personal or Protected B details unless approved; graph access role-based.",
       lifecycle_phase=PHASES[1], status="In Prototype", data_classification="Unclassified",
       solution_type="AI", business_value="Policy Delivery",
       it_involvement="Advisory", next_decision="Approve prototype",
       notes="Supports executive prioritization by revealing patterns across submitted AI ideas."),
    _e(use_case_title="Regional Economic Dashboard",
       business_area="Policy & Economic Analysis",
       contact_person="Economist",
       problem_statement="Regional economic indicators are compiled manually from many sources for executive reporting.",
       expected_outcome="Provide an automated dashboard of regional economic indicators refreshed on a schedule.",
       ai_tool="Power BI, Azure Data Factory",
       security_privacy="Unclassified open data; no personal information.",
       lifecycle_phase=PHASES[3], status="In Pilot", data_classification="Unclassified",
       solution_type="Dashboard", business_value="Policy Delivery",
       it_involvement="Full Involvement", next_decision="Move to pilot"),
    _e(use_case_title="Client Inquiry Pattern Analyzer",
       business_area="Client Services",
       contact_person="Service Manager",
       problem_statement="Leadership lacks visibility into the recurring themes behind client inquiries across regions.",
       expected_outcome="Cluster and trend client inquiries to reveal emerging issues for executive attention.",
       ai_tool="Azure OpenAI embeddings, clustering, Power BI",
       security_privacy="Protected B; aggregate analysis only, no identifiable client detail in reports.",
       lifecycle_phase=PHASES[1], status="Under Review", data_classification="Protected B",
       solution_type="AI", business_value="Service Quality",
       it_involvement="Advisory", next_decision="Approve prototype", pia_trigger=True),

    # ── Client Service Delivery ───────────────────────────────────────────
    _e(use_case_title="Client Intake Chatbot",
       business_area="Client Services",
       contact_person="Client Service Officer",
       problem_statement="Clients ask basic questions about programs and application steps through email and phone, creating high front-line volume.",
       expected_outcome="Deflect common client questions with a chatbot grounded in published program information.",
       ai_tool="Azure Bot Service, Azure OpenAI, Azure AI Search",
       security_privacy="Protected A; no collection of client personal information in the chat.",
       lifecycle_phase=PHASES[2], status="In Pilot", data_classification="Protected A",
       solution_type="AI", business_value="Service Quality",
       it_involvement="Advisory", next_decision="Move to pilot", aia_trigger=True, pia_trigger=True),
    _e(use_case_title="Application Status Notifier",
       business_area="Client Services",
       contact_person="Client Service Officer",
       problem_statement="Applicants frequently contact staff asking for the status of their application.",
       expected_outcome="Proactively notify applicants of status changes to reduce status-check inquiries.",
       ai_tool="Power Automate, Azure Functions",
       security_privacy="Protected B; notifications sent only to verified applicants.",
       lifecycle_phase=PHASES[0], status="New", data_classification="Protected B",
       solution_type="Automation", business_value="Employee Experience",
       it_involvement="Light Advisory", next_decision="Validate requirements", pia_trigger=True),
]


def seed(store, force: bool = False) -> int:
    """Seed the store with the dummy entries. Idempotent unless force=True."""
    existing = store.list_entries()
    if existing and not force:
        return 0
    count = 0
    for payload in ENTRIES:
        store.save_entry(payload)
        count += 1
    return count
