import joblib

NAMA_TAHAP = ['sehat', 'menurun', 'kritis']

def hitung_rolling_mean(df, sensor_aktif, window=10):
    """Rata-rata window siklus terakhir dari sensor ternormalisasi, per mesin.
    Untuk siklus awal (< window) memakai siklus yang tersedia."""
    df = df.sort_values(['unit', 'cycle']).reset_index(drop=True)
    kolom_mean = []
    for s in sensor_aktif:
        nama = f'{s}_mean{window}'
        df[nama] = df.groupby('unit')[f'{s}_norm'].transform(
            lambda x: x.rolling(window=window, min_periods=1).mean())
        kolom_mean.append(nama)
    return df, kolom_mean

def prediksi_tahap_kesehatan(df, kolom_mean, model):
    """model boleh objek KMeans atau jalur file .joblib.
    Cluster 0/1/2 sudah diurutkan: 0 = sehat, 1 = menurun, 2 = kritis."""
    if isinstance(model, str):
        model = joblib.load(model)
    df['cluster_kesehatan'] = model.predict(df[kolom_mean])
    df['tahap'] = df['cluster_kesehatan'].map(dict(enumerate(NAMA_TAHAP)))
    return df
