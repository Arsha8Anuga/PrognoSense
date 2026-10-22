import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.logging_mw import RequestLoggingMiddleware
from backend.app.routers import health, prediksi, analisis, armada

app = FastAPI(
    title="PrognoSense API",
    description="API Layanan Monitoring & Prediksi Kesehatan Mesin",
    version="1.0.0"
)

# 1. Pasang Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Pasang Custom Middleware Logging (Persyaratan Orang 4)
app.add_middleware(RequestLoggingMiddleware)

# 3. Mendaftarkan Router Endpoints
app.include_router(health.router, tags=["Health"])
app.include_router(prediksi.router, prefix="/api", tags=["Prediksi"])
app.include_router(analisis.router, prefix="/api", tags=["Analisis"])
app.include_router(armada.router, prefix="/api", tags=["Armada"])

@app.get("/")
def root():
    return {"message": "PrognoSense API is running"}