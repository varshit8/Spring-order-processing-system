import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from app.model import MODEL_VERSION, classify_prediction, score_prediction
from app.rag import build_grounded_answer, extract_action_items, rag_store, summarize_document
from app.schemas import (
    AgentRequest,
    AgentResponse,
    ChatRequest,
    ChatResponse,
    DocumentIngestRequest,
    DocumentIngestResponse,
    DocumentSummary,
    PredictionRequest,
    PredictionResponse,
    SearchRequest,
    SearchResponse,
)
from app.validation import evaluate_validation_report, generate_validation_report, load_records

app = FastAPI(
    title="ML Validation and AI Knowledge Assistant Platform",
    version="0.1.0",
    description="Starter ML validation API with local RAG knowledge assistant endpoints.",
)

ENVIRONMENT_CONFIG_PATH = Path("data/environments/config.json")


def load_environment_config() -> dict:
    with ENVIRONMENT_CONFIG_PATH.open(encoding="utf-8") as config_file:
        return json.load(config_file)


def build_dashboard_html() -> str:
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ML Validation Dashboard</title>
  <style>
    :root {
      --bg: #f2efe8;
      --panel: #fffdf8;
      --ink: #1f2a37;
      --accent: #0f766e;
      --accent-2: #d97706;
      --danger: #b91c1c;
      --border: #d8d0c2;
    }
    body {
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      background:
        radial-gradient(circle at top left, #fdf3d3 0, transparent 30%),
        linear-gradient(135deg, #f4efe6 0%, #ebe5d7 100%);
      color: var(--ink);
    }
    .wrap {
      max-width: 1120px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }
    .hero {
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 20px;
      margin-bottom: 24px;
    }
    .panel {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 20px;
      box-shadow: 0 16px 40px rgba(31, 42, 55, 0.08);
    }
    h1, h2, h3 {
      margin: 0 0 12px;
      font-weight: 700;
    }
    h1 {
      font-size: 2.2rem;
      line-height: 1.05;
    }
    p {
      margin: 0 0 12px;
      line-height: 1.5;
    }
    .pill {
      display: inline-block;
      padding: 6px 12px;
      border-radius: 999px;
      background: #e7f7f4;
      color: var(--accent);
      font-size: 0.9rem;
      margin-bottom: 10px;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
    }
    label {
      display: block;
      font-size: 0.92rem;
      margin-bottom: 6px;
    }
    input, select, button, textarea {
      width: 100%;
      box-sizing: border-box;
      border-radius: 12px;
      border: 1px solid var(--border);
      padding: 12px 14px;
      font: inherit;
      background: #fff;
    }
    button {
      background: var(--ink);
      color: #fff;
      border: none;
      cursor: pointer;
      transition: transform 0.15s ease, opacity 0.15s ease;
    }
    button:hover {
      opacity: 0.95;
      transform: translateY(-1px);
    }
    .secondary {
      background: var(--accent);
    }
    .env-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-top: 16px;
    }
    .env-card {
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 16px;
      background: linear-gradient(180deg, #fffefb 0%, #f8f3ea 100%);
    }
    .status-pass { color: var(--accent); }
    .status-fail { color: var(--danger); }
    pre {
      white-space: pre-wrap;
      word-break: break-word;
      background: #faf6ee;
      border-radius: 14px;
      padding: 14px;
      border: 1px solid var(--border);
      overflow-x: auto;
    }
    .row {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      margin-top: 12px;
    }
    .row > * {
      flex: 1;
    }
    @media (max-width: 800px) {
      .hero {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <section class="panel">
        <div class="pill">Interactive Demo</div>
        <h1>ML Validation Dashboard</h1>
        <p>Explore prediction behavior, check active model version, and inspect drift status across dev, qa, and prod from one place.</p>
        <div class="row">
          <div class="panel" style="padding: 14px;">
            <h3>Health</h3>
            <div id="healthStatus">Loading...</div>
          </div>
          <div class="panel" style="padding: 14px;">
            <h3>Readiness</h3>
            <div id="readyStatus">Loading...</div>
          </div>
        </div>
      </section>
      <section class="panel">
        <h2>Manual Prediction</h2>
        <div class="grid">
          <div>
            <label for="age">Age</label>
            <input id="age" type="number" value="51" min="0" max="120" />
          </div>
          <div>
            <label for="bmi">BMI</label>
            <input id="bmi" type="number" value="32.8" step="0.1" min="10" max="80" />
          </div>
          <div>
            <label for="glucose">Glucose</label>
            <input id="glucose" type="number" value="158" min="40" max="500" />
          </div>
          <div>
            <label for="bloodPressure">Blood Pressure</label>
            <input id="bloodPressure" type="number" value="96" min="40" max="250" />
          </div>
        </div>
        <div class="row">
          <button onclick="runPrediction()">Run Prediction</button>
        </div>
        <pre id="predictionOutput">Prediction output will appear here.</pre>
      </section>
    </div>

    <section class="panel">
      <h2>Environment Validation</h2>
      <p>These cards call the backend validation endpoint and summarize drift behavior for each environment-specific dataset.</p>
      <div class="env-grid" id="environmentCards"></div>
    </section>
  </div>

  <script>
    async function fetchJson(url, options) {
      const response = await fetch(url, options);
      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }
      return response.json();
    }

    async function loadStatus() {
      const health = await fetchJson('/health');
      const ready = await fetchJson('/ready');
      document.getElementById('healthStatus').textContent = `${health.status} (${health.service})`;
      document.getElementById('readyStatus').textContent = `${ready.status} | ${ready.model_version}`;
    }

    async function runPrediction() {
      const payload = {
        age: Number(document.getElementById('age').value),
        bmi: Number(document.getElementById('bmi').value),
        glucose: Number(document.getElementById('glucose').value),
        blood_pressure: Number(document.getElementById('bloodPressure').value)
      };

      try {
        const result = await fetchJson('/predict', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        document.getElementById('predictionOutput').textContent = JSON.stringify(result, null, 2);
      } catch (error) {
        document.getElementById('predictionOutput').textContent = error.message;
      }
    }

    async function loadEnvironment(environment) {
      const card = document.getElementById(`env-${environment}`);
      card.innerHTML = 'Loading...';
      try {
        const result = await fetchJson(`/validation/${environment}`);
        const statusClass = result.status === 'PASSED' ? 'status-pass' : 'status-fail';
        card.innerHTML = `
          <h3>${environment.toUpperCase()}</h3>
          <p class="${statusClass}"><strong>${result.status}</strong></p>
          <p>Model version: ${result.model_version}</p>
          <p>Average risk score: ${result.average_risk_score}</p>
          <p>Drift detected: ${result.drift_detected}</p>
          <p>Drifted features: ${result.drifted_features.length ? result.drifted_features.join(', ') : 'None'}</p>
        `;
      } catch (error) {
        card.innerHTML = `<p class="status-fail">${error.message}</p>`;
      }
    }

    function createEnvironmentCards() {
      const environments = ['dev', 'qa', 'prod'];
      const container = document.getElementById('environmentCards');
      container.innerHTML = environments.map(env => `<div class="env-card" id="env-${env}"></div>`).join('');
      environments.forEach(loadEnvironment);
    }

    loadStatus();
    createEnvironmentCards();
  </script>
</body>
</html>
"""


@app.get("/health")
def healthcheck() -> dict:
    return {"status": "ok", "service": "ml-inference-api"}


@app.get("/ready")
def readiness() -> dict:
    return {"status": "ready", "model_version": MODEL_VERSION}


@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    return build_dashboard_html()


@app.get("/validation/{environment}")
def validation_environment(environment: str) -> dict:
    config = load_environment_config()
    if environment not in config:
        raise HTTPException(status_code=404, detail="Unknown environment")

    environment_config = config[environment]
    reference_records = load_records(environment_config["reference"])
    candidate_records = load_records(environment_config["candidate"])
    report = generate_validation_report(reference_records, candidate_records)
    evaluation = evaluate_validation_report(
        report,
        fail_on_drift=environment_config["fail_on_drift"],
        max_drifted_features=environment_config["max_drifted_features"],
    )
    return {
        "environment": environment,
        "model_version": report["model_version"],
        "drift_detected": report["drift_detected"],
        "drifted_features": evaluation["drifted_features"],
        "average_risk_score": report["candidate_prediction_summary"]["average_risk_score"],
        "status": "FAILED" if evaluation["should_fail"] else "PASSED",
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest) -> PredictionResponse:
    score = score_prediction(payload)
    prediction = classify_prediction(score)
    return PredictionResponse(
        risk_score=score,
        prediction=prediction,
        model_version=MODEL_VERSION,
        validation_status="passed",
    )


@app.post("/documents", response_model=DocumentIngestResponse)
def ingest_document(payload: DocumentIngestRequest) -> DocumentIngestResponse:
    document = rag_store.ingest(
        filename=payload.filename,
        content=payload.content,
        source_type=payload.source_type,
    )
    return DocumentIngestResponse(
        document_id=document.document_id,
        filename=document.filename,
        chunk_count=len(document.chunk_ids),
        status="indexed",
    )


@app.get("/documents", response_model=list[DocumentSummary])
def list_documents() -> list[DocumentSummary]:
    return [
        DocumentSummary(
            document_id=document.document_id,
            filename=document.filename,
            source_type=document.source_type,
            chunk_count=len(document.chunk_ids),
        )
        for document in rag_store.list_documents()
    ]


@app.post("/search", response_model=SearchResponse)
def search_documents(payload: SearchRequest) -> SearchResponse:
    citations = rag_store.search(payload.query, top_k=payload.top_k)
    return SearchResponse(query=payload.query, citations=citations)


@app.post("/chat", response_model=ChatResponse)
def chat_with_documents(payload: ChatRequest) -> ChatResponse:
    citations = rag_store.search(payload.question, top_k=payload.top_k)
    return ChatResponse(
        answer=build_grounded_answer(payload.question, citations),
        citations=citations,
        retrieval_mode="local_keyword_rag",
    )


@app.post("/agents/summarize", response_model=AgentResponse)
def summarize_document_agent(payload: AgentRequest) -> AgentResponse:
    document = rag_store.get_document(payload.document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    citations = rag_store.search(document.filename, top_k=1, document_id=document.document_id)
    if not citations and document.chunk_ids:
        first_chunk = rag_store.chunks[document.chunk_ids[0]]
        citations = rag_store.search(first_chunk.text, top_k=1, document_id=document.document_id)

    return AgentResponse(
        document_id=document.document_id,
        result=summarize_document(document),
        citations=citations,
    )


@app.post("/agents/extract-actions", response_model=AgentResponse)
def extract_actions_agent(payload: AgentRequest) -> AgentResponse:
    document = rag_store.get_document(payload.document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    citations = rag_store.search("must should required action owner todo", top_k=3, document_id=document.document_id)
    return AgentResponse(
        document_id=document.document_id,
        result=extract_action_items(document),
        citations=citations,
    )
