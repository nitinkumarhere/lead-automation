from fastapi import FastAPI
from app.routers import automation

app = FastAPI(
    title="Aviara Labs - Async AI Automation Backend",
    version="1.1.0",
    docs_url="/docs"
)

# Crucial: This binds your /api/v1/process-async router endpoints to the web server
app.include_router(automation.router)

@app.get("/health", tags=["Infrastructure Monitoring"])
async def health_check():
    return {"status": "healthy", "service": "async-lead-automation-pipeline"}
