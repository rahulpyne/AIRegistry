"""
AI Registry — Flask application.

Three sections:
    /form                       Section 1  AI Registry Form (capture -> store)
    /graph                      Section 2  Idea Visualizer (semantic graph)
    /lifecycle/<entry_id>       Section 3  AI Operating Lifecycle board

JSON APIs back the pages. Storage is pluggable (Supabase primary, local JSON
fallback) via storage.get_store().
"""
import os
import logging
from pathlib import Path

from flask import (Flask, request, jsonify, render_template,
                   redirect, url_for, send_from_directory, abort)
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

import storage
import graph_builder
import lifecycle
import seed_data

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # 25 MB uploads
app.config["TEMPLATES_AUTO_RELOAD"] = True

UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "./uploads")
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

store = storage.get_store()

if os.environ.get("SEED_ON_START", "1") == "1":
    try:
        n = seed_data.seed(store)
        if n:
            logger.info("Seeded %d dummy registry entries", n)
    except Exception:
        logger.exception("Seeding failed (continuing)")

# Form choices (from AI_Registry_Form_Template.docx, Table 1).
CHOICES = {
    "lifecycle_phase": [
        "1 · Experiment & Innovate", "2 · Prototype & Validate", "3 · Pilot & Test",
        "4 · Build & Scale", "5 · Production & Operate",
    ],
    "status": ["New", "Under Review", "In Prototype", "In Pilot", "Parked", "Retired", "Production"],
    "data_classification": ["Unclassified", "Protected A", "Protected B", "Protected C", "Unknown"],
    "solution_type": ["AI", "Automation", "Dashboard", "Process Redesign", "Training", "Mixed"],
    "business_value": ["Service Quality", "Operational Efficiency", "Risk Reduction",
                       "Employee Experience", "Policy Delivery", "Financial Stewardship"],
    "it_involvement": ["None", "Light Advisory", "Advisory", "Full Involvement"],
    "next_decision": ["Validate requirements", "Approve prototype", "Security review",
                      "Move to pilot", "Stop or park"],
}

REQUIRED_FIELDS = [
    "use_case_title", "rda_organization", "business_area", "contact_person",
    "problem_statement", "expected_outcome", "ai_tool", "security_privacy",
]


# ── Pages ──────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return redirect(url_for("graph_page"))


@app.route("/form")
def form_page():
    return render_template("form.html", choices=CHOICES)


@app.route("/entries")
def entries_page():
    return render_template("entries.html", entries=store.list_entries())


@app.route("/graph")
def graph_page():
    return render_template("graph.html")


@app.route("/lifecycle/")
@app.route("/lifecycle/<entry_id>")
def lifecycle_page(entry_id=None):
    entries = store.list_entries()
    if not entry_id:
        if not entries:
            return render_template("lifecycle.html", entry=None, board=None, entries=[])
        entry_id = entries[0]["id"]
    entry = store.get_entry(entry_id)
    if not entry:
        abort(404)
    board = lifecycle.build_board(entry,
                                  store.list_documents(entry_id),
                                  store.list_approvals(entry_id))
    return render_template("lifecycle.html", entry=entry, board=board, entries=entries)


# ── APIs ───────────────────────────────────────────────────────────────────
@app.route("/api/registry", methods=["POST"])
def api_registry():
    data = request.get_json(silent=True) or request.form.to_dict()
    missing = [f for f in REQUIRED_FIELDS if not str(data.get(f, "")).strip()]
    if missing:
        return jsonify({"success": False, "error": f"Missing required fields: {', '.join(missing)}"}), 400

    payload = {k: data.get(k, "") for k in (
        *REQUIRED_FIELDS, "notes", "lifecycle_phase", "status",
        "data_classification", "solution_type", "business_value",
        "it_involvement", "next_decision",
    )}
    payload["aia_trigger"] = str(data.get("aia_trigger", "")).lower() in ("1", "true", "on", "yes")
    payload["pia_trigger"] = str(data.get("pia_trigger", "")).lower() in ("1", "true", "on", "yes")

    record = store.save_entry(payload)
    return jsonify({"success": True, "id": record["id"]})


@app.route("/api/graph")
def api_graph():
    return jsonify(graph_builder.build_graph(store.list_entries()))


@app.route("/api/entries/<entry_id>/documents", methods=["POST"])
def api_upload_document(entry_id):
    if not store.get_entry(entry_id):
        return jsonify({"success": False, "error": "Unknown entry"}), 404
    f = request.files.get("file")
    phase = int(request.form.get("phase", 0))
    artifact = request.form.get("artifact", "")
    if not f or not f.filename:
        return jsonify({"success": False, "error": "No file provided"}), 400
    if not phase or not artifact:
        return jsonify({"success": False, "error": "phase and artifact are required"}), 400

    safe = secure_filename(f.filename)
    dest_dir = Path(UPLOAD_FOLDER) / entry_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    rel_path = f"{entry_id}/{safe}"
    f.save(str(dest_dir / safe))

    record = store.save_document(entry_id, phase, artifact, safe, rel_path)
    return jsonify({"success": True, "document": record})


@app.route("/api/documents/<doc_id>", methods=["PATCH"])
def api_update_document(doc_id):
    data = request.get_json(force=True)
    status = data.get("status", "")
    if status not in ("UPLOADED", "IN-REVIEW", "APPROVED"):
        return jsonify({"success": False, "error": "Invalid status"}), 400
    record = store.update_document_status(doc_id, status)
    if not record:
        return jsonify({"success": False, "error": "Unknown document"}), 404
    return jsonify({"success": True, "document": record})


@app.route("/api/entries/<entry_id>/approvals", methods=["PATCH"])
def api_set_approval(entry_id):
    if not store.get_entry(entry_id):
        return jsonify({"success": False, "error": "Unknown entry"}), 404
    data = request.get_json(force=True)
    phase = int(data.get("phase", 0))
    team = data.get("team", "").upper()
    status = data.get("status", "").upper()
    approver = data.get("approver", "")
    if team not in ("BUSINESS", "IT") or status not in ("PENDING", "APPROVED") or not phase:
        return jsonify({"success": False, "error": "phase, team(BUSINESS|IT), status(PENDING|APPROVED) required"}), 400
    record = store.set_approval(entry_id, phase, team, status, approver)
    return jsonify({"success": True, "approval": record})


@app.route("/uploads/<path:rel_path>")
def serve_upload(rel_path):
    return send_from_directory(UPLOAD_FOLDER, rel_path)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)
