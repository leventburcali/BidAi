# BidAi — Public Tender Specification Analysis Assistant

An AI assistant that reads Turkish public tender specifications (*ihale şartnameleri*) and gives bidders a structured summary, risk analysis, and source-cited Q&A.

**🚀 Live Demo:** https://bidai-69768111605.europe-west1.run.app/docs
**Stack:** Python · FastAPI · Anthropic Claude · Pydantic · sentence-transformers · Docker · GCP Cloud Run

## Problem

Public tender specifications are long and complex; companies must read and analyze them carefully before bidding. Manually extracting critical details such as risks, eligibility criteria, and guarantee rates is a serious time sink with a high chance of oversight — and a single missed clause can lead to disqualification or unexpected costs. This assistant automates that analysis, producing structured information, a risk assessment, and source-cited answers from the document.

## Features

- **Structured Extraction:** Extracts information such as guarantee rates, eligibility criteria, and penalty clauses from the document as structured JSON.
- **Risk Analysis:** Translates the specification into risks from the bidder's perspective — elimination, cost, cash-flow, and timeline risks; prioritized and source-cited.
- **Document Q&A (RAG):** Free-form questions can be asked against the document; the system retrieves the relevant clauses and generates a source-cited answer.

## Architecture

1. **Parse:** The incoming document is parsed to segment the long clauses in the specification.
2. **Extraction:** A structured JSON summary of those clauses is produced using the Claude API. Pydantic validates that the data conforms to the expected JSON schema.
3. **Risk Analysis:** A risk report is generated from the extraction output via the Claude API, presented to the user with priority order and severity.
4. **RAG:** The user's question is embedded; using cosine similarity, the most relevant clauses from the parsed text are selected and sent to the Claude API, returning an answer that cites those clauses.
5. **API:** The presentation layer is built with FastAPI.
6. **DI:** Dependencies such as the LLM and embedding clients are placed behind interfaces (dependency injection), keeping the system testable and simplified.

Project structure:

```
app/
  parsing/      # Document parsing (.doc, .pdf → clauses)
  extraction/   # Structured extraction with the LLM (Pydantic schemas)
  qa/           # RAG: embedding, retrieval, Q&A
  risk/         # Risk analysis
  api/          # FastAPI REST API (presentation layer)
tests/          # Unit tests (pytest)
data/samples/   # Sample specifications
```

## Setup

**Requirements:** Python 3.10+

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set the API key (create a .env file)
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

## Running

```bash
# Start the API server
uvicorn app.api.main:app --reload

# Open in the browser:
#   http://127.0.0.1:8000/docs    -> interactive API docs (Swagger)
#   http://127.0.0.1:8000/health  -> health check
```

## API Endpoints

| Method | Path      | Description                                          |
|--------|-----------|------------------------------------------------------|
| GET    | `/health` | Health check                                         |
| POST   | `/ozet`   | Document text → structured summary                   |
| POST   | `/risk`   | Document text → risk report                          |
| POST   | `/soru`   | Document file + question → source-cited answer (RAG) |

## Tests

```bash
pytest -v
```

## Scope & Limitations

**Supported:**
- Construction administrative specifications and draft contracts
- Word-HTML and text-based (text-layer) PDF documents

**Not yet supported:**
- Technical specifications (their structure varies too much by sector; deliberately deferred to v2)
- Scanned / image-based PDFs (require OCR)
- Modern .docx format (the parser currently expects Word-HTML)

**Known limitations:**
- Retrieval is not perfect; for some questions the relevant clause may not surface in the top results (improved with title+body embedding, can be improved further).
- Vectors are held in memory; a production deployment needs a persistent vector store (e.g. pgvector).

## Technologies

Python · FastAPI · Anthropic Claude · Pydantic · sentence-transformers · pytest