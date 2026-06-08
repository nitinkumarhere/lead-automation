import json
import asyncio
from app.celery_app import celery_app
from app.schemas.lead import EnrichmentInput, ClassificationInput
from app.services.enrichment import EnrichmentService
from app.services.ai_classifier import AIClassifierService


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

    # 3. Consolidate results for state preservation log
    result = {
        "status": "PROCESSED",
        "lead": lead_data_dict,
        "enrichment": enriched_data.model_dump(),
        "ai_analysis": ai_classification.model_dump()
    }

    # This prints out live inside your separated 'worker-1' Docker shell screen!
    print(f"[BACKGROUND WORKER SUCCESS] Fully completed background lead execution task: {json.dumps(result)}")
    return result
