from fastapi import APIRouter, Query

router = APIRouter()

@router.get("/mesin/{unit}")
def get_detail_mesin(unit: int, rasio: int = Query(100, description="Rasio sampel data")):
    return {
        "status": "success",
        "unit": unit,
        "rasio": rasio,
        "sumber_data": f"mesin/{unit}.json",
        "detail": {
            "model_mesin": "TurboFan-FD001",
            "siklus_terakhir": 192,
            "estimasi_rul": 28,
            "riwayat_sensor": [
                {"siklus": 190, "s2": 642.35, "s3": 1589.2},
                {"siklus": 191, "s2": 642.80, "s3": 1590.1},
                {"siklus": 192, "s2": 643.10, "s3": 1591.5}
            ]
        }
    }

@router.get("/kondisi")
def get_kondisi():
    return {
        "status": "success",
        "sumber_data": "kondisi.json",
        "ringkasan_kondisi": {
            "total_unit": 100,
            "normal": 70,
            "peringatan": 20,
            "kritis": 10
        }
    }

@router.get("/evaluasi")
def get_evaluasi():
    return {
        "status": "success",
        "sumber_data": "evaluasi.json",
        "metrik_model": {
            "rmse": 14.25,
            "mae": 10.82,
            "r2_score": 0.89
        }
    }