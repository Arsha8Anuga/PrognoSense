import re

from fastapi import APIRouter

from ..deps import baca_hasil, cek_rasio, galat

router = APIRouter()


@router.get('/armada')
def get_armada(rasio: int = 100):
    if (e := cek_rasio(rasio)):
        return e
    data = baca_hasil(f'armada_r{rasio}.json')
    return data if data is not None else galat(500, 'data_tidak_ada', f'armada_r{rasio}.json belum diekspor.')


@router.get('/mesin/{unit}')
def get_mesin(unit: str, rasio: int = 100):
    if (e := cek_rasio(rasio)):
        return e
    if not re.fullmatch(r'FD00[24]_\d+', unit):     # cegah path traversal lewat nama unit
        return galat(404, 'unit_tidak_ada', f'Unit {unit} tidak ditemukan.')
    data = baca_hasil('mesin', f'r{rasio}', f'{unit}.json')
    return data if data is not None else galat(404, 'unit_tidak_ada', f'Unit {unit} tidak ditemukan.')
