"""Model RUL: kandidat yang dibandingkan, metrik, dan data test resmi (Kontrak 3). Pemilik: Orang 2."""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.neighbors import KNeighborsRegressor

from .features import RUL_CAP


class RataRata:
    """Baseline: selalu menebak rata-rata RUL data latih."""
    def fit(self, X, y):
        self.nilai_ = float(np.mean(y))
        return self

    def predict(self, X):
        return np.full(len(X), self.nilai_)


def kandidat():
    """Model baru (belum dilatih) untuk dibandingkan; kunci = nama di evaluasi.json."""
    import lightgbm as lgb
    return {
        'Baseline rata-rata': RataRata(),
        'Regresi linear (Ridge)': Ridge(alpha=1.0),
        'kNN (k=15)': KNeighborsRegressor(n_neighbors=15, n_jobs=-1),
        'Random Forest': RandomForestRegressor(n_estimators=200, min_samples_leaf=10, max_features=0.5,
                                               n_jobs=-1, random_state=42),
        'LightGBM': lgb.LGBMRegressor(n_estimators=600, learning_rate=0.03, num_leaves=31,
                                      min_child_samples=50, subsample=0.8, subsample_freq=1,
                                      colsample_bytree=0.8, random_state=42, verbose=-1),
    }


def tebak(model, X):
    """Prediksi RUL; tidak ada umur negatif."""
    return np.clip(model.predict(X), 0, None)


def skor(y, p):
    return {'rmse': round(float(np.sqrt(mean_squared_error(y, p))), 2),
            'mae': round(float(mean_absolute_error(y, p)), 2)}


def rul_test_resmi(path, prefix):
    """RUL benar siklus terakhir tiap mesin test, index = ID mesin (mis. FD002_T1), dipotong di RUL_CAP."""
    r = pd.read_csv(path, header=None)[0]
    return pd.Series(r.values, index=[f'{prefix}{i}' for i in range(1, len(r) + 1)]).clip(upper=RUL_CAP)
