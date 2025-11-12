"""
FastAPI Backend for Live Stream Subtitle System
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

from api.stream import router as stream_router
from api.processing import router as processing_router

app = FastAPI(
    title="Live Sub API",
    description="Backend API for automatic stream recording and subtitle generation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(stream_router, prefix="/api/stream", tags=["stream"])
app.include_router(processing_router, prefix="/api/processing", tags=["processing"])

@app.get("/")
async def root():
    return {"message": "Live Sub API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
