# AI-Powered Lead Automation System

A production-grade, asynchronous lead processing pipeline built for the Aviara Labs Private Limited AI Automation Engineer (ASE) assessment. This system processes incoming webhooks, validates request integrity, enriches metadata, handles AI-driven intent categorization, and persists records downstream.

## 🚀 Architectural Overview

The system architecture prioritizes low latency, strict data contracts, validation at the boundary, and fallback resilience.

```text
Incoming Webhook
       │
       ▼
┌──────────────┐
│  n8n Engine  │ ──(JS Scheme Validation)──► [Validation Error Drop-off]
└──────┬───────┘
       │ (Secure REST API / Token Header Verification)
       ▼
┌──────────────┐
│ FastAPI App  │ ──► Service Layer ──► Enrichment Utility (Deterministic Fallback)
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│ OpenAI GPT-4o-Mini   │ ──(System Prompt / JSON Enforcement)──► Intent Class Response
└──────────────────────┘
```

### High-Load Scaling Strategy (1000+ Leads/Hour)
1. **Asynchronous Hand-off**: To support high volume without connection starvation, the synchronous REST routes can easily sit behind an asynchronous message queue (e.g., Celery backed by a Redis broker instance).
2. **Worker Isolation**: Isolating API controllers from long-running third-party input/output processing operations prevents event-loop blockages under traffic spikes.

### Reliability & Fault Tolerance
* **Rate Limiting**: Built-in boundary controls prevent downstream execution budget exhaustion.
* **Deterministic Fallback**: If the external LLM or Enrichment layers fail or experience outages, the backend catches the error cleanly and routes data via optimized string token match rules to guarantee zero pipeline downtime.
* **Idempotency Strategy**: Pipeline checks execute unique key verification using combined hash keys derived from `email` + `company` strings before running insert arrays.

---

## 🛠️ Project Structure

```text
lead-automation-sys/
├── app/
│   ├── __init__.py
│   ├── main.py              # Application Entrypoint & Health Controls
│   ├── config.py            # Pydantic Settings Management
│   ├── schemas/
│   │   └── lead.py          # Strict Pydantic Data Domain Ingestion Contracts
│   ├── routers/
│   │   └── automation.py    # Endpoint Controllers & Key Verification Layers
│   └── services/
│       ├── enrichment.py    # Business Logic: Data Enrichment Engineering
│       └── ai_classifier.py # Business Logic: OpenAI JSON Structure Routing
├── Dockerfile               # Lean Container Build Sequence
├── docker-compose.yml       # Infrastructure Orchestration Grid
├── requirements.txt         # Verified System Dependency Configurations
└── README.md                # Technical System Documentation
```

---

## 💻 Local Setup & Installation

### Prerequisites
* Docker & Docker Compose installed on your host system.
* An OpenAI API Key (Optional: System runs an optimized fallback engine if a key is absent).

### Step 1: Environment Variables
Create a `.env` file in the project root directory:
```env
OPENAI_API_KEY=your_actual_openai_api_key_here
API_BEARER_TOKEN=super-secret-n8n-token
```

### Step 2: Boot Infrastructure
Spin up the containerized backend ecosystem:
```bash
docker compose up --build
```
Verify the instance health by pointing your browser to `http://localhost:8000/health`.

---

## 🔌 API Documentation

All endpoints require the secure key header: `X-API-Key: super-secret-n8n-token`

### 1. Data Enrichment Endpoint
* **Route**: `POST /api/v1/enrich`
* **Payload**:
```json
{
  "name": "John Doe",
  "email": "john@company.com",
  "company": "Acme Inc"
}
```
* **Response (200 OK)**:
```json
{
  "linkedin_url": "https://linkedin.com",
  "company_size": "51-200 employees",
  "industry": "Technology / SaaS"
}
```

### 2. AI Intent Classification Endpoint
* **Route**: `POST /api/v1/classify`
* **Payload**:
```json
{
  "message": "I am interested in your services"
}
```
* **Response (200 OK)**:
```json
{
  "intent": "sales_enquiry",
  "confidence": 0.95
}
```

---

## 🔀 n8n Workflow Integration

The workflow configuration JSON is stored in the repository root directory as `n8n_workflow_blueprint.json`. 

### Import Instructions
1. Create a blank canvas workflow in your n8n workspace.
2. Press `Ctrl + V` (or `Cmd + V` on Mac) to paste the raw JSON structure layout directly onto the grid.
3. Configure your downstream tracking credentials (e.g., Airtable/Google Sheets token scopes) on the storage module.
