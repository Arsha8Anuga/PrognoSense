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


# ---------- evaluasi.json (Kontrak 6: GET /api/evaluasi) ----------
import json
from pathlib import Path


def _label_state(i, label_bin, urutan_tahap):
    return f"{label_bin[i // len(urutan_tahap)]} · {urutan_tahap[i % len(urutan_tahap)]}"


def tabel_policy(qtable, rl_config):
    """18 baris: state, aksi terbaik, Q lanjut, Q rawat."""
    q = np.asarray(qtable)
    lb, ut = rl_config["label_bin"], rl_config["urutan_tahap"]
    return [{"state": _label_state(i, lb, ut),
             "aksi": "rawat" if q[i].argmax() == 1 else "lanjut",
             "q_lanjut": round(float(q[i, 0]), 2),
             "q_rawat": round(float(q[i, 1]), 2)} for i in range(len(q))]


def susun_evaluasi(preds, rul_eval, kondisi, rl_config, model_dir="models/v1",
                   kurva_reward=None):
    """Gabungkan metrik clustering (Orang 1), regresi (Orang 2), dan RL (Orang 3)."""
    model_dir = Path(model_dir)
    strategi, policy = [], []
    for r in RASIO:
        qp = model_dir / f"qtable_r{r}.npy"
        q = np.load(qp) if qp.exists() else None
        strategi += bandingkan(preds, r, qtable=q, bins=rl_config["batas_bin"])
        if q is not None and r == 100:
            policy = tabel_policy(q, rl_config)
    return {
        "clustering": {
            "k_kondisi": kondisi["k"],
            "silhouette_kondisi": kondisi.get("silhouette_kondisi"),
            "k_kesehatan": kondisi["kesehatan"]["k"],
            "silhouette_kesehatan": kondisi["kesehatan"]["silhouette"],
            "pemilihan_k": kondisi["pemilihan_k"],
        },
        "rul": {
            "model": rul_eval["model"],
            "terpilih": rul_eval["terpilih"],
            "dinilai_pada": rul_eval["dinilai_pada"],
            "sebar": rul_eval["sebar"],
            "importance": rul_eval["importance"],
        },
        "rl": {
            "kurva_reward": kurva_reward or [],
            "policy": policy,
            "strategi": strategi,
            "catatan": ("Degradasi diputar ulang dari data; agen hanya menentukan kapan "
                        "lintasan dihentikan. Biaya total tidak menghitung siklus produktif "
                        "yang hilang, jadi bandingkan juga siklus terbuang dan produktif."),
        },
    }


def tulis_evaluasi(data_dir="data/results", model_dir="models/v1", keluar=None):
    d = Path(data_dir)
    preds = pd.read_csv(d / "predictions.csv")
    muat = lambda p: json.load(open(p, encoding="utf-8"))
    kurva_p = d / "kurva_reward.json"
    hasil = susun_evaluasi(
        preds, muat(d / "rul_evaluasi.json"), muat(d / "kondisi.json"),
        muat(Path(model_dir) / "rl_config.json"), model_dir,
        muat(kurva_p) if kurva_p.exists() else None)
    keluar = Path(keluar) if keluar else d / "evaluasi.json"
    with open(keluar, "w", encoding="utf-8") as f:
        json.dump(hasil, f, ensure_ascii=False, indent=1)
    return keluar


if __name__ == "__main__":
    print("Tertulis:", tulis_evaluasi())
