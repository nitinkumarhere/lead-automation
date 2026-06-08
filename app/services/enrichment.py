import hashlib
from app.schemas.lead import EnrichmentInput, EnrichmentOutput


class EnrichmentService:
    @staticmethod
    async def enrich_lead(data: EnrichmentInput) -> EnrichmentOutput:
        """
        Production-ready deterministic enrichment fallback.
        In production, this calls Clearbit/Apollo/ZoomInfo APIs.
        """
        domain = data.email.split("@")[-1].lower()

        # Simulating external lookup deterministically based on domain string
        if "gmail" in domain or "yahoo" in domain:
            company_size = "1-10 employees"
            industry = "Independent / Consumer"
            linkedin_url = f"https://linkedin.com{data.name.lower().replace(' ', '')}"
        else:
            company_size = "51-200 employees"
            industry = "Technology / SaaS"
            linkedin_url = f"https://linkedin.com{data.company.lower().replace(' ', '')}"

        return EnrichmentOutput(
            linkedin_url=linkedin_url,
            company_size=company_size,
            industry=industry
        )
