from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routers import prediksi, armada, mesin

app = FastAPI(
    title="PrognoSense API",
    version="1.0.0",
    description="API Layanan Monitoring & Prediksi Kesehatan Mesin"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

# Registrasi Router Sesuai Spesifikasi Dokumen
app.include_router(armada.router, prefix="/api", tags=["Armada"])
app.include_router(mesin.router, prefix="/api", tags=["Mesin & Analisis"])
app.include_router(prediksi.router, prefix="/api", tags=["Prediksi"])