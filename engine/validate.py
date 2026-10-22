import pandas as pd
import numpy as np

def validate(df: pd.DataFrame, bundle=None) -> dict:
    """
    Validasi dataframe CSV/TXT unggahan pengguna berdasarkan Kontrak 2.
    """
    errors = []
    warnings = []
    mesin_lolos = []
    
    # 1. Cek jumlah kolom (wajib 26)
    if df.shape[1] != 26:
        return {
            "ok": False,
            "mesin_lolos": [],
            "error": [{"kode": "kolom_salah", "pesan": "Jumlah kolom tidak sesuai (harus 26 kolom)."}],
            "peringatan": []
        }
    
    # Standardisasi nama kolom
    cols = ['unit', 'cycle', 'set1', 'set2', 'set3'] + [f's{i}' for i in range(1, 22)]
    df.columns = cols
    
    # 2. Cek sel kosong atau bukan angka
    if df.isnull().values.any():
        errors.append({"kode": "nilai_kosong", "pesan": "Terdapat nilai kosong pada file."})
        return {"ok": False, "mesin_lolos": [], "error": errors, "peringatan": warnings}
        
    for unit, group in df.groupby('unit'):
        # Cek minimal 10 siklus
        if len(group) < 10:
            warnings.append({
                "kode": "terlalu_pendek", 
                "unit": str(unit), 
                "pesan": f"Mesin {unit} kurang dari 10 siklus (minimal 10)."
            })
            continue
            
        # Cek urutan siklus (mulai dari 1 dan naik 1 per baris)
        cycles = group['cycle'].values
        if list(cycles) != list(range(1, len(cycles) + 1)):
            warnings.append({
                "kode": "siklus_tidak_urut", 
                "unit": str(unit), 
                "pesan": f"Siklus mesin {unit} tidak berurutan."
            })
            continue
            
        mesin_lolos.append(str(unit))
        
    ok = len(mesin_lolos) > 0
    if not ok:
        errors.append({"kode": "csv_tidak_valid", "pesan": "Tidak ada mesin yang lolos validasi."})
        
    return {
        "ok": ok,
        "mesin_lolos": mesin_lolos,
        "error": errors,
        "peringatan": warnings
    }