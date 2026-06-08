import json
import sqlite3
import asyncio
from app.celery_app import celery_app
from app.schemas.lead import EnrichmentInput, ClassificationInput
from app.services.enrichment import EnrichmentService
from app.services.ai_classifier import AIClassifierService


def init_db():
    """Initializes a local structured database inside the container."""
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            company TEXT,
            linkedin_url TEXT,
            company_size TEXT,
            industry TEXT,
            intent TEXT,
            confidence REAL
        )
    """)
    conn.commit()
    conn.close()

# Run database creation on worker initialization
init_db()

# Helper to run async functions inside synchronous Celery workers natively
def run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@celery_app.task(name="tasks.process_lead_pipeline")
def process_lead_pipeline(lead_data_dict: dict):
    """
    Asynchronous Worker Task: Executes Enrichment + AI classification sequentially
    completely off the main API loop thread.
    """
    # Parse dict payload back into structured strict Pydantic model objects
    lead_input = EnrichmentInput(**lead_data_dict)

    # 1. Run Enrichment Service Task
    enriched_data = run_async(EnrichmentService.enrich_lead(lead_input))

    # 2. Map Payload text data and run AI Intent Classifier Task
    message_text = f"Lead from {lead_input.name} at {lead_input.company} requires verification processing."
    classifier_input = ClassificationInput(message=message_text)
    ai_classification = run_async(AIClassifierService().classify_intent(classifier_input))

    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()
    cursor.execute("""
            INSERT INTO leads (name, email, company, linkedin_url, company_size, industry, intent, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
        lead_input.name,
        lead_input.email,
        lead_input.company,
        enriched_data.linkedin_url,
        enriched_data.company_size,
        enriched_data.industry,
        ai_classification.intent,
        ai_classification.confidence
    ))
    conn.commit()
    conn.close()

    # 3. Consolidate results for state preservation log
    result = {
        "status": "PROCESSED",
        "name": lead_input.name,
        "email": lead_input.email,
        "company": lead_input.company,
        "linkedin_url": enriched_data.linkedin_url,
        "company_size": enriched_data.company_size,
        "industry": enriched_data.industry,
        "intent": ai_classification.intent,
        "confidence": ai_classification.confidence
    }

    # This prints out live inside your separated 'worker-1' Docker shell screen!
    print(f"[DATABASE COUPLING SUCCESS] Saved structured record for: {lead_input.email}")
    return result
