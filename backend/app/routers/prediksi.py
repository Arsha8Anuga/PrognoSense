from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
import io
from engine.validate import validate

router = APIRouter()

@router.post("/prediksi")
async def prediksi_rul(file: UploadFile = File(...)):
    if not file.filename.endswith(('.csv', '.txt')):
        raise HTTPException(status_code=400, detail="Format file harus .csv atau .txt")
    
    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents), sep=r"\s+|,", engine="python", header=None)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gagal membaca file: {str(e)}")
        
    res_val = validate(df)
    if not res_val["ok"]:
        return {
            "status": "error",
            "errors": res_val["error"],
            "warnings": res_val["peringatan"]
        }
        
    return {
        "status": "success",
        "mesin_lolos": res_val["mesin_lolos"],
        "warnings": res_val["peringatan"],
        "data": []
    }