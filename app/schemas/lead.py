from pydantic import BaseModel, EmailStr, Field
from typing import Optional
class EnrichmentInput(BaseModel):
    name: str = Field(..., examples=["John Doe"])
    email: EmailStr = Field(..., examples=["john@company.com"])
    company: str = Field(..., examples=["Acme Inc"])

class EnrichmentOutput(BaseModel):
    linkedin_url: str
    company_size: str
    industry: str

class ClassificationInput(BaseModel):
    message: str = Field(..., examples=["I am interested in your services"])

class ClassificationOutput(BaseModel):
    intent: str
    confidence: float



class LeadDBRecord(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    company: str
    linkedin_url: str
    company_size: str
    industry: str
    intent: str
    confidence: float

    class Config:
        from_attributes = True
