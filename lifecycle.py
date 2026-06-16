"""
AI Operating Lifecycle model — encoded verbatim from
PMP_AI_Operating_Framework.docx (PacifiCan, Strategy Framework for AI).

Provides:
    PHASES        - the 5 lifecycle phases (objective, IT involvement, data
                    classification, exit criteria) + a distinct colour each.
    ARTIFACTS     - the artifact map (artifact x phase requirement level),
                    including the AIA and PIA rows.
    GATES         - the AIA & PIA gate conditions between phases (§4.2).
    TEMPLATE_LINKS- per-artifact template links surfaced on the board.

build_board(entry, documents, approvals) assembles the per-entry view the
Lifecycle page renders.
"""
from __future__ import annotations

# Phase number -> metadata. Colours chosen to read as a cool→warm progression.
PHASES = {
    1: {"name": "Experiment & Innovate",
        "objective": "Encourage discovery, informal experimentation, idea generation.",
        "it_involvement": "None",
        "data_classification": "Unclassified / public, non-sensitive only",
        "exit_criteria": "Idea inventoried; initial problem and potential value described.",
        "color": "#5B8DEF"},
    2: {"name": "Prototype & Validate",
        "objective": "Structured proof of concept to test feasibility and value with a small group.",
        "it_involvement": "Light advisory if requested",
        "data_classification": "Non-sensitive; Protected B only if environment approved",
        "exit_criteria": "Validated value proposition; initial risk profile; data & integration scope identified.",
        "color": "#3FB6A8"},
    3: {"name": "Pilot & Test",
        "objective": "Test with a larger group and realistic workflows.",
        "it_involvement": "Advisory & light involvement",
        "data_classification": "Up to Protected B with controls",
        "exit_criteria": "User value, risk controls, performance, and operating needs validated.",
        "color": "#E0A23B"},
    4: {"name": "Build & Scale",
        "objective": "Develop a scalable, supportable solution with production architecture and governance.",
        "it_involvement": "Full involvement",
        "data_classification": "Up to Protected B with approved controls",
        "exit_criteria": "Build approach approved; funding, ownership, operations model confirmed.",
        "color": "#E0743B"},
    5: {"name": "Production & Operate",
        "objective": "Operate, monitor, support, and continuously improve.",
        "it_involvement": "Full involvement",
        "data_classification": "As approved by security/privacy authority",
        "exit_criteria": "Solution operationalized with support, monitoring, governance, lifecycle management.",
        "color": "#B5539C"},
}

# Artifact map (PMP §5). Per-phase requirement level per artifact.
# Level vocabulary kept exactly as the document uses it.
ARTIFACTS = [
    {"name": "AI Registry Form",                "key": "ai_registry_form",
     "levels": {1: "Required", 2: "Required", 3: "Required", 4: "Required", 5: "Required"}},
    {"name": "PRD",                             "key": "prd",
     "levels": {1: "Optional", 2: "Required", 3: "Updated", 4: "Updated", 5: "Reference"}},
    {"name": "Experiment Brief",                "key": "experiment_brief",
     "levels": {1: "Optional", 2: "Required", 3: "Updated", 4: "Reference", 5: "Reference"}},
    {"name": "Risk & Data Classification Note", "key": "risk_note",
     "levels": {1: "Optional", 2: "Initial", 3: "Required", 4: "Required", 5: "Maintained"}},
    {"name": "Algorithmic Impact Assessment (AIA)", "key": "aia", "gov": True,
     "levels": {1: "Pre-screen", 2: "Draft", 3: "Complete", 4: "Final / Published", 5: "Maintained"}},
    {"name": "Privacy Impact Assessment (PIA)", "key": "pia", "gov": True,
     "levels": {1: "Trigger Qs", 2: "Threshold", 3: "Full PIA", 4: "Controls + sign-off", 5: "Evergreen"}},
    {"name": "Evaluation Plan",                 "key": "evaluation_plan",
     "levels": {1: "Optional", 2: "Initial", 3: "Required", 4: "Required", 5: "Maintained"}},
    {"name": "Architecture / Technical Design", "key": "architecture",
     "levels": {1: "Not required", 2: "Lightweight", 3: "Draft", 4: "Required", 5: "Maintained"}},
    {"name": "Operational Readiness Plan",      "key": "ops_readiness",
     "levels": {1: "Not required", 2: "Not required", 3: "Draft", 4: "Required", 5: "Maintained"}},
]

