"""FastAPI application entry point"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import session

app = FastAPI(
    title="Interview System API",
    version="2.0.0",
    description="REST API for AI-powered interview platform",
)

# CORS configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else []
DEFAULT_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=DEFAULT_ORIGINS + ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*\.(trycloudflare\.com|ngrok-free\.app|ngrok\.io)",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(session.router, prefix="/api")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "interview-system"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Interview System API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }
