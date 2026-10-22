"""Strategi pembanding + metrik evaluasi RL (Kontrak 4). Dibuat Orang 3.

Semua strategi dijalankan satu kali per mesin, memakai aturan yang sama dengan
engine/rl_env.py: rawat pada indeks i berarti i siklus produktif dan biaya rawat;
tidak pernah rawat berarti mesin rusak di siklus terakhir (biaya gagal).
Parameter (T dan N) dipilih di kelompok B, lalu diuji di kelompok C.
"""
import numpy as np
import pandas as pd

from .rl_env import BINS_DEFAULT, TAHAP

T_KANDIDAT = list(range(5, 65, 5))      # ambang RUL: 5, 10, ..., 60
N_KANDIDAT = list(range(20, 305, 5))    # rawat periodik tiap N siklus
RASIO = (50, 100, 200)                  # biaya gagal; biaya rawat tetap 10
BIAYA_RAWAT = 10


# ---------- data per mesin ----------
def siapkan(preds, units, bins=None):
    """Ubah predictions.csv jadi array numpy per mesin (urut menurut cycle)."""
    bins = list(bins) if bins is not None else list(BINS_DEFAULT)
    df = preds[preds["unit"].isin(units)].sort_values(["unit", "cycle"])
    data = {}
    for u, g in df.groupby("unit"):
        b = np.searchsorted(bins, g["rul_pred"].to_numpy(), side="right")
        tahap = g["tahap"].map(TAHAP).to_numpy()
        data[u] = {
            "cycle": g["cycle"].to_numpy(),
            "rul_pred": g["rul_pred"].to_numpy(),
            "rul_aktual": g["rul_aktual"].to_numpy(),
            "state": b * len(TAHAP) + tahap,
        }
    return data


# ---------- aturan: tiap fungsi mengembalikan indeks rawat, atau None ----------
def idx_ambang(u, T):
    i = np.flatnonzero(u["rul_pred"] < T)
    return int(i[0]) if len(i) else None


def idx_periodik(u, N):
    return N - 1 if N <= len(u["cycle"]) else None


def idx_tak_pernah(u):
    return None


def idx_oracle(u):
    i = np.flatnonzero(u["rul_aktual"] <= 1)
    return int(i[0]) if len(i) else None


def idx_agen(u, qtable):
    aksi = np.asarray(qtable)[u["state"]].argmax(axis=1)
    i = np.flatnonzero(aksi == 1)
    return int(i[0]) if len(i) else None


# ---------- metrik ----------
def metrik(data, fn_idx, biaya_gagal=100, biaya_rawat=BIAYA_RAWAT):
    n_rawat = n_gagal = 0
    terbuang, produktif = [], []
    for u in data.values():
        i = fn_idx(u)
        if i is None:                       # tidak pernah rawat -> rusak
            n_gagal += 1
            produktif.append(len(u["cycle"]) - 1)
        else:
            n_rawat += 1
            produktif.append(i)
            terbuang.append(float(u["rul_aktual"][i]))
    n = len(data)
    return {
        "gagal_pct": round(100 * n_gagal / n, 2),
        "siklus_terbuang": round(float(np.mean(terbuang)), 2) if terbuang else None,
        "siklus_produktif": round(float(np.mean(produktif)), 2),
        "biaya": int(biaya_rawat * n_rawat + biaya_gagal * n_gagal),
        "n_mesin": n, "n_rawat": n_rawat, "n_gagal": n_gagal,
    }


def _pilih(data_b, kandidat, fn, biaya_gagal):
    """Parameter dengan biaya total terkecil di B (seri: siklus terbuang lebih kecil)."""
    terbaik = None
    for p in kandidat:
        m = metrik(data_b, lambda u: fn(u, p), biaya_gagal)
        kunci = (m["biaya"], m["siklus_terbuang"] if m["siklus_terbuang"] is not None else 1e9)
        if terbaik is None or kunci < terbaik[0]:
            terbaik = (kunci, p)
    return terbaik[1]


def pilih_ambang(data_b, biaya_gagal=100):
    return _pilih(data_b, T_KANDIDAT, idx_ambang, biaya_gagal)


def pilih_periodik(data_b, biaya_gagal=100):
    return _pilih(data_b, N_KANDIDAT, idx_periodik, biaya_gagal)


# ---------- perbandingan semua strategi ----------
def bandingkan(preds, rasio=100, qtable=None, bins=None):
    """Pilih parameter di B, uji semua strategi di C. Kembalikan list baris tabel."""
    kel = preds.drop_duplicates("unit").set_index("unit")["kelompok"]
    unit_b = kel[kel == "B"].index.tolist()
    unit_c = kel[kel == "C"].index.tolist()
    data_b = siapkan(preds, unit_b, bins)
    data_c = siapkan(preds, unit_c, bins)

    T = pilih_ambang(data_b, rasio)
    N = pilih_periodik(data_b, rasio)

    daftar = [
        ("Ambang RUL", {"T": T}, lambda u: idx_ambang(u, T)),
        ("Periodik", {"N": N}, lambda u: idx_periodik(u, N)),
        ("Jalan sampai rusak", {}, idx_tak_pernah),
        ("Oracle (acuan)", {}, idx_oracle),
    ]
    if qtable is not None:
        daftar.insert(0, ("Agen Q-Learning", {}, lambda u: idx_agen(u, qtable)))

    hasil = []
    for nama, param, fn in daftar:
        m = metrik(data_c, fn, rasio)
        hasil.append({"nama": nama, "rasio": rasio, "parameter": param, **m})
    return hasil