# Requirement levels that mean "an actual document/upload is expected this phase".
_UPLOAD_LEVELS = {
    "Required", "Updated", "Initial", "Draft", "Complete", "Final / Published",
    "Threshold", "Full PIA", "Controls + sign-off", "Lightweight", "Maintained",
    "Pre-screen", "Trigger Qs",
}

# Template links per artifact (configurable; point to canonical templates).
TEMPLATE_LINKS = {
    "ai_registry_form": "/form",
    "prd": "https://canada.ca — PacifiCan Strategy Framework for AI (PRD template)",
    "experiment_brief": "https://canada.ca — Experiment Brief template",
    "risk_note": "https://canada.ca — Risk & Data Classification Note",
    "aia": "https://www.canada.ca/en/government/system/digital-government/digital-government-innovations/responsible-use-ai/algorithmic-impact-assessment.html",
    "pia": "https://www.canada.ca/en/government/system/digital-government/digital-privacy-playbook/privacy-impact-assessments.html",
    "evaluation_plan": "https://canada.ca — Evaluation Plan template",
    "architecture": "https://canada.ca — Architecture / Technical Design template",
    "ops_readiness": "https://canada.ca — Operational Readiness Plan template",
}

# AIA & PIA gates between phases (PMP §4.2).
GATES = [
    {"between": "2 → 3",
     "condition": "Draft AIA and PIA threshold analysis exist; impact level estimated; privacy risks identified."},
    {"between": "3 → 4",
     "condition": "AIA completed and full PIA approved by privacy/ATIP officials; mitigations agreed."},
    {"between": "4 → 5",
     "condition": "Final AIA published; PIA-mandated controls implemented and signed off; recourse, notice, and training in place."},
    {"between": "In-operation",
     "condition": "AIA and PIA reviewed on material change and on a fixed cadence as part of monthly portfolio and lifecycle gate reviews."},
]

# Which teams' approval each phase gate needs (Business always; IT from pilot on).
PHASE_APPROVERS = {
    1: ["BUSINESS"],
    2: ["BUSINESS"],
    3: ["BUSINESS", "IT"],
    4: ["BUSINESS", "IT"],
    5: ["BUSINESS", "IT"],
}


def artifacts_for_phase(phase: int) -> list[dict]:
    """Artifacts relevant in a phase, with level + whether an upload is expected."""
    out = []
    for art in ARTIFACTS:
        level = art["levels"].get(phase, "Not required")
        out.append({
            "name": art["name"],
            "key": art["key"],
            "level": level,
            "gov": art.get("gov", False),
            "expects_upload": level in _UPLOAD_LEVELS,
            "template_link": TEMPLATE_LINKS.get(art["key"], ""),
        })
    return out


def build_board(entry: dict, documents: list[dict], approvals: list[dict]) -> dict:
    """Assemble the per-entry lifecycle board the template renders."""
    current_phase = _phase_number(entry)

    # index docs by (phase, artifact_key) and approvals by (phase, team)
    doc_index: dict[tuple[int, str], list] = {}
    for d in documents:
        doc_index.setdefault((int(d["phase"]), d["artifact"]), []).append(d)
    appr_index = {(int(a["phase"]), a["team"]): a for a in approvals}

    phases = []
    for n, meta in PHASES.items():
        arts = artifacts_for_phase(n)
        for a in arts:
            a["documents"] = doc_index.get((n, a["key"]), [])
        approvals_for_phase = []
        for team in PHASE_APPROVERS[n]:
            rec = appr_index.get((n, team))
            approvals_for_phase.append({
                "team": team,
                "status": (rec or {}).get("status", "PENDING"),
                "approver": (rec or {}).get("approver", ""),
            })
        phases.append({
            "number": n,
            **meta,
            "is_current": n == current_phase,
            "artifacts": arts,
            "approvals": approvals_for_phase,
        })

    return {"phases": phases, "gates": GATES, "current_phase": current_phase}


# Map the registry form's lifecycle-phase label to a phase number.
_PHASE_BY_LABEL = {meta["name"]: n for n, meta in PHASES.items()}


def _phase_number(entry: dict) -> int:
    payload = entry.get("payload", entry)
    label = (payload.get("lifecycle_phase") or "").strip()
    # labels may arrive as "1 · Experiment & Innovate" or just the name
    for name, n in _PHASE_BY_LABEL.items():
        if name in label:
            return n
    if label and label[0].isdigit():
        try:
            return int(label[0])
        except ValueError:
            pass
    return 1
