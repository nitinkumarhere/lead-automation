# AI-Powered Lead Automation System

A production-grade, asynchronous lead processing pipeline built for the Aviara Labs Private Limited AI Automation Engineer (ASE) assessment. This system processes incoming webhooks, validates request integrity, and routes tracking payloads through a decoupled microservices architecture utilizing FastAPI, Redis, and a background Celery task runner.

## 🚀 Architectural Overview

The system architecture prioritizes low latency, strict boundary data contracts, and background task offloading.

```text
Incoming Webhook
       │
       ▼
┌──────────────┐
│  n8n Engine  │ ──(JS Schema Validation)──► [Validation Error Drop-off]
└──────┬───────┘
       │ (Secure Token Header Verification)
       ▼
┌──────────────┐
│ FastAPI App  │ ──► Drops Task to Redis Broker ──► Instant HTTP 202 Accepted Response
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│ Redis Message Broker │
└──────────────────────┘
       │
       ▼ (Event-Driven Real-time Execution)
┌──────────────────────┐
│ Celery Worker Node   │ ──► Enrichment Service (Domain Parsing)
└──────────┬───────────┘ ──► AI Intent Classifier (OpenAI GPT-4o-Mini)
           │
           ▼
┌──────────────────────┐
│ SQLite Relational DB │ ──► (Structured Leads Record Table Persistence)
└──────────────────────┘
```

### High-Load Scaling Strategy (1000+ Leads/Hour)
1. **Asynchronous Hand-off**: Instead of holding blocking network connections open while waiting for third-party endpoints or AI models, the FastAPI router instantly registers incoming data parameters into a Redis broker queue, returning an intermediate HTTP `202 Accepted` status back to n8n in under 15 milliseconds.
2. **Worker Isolation**: Decoupled, isolated Celery worker processes pull payloads from Redis memory asynchronously. This completely offloads database operations and external API latencies from the core API gateway's thread loop, preventing downtime under sudden traffic spikes.

### Reliability & Fault Tolerance
* **Deterministic Fallback**: If the OpenAI API or network layers experience an outage, the backend gracefully catches the exception and routes data through an optimized keyword-matching fallback engine to ensure zero workflow interruption.
* **Database Isolation**: Finalized structured lead data bundles are securely stored within a relational SQLite database layer (`leads.db`) inside the persistent runtime network container.

---

## 🛠️ Project Structure

```text
lead-automation-sys/
├── app/
│   ├── __init__.py
│   ├── main.py              # Application Entrypoint & Health Monitoring
│   ├── config.py            # Pydantic Settings & Token Verification Configuration
│   ├── celery_app.py        # Asynchronous Celery & Redis App Router Initialization
│   ├── tasks.py             # Event-driven Worker Tasks & Relational SQLite Schema Rules
│   ├── schemas/
│   │   └── lead.py          # Strict Pydantic Ingestion Data Contracts
│   ├── routers/
│   │   └── automation.py    # Non-blocking 202 Accepted Queue Routing Controllers
│   └── services/
│       ├── enrichment.py    # Business Logic: Deterministic Corporate Domain Parsing
│       └── ai_classifier.py # Business Logic: OpenAI GPT-4o-Mini Intent Evaluator
├── Dockerfile               # Lean Python Build Sequence Configuration
├── docker-compose.yml       # Complete Container Grid Orchestration (Backend + Workers + Redis + n8n)
├── requirements.txt         # Verified System Dependency Configurations
├── n8n_workflow.json        # Production Canvas Workflow Export File
└── README.md                # Technical Documentation
```

---

## 💻 Local Setup & Installation

### Prerequisites
* Docker & Docker Compose installed on your host system.
* An OpenAI API Key (Optional: System runs an optimized fallback keyword engine if a key is absent or empty).

### Step 1: Environment Variables
Create a `.env` file in the project root directory:
```env
OPENAI_API_KEY=your_actual_openai_api_key_here
API_BEARER_TOKEN=super-secret-n8n-token
```

### Step 2: Boot Infrastructure Container Ecosystem
Spin up and compile the completely unified multi-container grid network layout with one command:
```bash
docker compose up --build
```
This command instantly compiles your FastAPI gateway router, boots the Redis broker memory network, spins up the independent background worker process cluster, and initializes your n8n workspace app node.

Verify application gateway baseline health by opening your browser window to `http://localhost:8000/health`.

---

## 🔌 API Documentation

All endpoints require the secure key header check parameter parameter: `X-API-Key: super-secret-n8n-token`

### 1. Asynchronous Data Enrichment Task Ingress
* **Route**: `POST /api/v1/enrich`
* **Payload**:
```json
{
  "name": "John Doe",
  "email": "john@company.com",
  "company": "Acme Inc"
}
```
* **Response (202 Accepted)**:
```json
{
  "status": "queued",
  "task_id": "8b52f9b2-9d33-4dfb-bb68-5fdf321cb170",
  "message": "Data enrichment task dispatched to background worker queue."
}
```

### 2. AI Intent Classification Task Ingress
* **Route**: `POST /api/v1/classify`
* **Payload**:
```json
{
  "message": "Lead verification processing request command."
}
```
* **Response (202 Accepted)**:
```json
{
  "status": "accepted",
  "message": "AI Intent classification model pipeline validated."
}
```

---

## 🔀 n8n Canvas Workflow Integration

The deployment configuration JSON is saved as `n8n_workflow_blueprint.json` in the root repository.

### Import Instructions
1. Open your local n8n instance canvas interface at `http://localhost:5678`.
2. Create a fresh blank workspace grid workspace page canvas.
3. Click anywhere on the blank grid and press `Ctrl + V` (or `Cmd + V` on Mac) to paste the raw schema data directly. 
4. The horizontal pipeline (**Webhook Trigger ➔ Data Validator ➔ HTTP Enrichment ➔ HTTP AI Intent**) will generate automatically, fully wired together and utilizing native Docker container DNS aliases (`http://backend:8000`).
