from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

from app.api.routes.scoring import router as scoring_router

app = FastAPI(
    title="Scoring Service",
    description="Микросервис для эмуляции банковского скоринга",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роутеры
app.include_router(scoring_router, prefix="/api/v1/scoring", tags=["scoring"])

@app.get("/")
async def root():
    return {"message": "Scoring Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "scoring"}

