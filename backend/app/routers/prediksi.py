from fastapi import APIRouter

router = APIRouter()

@router.get("/prediksi")
def get_prediksi():
    return {"message": "Endpoint prediksi"}