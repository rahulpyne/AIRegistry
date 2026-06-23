"""
Idea Visualizer graph builder.

Turns the set of AI Registry entries into an Obsidian-style, 3-level
hierarchical graph:

    category  (big node)   recurring / generic theme
      └─ subcategory       a tighter sub-theme within the category
           └─ idea         an individual registry entry (leaf)

Node size scales with the number of ideas underneath it; colour encodes the
top-level category. The whole graph is recomputed from the current entries on
every request, so it adapts as new ideas arrive.

Now: local TF-IDF + agglomerative clustering (no external services, no keys).
Later (Azure): replace `_vectorize` with Azure OpenAI embeddings and the
clustering with vectors stored in Azure AI Search — the rest is unchanged.
"""
from __future__ import annotations

import re
import math

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering

# Colour palette for top-level categories.
_PALETTE = [
    "#5B8DEF", "#3FB6A8", "#E0A23B", "#E0743B",
    "#B5539C", "#7E57C2", "#26A69A", "#EC407A",
]

_STOP_EXTRA = {
    "ai", "use", "using", "used", "tool", "tools", "application", "applications",
    "data", "team", "teams", "staff", "employee", "employees", "pacifican",
    "rda", "program", "programs", "system", "process", "processes", "idea",
    "ideas", "solution", "support", "across", "internal", "new", "based",
}


def _entry_text(entry: dict) -> str:
    p = entry.get("payload", entry)
    parts = [
        p.get("problem_statement", ""),
        p.get("expected_outcome", ""),
        p.get("business_area", ""),
        p.get("use_case_title", "") or p.get("title", ""),
    ]
    return " ".join(str(x) for x in parts if x)


def _entry_title(entry: dict) -> str:
    p = entry.get("payload", entry)
    return p.get("use_case_title") or p.get("title") or entry.get("id", "Untitled")


def _vectorize(texts: list[str]):
    """TF-IDF vectors + the fitted vectorizer (swap-point for Azure embeddings)."""
    vec = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1,
        max_features=400,
    )
    matrix = vec.fit_transform(texts)
    return matrix, vec


def _cluster(matrix, n_clusters: int) -> np.ndarray:
    n_samples = matrix.shape[0]
    n_clusters = max(1, min(n_clusters, n_samples))
    if n_clusters == 1 or n_samples == 1:
        return np.zeros(n_samples, dtype=int)
    model = AgglomerativeClustering(n_clusters=n_clusters, metric="cosine", linkage="average")
    return model.fit_predict(matrix.toarray())


def _label_for(indices: list[int], matrix, vocab, max_terms: int = 2) -> str:
    """Human-ish label from the highest mean TF-IDF terms of a cluster."""
    sub = matrix[indices].toarray().mean(axis=0)
    ranked = np.argsort(sub)[::-1]
    terms = []
    for i in ranked:
        term = vocab[i]
        if sub[i] <= 0:
            break
        if term in _STOP_EXTRA or any(term in t or t in term for t in terms):
            continue
        terms.append(term)
        if len(terms) >= max_terms:
            break
    if not terms:
        return "General"
    return " / ".join(t.title() for t in terms)


def build_graph(entries: list[dict]) -> dict:
    """Return Cytoscape elements: {"nodes": [...], "edges": [...]}."""
    entries = [e for e in entries if _entry_text(e).strip()]
    nodes: list[dict] = []
    edges: list[dict] = []

    if not entries:
        return {"nodes": [], "edges": [], "stats": {"entries": 0, "categories": 0}}

    texts = [_entry_text(e) for e in entries]
    matrix, vec = _vectorize(texts)
    vocab = vec.get_feature_names_out()

    n = len(entries)
    # heuristics: ~one category per 3 ideas, bounded; subcats split within.
    n_cat = max(1, min(round(math.sqrt(n)), 6))
    cat_labels = _cluster(matrix, n_cat)

    for ci in sorted(set(cat_labels)):
        cat_idx = [i for i, c in enumerate(cat_labels) if c == ci]
        color = _PALETTE[ci % len(_PALETTE)]
        cat_id = f"cat-{ci}"
        cat_name = _label_for(cat_idx, matrix, vocab, max_terms=2)
        nodes.append({
            "data": {"id": cat_id, "label": cat_name, "level": "category",
                     "color": color, "size": 30 + 9 * len(cat_idx),
                     "count": len(cat_idx)},
        })

        # sub-cluster within the category
        n_sub = max(1, min(round(len(cat_idx) / 2), 4)) if len(cat_idx) > 2 else 1
        sub_matrix = matrix[cat_idx]
        sub_labels = _cluster(sub_matrix, n_sub)

        for si in sorted(set(sub_labels)):
            members_local = [cat_idx[j] for j, s in enumerate(sub_labels) if s == si]
            sub_id = f"sub-{ci}-{si}"
            sub_name = _label_for(members_local, matrix, vocab, max_terms=2)
            nodes.append({
                "data": {"id": sub_id, "label": sub_name, "level": "subcategory",
                         "color": color, "size": 18 + 6 * len(members_local),
                         "count": len(members_local)},
            })
            edges.append({"data": {"id": f"e-{cat_id}-{sub_id}",
                                   "source": cat_id, "target": sub_id}})

            for idx in members_local:
                entry = entries[idx]
                leaf_id = entry.get("id", f"idea-{idx}")
                nodes.append({
                    "data": {"id": leaf_id, "label": _entry_title(entry),
                             "level": "idea", "color": color, "size": 12,
                             "entry_id": entry.get("id", ""),
                             "business_area": entry.get("payload", entry).get("business_area", "")},
                })
                edges.append({"data": {"id": f"e-{sub_id}-{leaf_id}",
                                       "source": sub_id, "target": leaf_id}})

    return {
        "nodes": nodes,
        "edges": edges,
        "stats": {"entries": n, "categories": len(set(cat_labels))},
    }
