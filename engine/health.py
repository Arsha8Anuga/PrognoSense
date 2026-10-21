import joblib

def hitung_rolling_mean(df, sensor_aktif, window=10):
    kolom_mean = []
    for s in sensor_aktif:
        nama_kolom = f'{s}_mean{window}'
        df[nama_kolom] = df.groupby('unit')[f'{s}_norm'].transform(lambda x: x.rolling(window=window, min_periods=1).mean())
        kolom_mean.append(nama_kolom)
    return df, kolom_mean

def prediksi_tahap_kesehatan(df, kolom_mean, model_path='models/v1/health_kmeans.joblib'):
    kmeans_health = joblib.load(model_path)
    df['cluster_kesehatan'] = kmeans_health.predict(df[kolom_mean])
    return df
