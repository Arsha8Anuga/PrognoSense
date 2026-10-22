from fastapi import APIRouter, Query

router = APIRouter()

@router.get("/armada")
def get_armada(rasio: int = Query(100, description="Rasio sampel data dalam persen")):
    return {
        "status": "success",
        "rasio": rasio,
        "sumber_data": "armada.json",
        "data": [
            {"unit": 1, "status": "Kritis", "rul": 12, "kesehatan": "Buruk"},
            {"unit": 2, "status": "Peringatan", "rul": 45, "kesehatan": "Sedang"},
            {"unit": 3, "status": "Normal", "rul": 110, "kesehatan": "Baik"}
        ]
    }