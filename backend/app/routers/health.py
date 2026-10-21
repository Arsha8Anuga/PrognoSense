from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def check_health():
    return {
        "status": "ok",
        "service": "PrognoSense Backend",
        "version": "1.0.0"
    }