from fastapi import APIRouter

from ..deps import baca_hasil, galat

router = APIRouter()


def _file(nama):
    data = baca_hasil(nama)
    return data if data is not None else galat(500, 'data_tidak_ada', f'{nama} belum diekspor.')


@router.get('/kondisi')
def get_kondisi():
    return _file('kondisi.json')


@router.get('/evaluasi')
def get_evaluasi():
    return _file('evaluasi.json')
