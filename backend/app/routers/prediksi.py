import io

import pandas as pd
from fastapi import APIRouter, File, Form, UploadFile

from engine.predict import predict
from engine.validate import KOLOM, validate
from .. import config
from ..deps import BUNDLE, cek_rasio, galat

router = APIRouter()


def baca_file(isi: bytes) -> pd.DataFrame:
    """CSV dengan header Kontrak 2, atau file NASA tanpa header (dipisah spasi)."""
    teks = isi.decode('utf-8', errors='replace')
    baris1 = teks.lstrip().split('\n', 1)[0]
    if any(c.isalpha() for c in baris1.replace('e', '').replace('E', '')):    # ada header (abaikan notasi 1e-3)
        return pd.read_csv(io.StringIO(teks), sep=None, engine='python', dtype=str)
    return pd.read_csv(io.StringIO(teks), sep=r'[\s,]+', engine='python', header=None, dtype=str)


@router.post('/prediksi')
async def prediksi(file: UploadFile = File(...), rasio: int = Form(100), sampai_rusak: bool = Form(False)):
    if (e := cek_rasio(rasio)):
        return e
    isi = await file.read()
    if len(isi) > config.BATAS_FILE:
        return galat(413, 'file_terlalu_besar', 'Ukuran file maksimal 20 MB.')
    try:
        df = baca_file(isi)
    except Exception as ex:
        return galat(400, 'file_tidak_terbaca', f'File tidak bisa dibaca: {ex}')
    if df.shape[1] == len(KOLOM) and list(df.columns) not in (KOLOM, list(range(len(KOLOM)))):
        return galat(422, 'csv_tidak_valid', 'Nama kolom tidak sesuai Kontrak 2.',
                     [{'kode': 'kolom_salah', 'pesan': 'Header harus: ' + ', '.join(KOLOM)}])

    bundle = BUNDLE['model']
    lap = validate(df, bundle)
    if not lap['ok']:
        return galat(422, 'csv_tidak_valid', 'File tidak lolos validasi.', lap['error'] + lap['peringatan'])

    df.columns = KOLOM
    df['unit'] = df['unit'].astype(str).str.strip()
    df = df[df['unit'].isin(lap['mesin_lolos'])]
    df[KOLOM[1:]] = df[KOLOM[1:]].apply(pd.to_numeric)
    hasil = predict(df, bundle, rasio=rasio)
    return {'model_version': BUNDLE['versi'], 'rasio': rasio,
            'mesin_diterima': len(hasil), 'mesin_ditolak': len(lap['peringatan']),
            'hasil': hasil, 'peringatan': lap['peringatan'],
            # shortcut: sampai_rusak hanya dicatat (Kontrak 2), belum dipakai melatih apa pun
            'layak_training': bool(sampai_rusak)}
