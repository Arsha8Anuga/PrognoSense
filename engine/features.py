"""Fitur jendela 10 siklus + label RUL (Kontrak 3). Pemilik: Orang 2."""
import numpy as np
import pandas as pd

from .schema import SENSOR_AKTIF
WINDOW = 10
RUL_CAP = 125


def nama_fitur(sensor=SENSOR_AKTIF):
    """Urutan 43 fitur; inilah isi features.json."""
    return ([f'{s}_last' for s in sensor] + [f'{s}_mean10' for s in sensor]
            + [f'{s}_slope10' for s in sensor] + ['cycle'])


def buat_fitur(df, sensor=SENSOR_AKTIF, window=WINDOW):
    """df wajib punya kolom unit, cycle, dan {s}_norm. Mengembalikan df baru berisi 43 fitur."""
    df = df.sort_values(['unit', 'cycle']).reset_index(drop=True)
    g = df['unit']

    def roll_sum(col):  # jumlah bergulir per mesin; siklus 1-9 memakai siklus yang tersedia
        return col.groupby(g).rolling(window, min_periods=1).sum().reset_index(level=0, drop=True)

    t = df['cycle'].astype(float)
    n, st, stt = roll_sum(pd.Series(1.0, index=df.index)), roll_sum(t), roll_sum(t * t)
    penyebut = n * stt - st * st          # = 0 bila jendela hanya 1 titik

    out = {'unit': df['unit'], 'cycle': df['cycle']}
    for s in sensor:
        x = df[f'{s}_norm']
        sx, stx = roll_sum(x), roll_sum(t * x)
        out[f'{s}_last'] = x
        out[f'{s}_mean10'] = sx / n
        # kemiringan regresi linear (least squares) dalam jendela; 1 titik -> 0
        out[f'{s}_slope10'] = np.where(penyebut > 0, (n * stx - st * sx) / penyebut.where(penyebut > 0, 1), 0.0)
    return pd.DataFrame(out)[['unit'] + nama_fitur(sensor)]


def label_rul(df, cap=RUL_CAP):
    """RUL = siklus terakhir mesin - cycle, dipotong di cap. Hanya untuk data train."""
    akhir = df.groupby('unit')['cycle'].transform('max')
    return (akhir - df['cycle']).clip(upper=cap)


if __name__ == '__main__':  # uji kecil: slope garis lurus harus tepat, siklus 1 harus 0
    d = pd.DataFrame({'unit': ['X'] * 12, 'cycle': range(1, 13)})
    for s in SENSOR_AKTIF:
        d[f'{s}_norm'] = 0.5 * d['cycle'] + 3
    f = buat_fitur(d)
    assert f['s2_slope10'].iloc[0] == 0
    assert np.allclose(f['s2_slope10'].iloc[1:], 0.5)
    assert np.isclose(f['s2_mean10'].iloc[11], (0.5 * np.arange(3, 13) + 3).mean())
    assert list(label_rul(d)) == list(range(11, -1, -1))
    assert len(nama_fitur()) == 43
    print('features.py OK')
