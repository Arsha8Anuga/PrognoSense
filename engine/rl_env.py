"""Lingkungan RL perawatan mesin (Kontrak 4). Dibuat Orang 3, dipakai Orang 2.

Optimal stopping: tiap siklus agen memilih 0 = lanjut atau 1 = rawat.
Degradasi diputar ulang dari data; yang dikendalikan agen hanya kapan lintasan dihentikan.
rul_aktual hanya dipakai untuk mencatat metrik, tidak pernah masuk state.
"""
import numpy as np
import pandas as pd

TAHAP = {"sehat": 0, "menurun": 1, "kritis": 2}
BINS_DEFAULT = [10, 20, 35, 50, 80]  # <10, 10-19, 20-34, 35-49, 50-79, >=80
N_TAHAP = 3
N_STATE = (len(BINS_DEFAULT) + 1) * N_TAHAP  # 18
LANJUT, RAWAT = 0, 1


class MaintenanceEnv:
    def __init__(self, preds, units, bins=None, biaya_rawat=10,
                 biaya_gagal=100, seed=42):
        self.bins = list(bins) if bins is not None else list(BINS_DEFAULT)
        self.biaya_rawat = biaya_rawat
        self.biaya_gagal = biaya_gagal
        self.rng = np.random.default_rng(seed)
        self.units = list(units)
        df = preds[preds["unit"].isin(self.units)].sort_values(["unit", "cycle"])
        self.data = {u: g.reset_index(drop=True) for u, g in df.groupby("unit")}
        missing = [u for u in self.units if u not in self.data]
        if missing:
            raise ValueError(f"Unit tidak ada di preds: {missing[:5]}")
        self.n_state = (len(self.bins) + 1) * N_TAHAP
        self.unit = None
        self.rows = None
        self.i = 0

    def state_of(self, rul_pred, tahap):
        b = int(np.searchsorted(self.bins, rul_pred, side="right"))
        return b * N_TAHAP + TAHAP[tahap]

    def _state(self, row):
        return self.state_of(row["rul_pred"], row["tahap"])

    def reset(self, unit=None):
        if unit is None:
            unit = self.units[int(self.rng.integers(len(self.units)))]
        self.unit = unit
        self.rows = self.data[unit]
        self.i = 0
        return self._state(self.rows.iloc[0])

    def step(self, action):
        row = self.rows.iloc[self.i]
        info = {"unit": self.unit, "cycle": int(row["cycle"]),
                "rul_aktual": float(row["rul_aktual"]), "gagal": False}
        if action == RAWAT:
            return self._state(row), -float(self.biaya_rawat), True, info
        if self.i == len(self.rows) - 1:  # lanjut di siklus terakhir = rusak
            info["gagal"] = True
            return self._state(row), -float(self.biaya_gagal), True, info
        self.i += 1
        return self._state(self.rows.iloc[self.i]), 1.0, False, info
