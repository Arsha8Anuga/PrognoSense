"""Satu bundle model untuk semua request, dan pembaca file hasil (Kontrak 6)."""
import json
import os
from datetime import datetime, timedelta, timezone

from fastapi.responses import JSONResponse

from engine.predict import load
from . import config

BUNDLE = {}


def muat_model():
    BUNDLE['model'] = load(config.MODEL_DIR)
    with open(os.path.join(config.MODEL_DIR, 'metadata.json')) as f:
        BUNDLE['versi'] = json.load(f)['model_version']
    BUNDLE['dimuat'] = datetime.now(timezone(timedelta(hours=7))).isoformat(timespec='seconds')


def galat(status, kode, pesan, detail=None):
    """Format error Kontrak 6."""
    isi = {'kode': kode, 'pesan': pesan}
    if detail:
        isi['detail'] = detail
    return JSONResponse(status_code=status, content={'error': isi})


def baca_hasil(*bagian):
    """JSON dari data/results; None bila file tidak ada."""
    path = os.path.join(config.DATA_DIR, *bagian)
    if not os.path.isfile(path):
        return None
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def cek_rasio(rasio):
    return None if rasio in config.RASIO else galat(400, 'rasio_salah', 'rasio harus 50, 100, atau 200.')
