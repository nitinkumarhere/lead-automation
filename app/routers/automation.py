from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from app.config import settings
from app.schemas.lead import EnrichmentInput, EnrichmentOutput, ClassificationInput, ClassificationOutput
from app.services.enrichment import EnrichmentService
from app.services.ai_classifier import AIClassifierService

router = APIRouter(prefix="/api/v1", tags=["Automation Execution"])
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.API_BEARER_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key security token"
        )
    return api_key

@router.post("/enrich", response_model=EnrichmentOutput, dependencies=[Depends(verify_api_key)])
async def enrich_lead_endpoint(payload: EnrichmentInput):
    return await EnrichmentService.enrich_lead(payload)

@router.post("/classify", response_model=ClassificationOutput, dependencies=[Depends(verify_api_key)])
async def classify_intent_endpoint(payload: ClassificationInput):
    classifier = AIClassifierService()
    return await classifier.classify_intent(payload)
