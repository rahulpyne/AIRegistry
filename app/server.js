// PacifiCan AI Registry — SurveyJS form server.
// Serves the static SurveyJS form and accepts submissions at POST /api/submit,
// reshaping the flat survey result into the nested document described in
// docs/intake-fields.md and inserting it into Cosmos DB (MongoDB API).

const path = require("path");
const express = require("express");
const { MongoClient } = require("mongodb");

const app = express();
app.use(express.json({ limit: "1mb" }));
app.use(express.static(path.join(__dirname, "public")));

const PORT = process.env.PORT || 8080;
const CONN = process.env.COSMOS_MONGO_CONNECTION_STRING || "";
const DB_NAME = process.env.COSMOS_DB_NAME || "airegistry";
const COLLECTION = process.env.COSMOS_COLLECTION || "registry_entries";

// --- Cosmos (Mongo API) connection, lazily established and reused ---
let clientPromise = null;
function getCollection() {
  if (!CONN) throw new Error("COSMOS_MONGO_CONNECTION_STRING is not set");
  if (!clientPromise) {
    clientPromise = new MongoClient(CONN, { maxPoolSize: 5 }).connect();
  }
  return clientPromise.then((c) => c.db(DB_NAME).collection(COLLECTION));
}

// Turn flat SurveyJS keys ("a__b__c") into nested objects ({a:{b:{c:...}}}).
function unflatten(flat) {
  const out = {};
  for (const [key, value] of Object.entries(flat || {})) {
    const parts = key.split("__");
    let cur = out;
    for (let i = 0; i < parts.length - 1; i++) {
      if (typeof cur[parts[i]] !== "object" || cur[parts[i]] === null) cur[parts[i]] = {};
      cur = cur[parts[i]];
    }
    cur[parts[parts.length - 1]] = value;
  }
  return out;
}

app.get("/healthz", (_req, res) => res.json({ ok: true }));

app.post("/api/submit", async (req, res) => {
  try {
    const data = req.body && typeof req.body === "object" ? req.body : {};
    if (!Object.keys(data).length) return res.status(400).json({ error: "Empty submission" });

    const doc = {
      submitted_at: new Date().toISOString(),
      schema_version: 1,
      aia_status: "captured",
      ...unflatten(data),
    };

    const col = await getCollection();
    const result = await col.insertOne(doc);
    res.json({ id: result.insertedId, submitted_at: doc.submitted_at });
  } catch (err) {
    console.error("submit failed:", err.message);
    res.status(500).json({ error: "Could not save submission" });
  }
});

app.listen(PORT, () => console.log(`AI Registry form listening on ${PORT}`));
