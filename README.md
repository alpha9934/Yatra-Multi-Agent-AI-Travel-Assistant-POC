# ✈️ Yatra Multi-Agent AI Travel Assistant

A corporate travel assistant POC inspired by Yatra's real products — [DIYA](https://cloud.google.com/customers/yatra) (AI booking) and RECAP (expense management). Built to explore what a production-grade multi-agent system actually looks like when you take it beyond a basic LLM wrapper.

🔗 **Live Demo:** [roger101-yatra-ai-frontend.hf.space](https://roger101-yatra-ai-frontend.hf.space)  
⚙️ **Backend API:** [yatra-multi-agent-ai-travel-assistant-poc.onrender.com](https://yatra-multi-agent-ai-travel-assistant-poc.onrender.com/docs)

---

## What it does

Five specialized agents work behind a single chat interface, each owning a distinct part of the corporate travel lifecycle:

| Agent | Model | What it handles |
|---|---|---|
| Orchestrator | GPT-4o-mini | Reads user intent, routes to the right agent |
| Booking (DIYA) | GPT-4o | Flight/hotel search, policy enforcement, booking confirmation |
| Policy | GPT-4o-mini | Travel policy Q&A — grounded in real policy docs via RAG |
| Expense (RECAP) | GPT-4o Vision | Parses receipts from text or image, flags policy violations |
| Disruption | GPT-4o | Handles delays and cancellations, calculates entitlements |

The routing happens in under 200ms. Each agent returns structured JSON so the frontend can render the right UI component — flight cards, expense tiles, booking confirmations — rather than just raw text.

---

## Screenshots

### Chat Interface
![DIYA Chat](docs/screenshots/01_chat_ui.png)

### Flight Search + Policy Enforcement
![Booking](docs/screenshots/06_booking_search.png)

### Booking Confirmed (saved to Supabase)
![Confirmed](docs/screenshots/07_booking_confirmed.png)

### Policy Q&A with RAG citations
![Policy](docs/screenshots/02_policy_check.png)

### Disruption Handling
![Disruption](docs/screenshots/03_disruption_alert.png)

### Expense Logging
![Expense Text](docs/screenshots/08_my_expenses_tab.png)

### Receipt OCR
![Expense OCR](docs/screenshots/05_expense_ocr.png)

### My Expenses Tab
![Expenses Tab](docs/screenshots/08_my_expenses_tab.png)

### My Trips Tab
![Trips Tab](docs/screenshots/08_my_expenses_tab.png)

### Deployed on Hugging Face
![Live Frontend](docs/screenshots/12_frontend_hf_live.png)
![Live Backend](docs/screenshots/11_backend_hf_live.png)

---

## Architecture

```
User (Next.js)
      │
      ▼
FastAPI Backend (Render)
      │
Orchestrator — GPT-4o-mini, intent classification
      │
   ┌──┼──────────┬─────────────┐
   ▼  ▼          ▼             ▼
Booking  Policy  Expense   Disruption
(GPT-4o) (mini+  (GPT-4o   (GPT-4o)
          RAG)    Vision)
      │                │
      ▼                ▼
  Supabase          Supabase
 (bookings)        (expenses)
      │
  Pinecone
(policy RAG)
```

The policy agent is the most interesting one to explain in interviews — it doesn't just call GPT with a static prompt. It first embeds the user's question, retrieves the top-5 most relevant chunks from a Pinecone index (chunked from a 10-section corporate travel policy doc), then builds a grounded prompt with those chunks injected as context. The answer always comes with source citations and a retrieval confidence score.

---

## RAG Pipeline

The policy knowledge base is a real corporate travel policy document covering flights, hotels, meals, approvals, disruptions, and compliance. The ingestion pipeline:

1. Load `.txt` policy docs from `docs/policy_docs/`
2. Split into overlapping chunks (~150 tokens, 60-token overlap at sentence boundaries)
3. Embed with `text-embedding-3-small`
4. Upsert to Pinecone (cosine similarity, 1536 dimensions)

At query time, the user's question is embedded and the top-5 chunks retrieved. The policy agent uses these as grounded context — it won't answer from training data alone.

Chunking strategy matters a lot here. Early versions used 400-token chunks and got very few retrievable units. Dropping to 150 tokens with sentence-boundary splitting improved retrieval quality significantly.

---

## Eval Suite

25 golden test cases covering all three agent types, run with `python tests/eval/run_eval.py`:

```
[ROUTING] Intent Classification    12/12
[POLICY]  RAG Policy Q&A            8/8
[EXPENSE] Receipt Parsing           5/5

RESULTS: 25/25 passed (100%)
AVG LATENCY: 2509ms
```

Each case checks the actual agent output against expected values — intent labels, allowed/not-allowed flags, extracted amounts and categories. Results export to CSV for tracking regressions.

---

## Try it

Some prompts that exercise different agents:

```
"Book me a flight from Bengaluru to Delhi next Monday"
"Can I book business class for a 3-hour flight?"
"My IndiGo flight 6E-204 is delayed by 2 hours"
"Log expense: Ola cab ₹680 from airport today"
"My trip costs ₹40,000 — do I need manager approval?"
"Is alcohol reimbursable for client dinners?"
```

Or upload a receipt image via the Receipt button to test the OCR flow.

---

## Running locally

```bash
# Backend
cd backend
cp .env.example .env
# Fill in OPENAI_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_KEY,
# PINECONE_API_KEY, PINECONE_INDEX

pip install -r requirements.txt
python test_connections.py          # verify all services
uvicorn main:app --reload --port 8000

# Ingest policy docs (first time only)
curl -X POST http://localhost:8000/admin/ingest-policy

# Frontend
cd frontend
cp .env.local.example .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000
npm install && npm run dev
```

---

## Stack

| Layer | Tech |
|---|---|
| Frontend | Next.js 14, React, Tailwind |
| Backend | FastAPI, Python 3.11 |
| AI | GPT-4o, GPT-4o-mini, text-embedding-3-small |
| Vector DB | Pinecone (serverless, cosine) |
| Database | Supabase PostgreSQL |
| Deployment | Render (backend), Hugging Face Spaces (frontend) |
| CI | GitHub Actions — lint + eval + Docker smoke test |

---

## Project structure

```
├── backend/
│   ├── agents/
│   │   ├── orchestrator.py       # intent classification
│   │   ├── booking_agent.py      # flight search + policy enforcement
│   │   ├── policy_agent.py       # RAG-powered policy Q&A
│   │   ├── expense_agent.py      # receipt parsing + OCR
│   │   └── disruption_agent.py   # delay/cancellation handling
│   ├── db/
│   │   ├── supabase_client.py    # bookings, expenses, audit log
│   │   └── schema.sql            # table definitions
│   ├── rag/
│   │   └── pinecone_rag.py       # chunking, embedding, retrieval
│   ├── middleware/
│   │   └── auth.py               # API key auth, injection guard
│   ├── routes/                   # FastAPI endpoints
│   ├── tests/eval/run_eval.py    # 25-case golden eval suite
│   └── docs/policy_docs/         # source documents for RAG
└── frontend/
    └── src/
        ├── pages/index.js        # chat UI
        └── lib/api.js            # API client
```

---

## What I'd do differently at production scale

A few things that are deliberately simplified here that would need proper engineering in production:

- **Auth**: right now there's a single shared user context. Real deployment would need JWT auth and row-level security in Supabase scoped per employee.
- **RAG evaluation**: retrieval quality is currently eyeballed. Would add RAGAS metrics (faithfulness, answer relevance, context precision) and track them per deploy.
- **Flight data**: mock data for now. Would swap in Amadeus API for real availability and pricing.
- **Async jobs**: receipt OCR runs synchronously in the request. For large PDFs this would need a background queue (Celery or FastAPI BackgroundTasks) with a polling endpoint.
- **Cost tracking**: no per-request token counting yet. Would instrument with LangSmith or a simple middleware that logs model, tokens, and latency per agent call.

---

Built by [Abhishek Gupta](https://github.com/alpha9934) · Inspired by [Yatra's Google Cloud case study](https://cloud.google.com/customers/yatra)
