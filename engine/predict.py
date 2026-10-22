"""load() dan predict() untuk backend (Kontrak 5). Fungsi murni: tidak menulis file, tidak melatih. Pemilik: Orang 2."""
import json
import os

import joblib
import numpy as np

from .conditions import apply_normalization, assign_kondisi
from .features import buat_fitur
from .health import NAMA_TAHAP
from .schema import SENSOR_AKTIF

RASIO = (50, 100, 200)


def load(model_dir='models/v1'):
    p = lambda f: os.path.join(model_dir, f)
    with open(p('norm_stats.json')) as f:
        norm_stats = json.load(f)
    with open(p('features.json')) as f:
        fitur = json.load(f)
    with open(p('rl_config.json')) as f:
        rl = json.load(f)
    # shortcut: Q-table boleh belum ada (Q-Learning belum dilatih); aksi/q jadi None sampai file qtable_r*.npy disalin
    qtable = {r: np.load(p(f'qtable_r{r}.npy')) for r in RASIO if os.path.exists(p(f'qtable_r{r}.npy'))}
    return {'kmeans_cond': joblib.load(p('kmeans_cond.joblib')), 'norm_stats': norm_stats,
            'health': joblib.load(p('health_kmeans.joblib')), 'rul': joblib.load(p('rul_model.joblib')),
            'fitur': fitur, 'rl': rl, 'qtable': qtable}


def state_rl(rul_pred, tahap_idx, rl):
    """Indeks state Q-table; rumusnya disimpan di rl_config.json supaya sama dengan rl_env.py."""
    b = int(np.digitize(rul_pred, rl['batas_bin']))
    return b * rl['n_tahap'] + int(tahap_idx)


def predict(df, bundle, rasio=100):
    """df: kolom unit, cycle, set1-3, s1-s21, sudah lolos validate. Hasil: satu dict per mesin (siklus terakhir)."""
    df = assign_kondisi(df.copy(), bundle['kmeans_cond'])
    df = apply_normalization(df, bundle['norm_stats'], SENSOR_AKTIF)
    F = buat_fitur(df)
    akhir = F.groupby('unit').tail(1)
    kondisi = df.sort_values(['unit', 'cycle']).groupby('unit')['kondisi'].last()
    rul = np.clip(bundle['rul'].predict(akhir[bundle['fitur']]), 0, None)
    tahap_idx = bundle['health'].predict(akhir[[f'{s}_mean10' for s in SENSOR_AKTIF]])
    q_tab = bundle['qtable'].get(rasio)

    hasil = []
    for (_, baris), r, t in zip(akhir.iterrows(), rul, tahap_idx):
        q = aksi = None
        if q_tab is not None:
            qs = q_tab[state_rl(r, t, bundle['rl'])]
            q = {'lanjut': round(float(qs[0]), 2), 'rawat': round(float(qs[1]), 2)}
            aksi = 'rawat' if qs[1] > qs[0] else 'lanjut'
        hasil.append({'unit': str(baris['unit']), 'siklus_terakhir': int(baris['cycle']),
                      'kondisi': int(kondisi[baris['unit']]), 'tahap': NAMA_TAHAP[int(t)],
                      'rul_pred': round(float(r), 1), 'aksi': aksi, 'q': q})
    return hasil
