# BidAi — Public Tender Specification Analysis Assistant

An **agentic AI assistant** that reads Turkish public tender specifications (*ihale şartnameleri*) and gives bidders a structured summary, a prioritized risk analysis, and source-cited Q&A — with retrieval, observability and automated evaluation.

**🚀 Live Demo:** https://bidai-69768111605.europe-west1.run.app/docs
**Stack:** Python · FastAPI · Anthropic Claude · LangGraph · Chroma · sentence-transformers · Pydantic · Langfuse · RAGAS · Docker · GCP Cloud Run

## Problem

Public tender specifications are long and complex; companies must analyze them carefully before bidding. Manually extracting risks, eligibility criteria and guarantee rates is slow and error-prone — and a single missed clause can mean disqualification or unexpected cost. BidAi automates that analysis, producing structured information, risk assessments and source-cited answers from the document.

## Features

- **Structured Extraction** — Extracts guarantee rates, eligibility criteria, penalty clauses etc. as schema-validated JSON (Pydantic). Missing fields return `null` instead of hallucinated values.
- **Risk Analysis** — Translates the specification into bidder-facing risks (elimination, cost, cash-flow, timeline), prioritized and source-cited.
- **RAG Q&A** — Free-form questions answered from the document; relevant clauses retrieved from a **Chroma vector database** and cited.
- **Agentic Advisor (`/danis`)** — A **LangGraph** multi-tool agent that, from a single open-ended question, orchestrates extraction, risk analysis, guarantee calculation and clause retrieval, then synthesizes a recommendation.

## Architecture

```
Document → Parsing → Extraction (Claude + Pydantic schema)
                           ↓
   Question → Embedding → Chroma retrieval → Claude generation (cited answer)
                           ↓
        Agent (LangGraph) orchestrates tools:
        [ozet_cikar · risk_analiz · teminat_hesapla · madde_ara]
                           ↓
         FastAPI REST layer  ·  Langfuse tracing  ·  RAGAS evaluation
```

- **Structured output:** Claude output is validated against Pydantic schemas — the prompt improves quality, the schema *guarantees* structure. All fields are `Optional`, so absent data returns `null` (verified by negative tests).
- **Retrieval:** Clauses are embedded with sentence-transformers and stored in **Chroma**; queries retrieve the most relevant clauses.
- **Agent:** Existing functions are exposed as tools; a LangGraph ReAct agent decides which to call. Deterministic structured endpoints are kept for machine/precise use — the agent is added only for open-ended queries.
- **Design:** Protocol-based dependency injection (`LLMClient` / `EmbeddingClient`); the heavy embedding model loads once as a singleton.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI |
| LLM | Anthropic Claude |
| Agent orchestration | LangGraph |
| Vector DB / RAG | Chroma, sentence-transformers |
| Validation | Pydantic |
| Observability | Langfuse (LLM tracing) |
| Evaluation | RAGAS (faithfulness, context precision/recall) |
| Container / Deploy | Docker, GCP Cloud Run |
| CI/CD | GitHub Actions + Workload Identity Federation (keyless) |

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Health check |
| POST | `/ozet` | Document → structured summary (JSON) |
| POST | `/risk` | Document → risk report (JSON) |
| POST | `/soru` | Document file + question → source-cited RAG answer |
| POST | `/danis` | Document file + open-ended question → agentic advisory (multi-tool) |

## Getting Started (local)

```bash
git clone https://github.com/leventburcali/BidAi.git
cd BidAi
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env

uvicorn app.api.main:app --reload
# open http://localhost:8000/docs
```

## Observability (Langfuse)

Every agent run is traced to Langfuse — tool calls, latency, token usage and cost — set `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST` to enable.
> Note: on Cloud Run, `--no-cpu-throttling` is required so the async trace export can flush after the response returns.

## Evaluation (RAGAS)

RAG quality is measured automatically (`eval/ragas_eval.py`): a golden set of questions + references runs through the pipeline, then RAGAS scores **faithfulness**, **context precision** and **context recall**. Claude is used as the evaluator (judge) LLM. This surfaces actionable findings — e.g. high recall but lower precision points to retrieval noise to fix with better chunking.

## Deployment

Containerized and deployed to **GCP Cloud Run** via a **GitHub Actions** pipeline using **Workload Identity Federation** (keyless auth — no service-account keys). Push to `main` → build → deploy:

```bash
gcloud run deploy bidai --source . --region europe-west1
```

## Scope & Limitations

**Supported:** construction administrative specifications, draft contracts, Word-HTML and text-based PDFs.
**Not yet supported:** technical specifications, scanned/OCR PDFs, modern `.docx`.
**Known limitation:** retrieval precision can be improved (RAGAS surfaced noisy retrieval on large clauses) — next step is clause chunking and reranking.

## Testing

```bash
pytest -v          # unit + golden-set + negative (no-hallucination) tests
python -m eval.ragas_eval   # RAG evaluation
```