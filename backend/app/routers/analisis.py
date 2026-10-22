from fastapi import APIRouter

router = APIRouter()

@router.get("/analisis/ringkasan")
def get_ringkasan_analisis():
    return {
        "status": "success",
        "total_mesin_dianalisis": 12,
        "mesin_kritis": 2,
        "rata_rata_rul": 45.5,
        "unit": "siklus"
    }