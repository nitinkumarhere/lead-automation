from fastapi import FastAPI
from app.routers import automation

app = FastAPI(
    title="Aviara Labs - AI Automation Engine Backend",
    version="1.0.0",
    docs_url="/docs"
)

# Include API Modular Routers
app.include_router(automation.router)

@app.get("/health", tags=["Infrastructure Monitoring"])
async def health_check():
    return {"status": "healthy", "service": "lead-automation-pipeline"}
