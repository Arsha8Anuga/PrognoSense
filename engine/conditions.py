import json
import numpy as np

def load_norm_stats(filepath='models/v1/norm_stats.json'):
    with open(filepath, 'r') as f:
        return json.load(f)

def assign_kondisi(df, kmeans_cond):
    """Tentukan kondisi operasi (0-5) tiap baris dari set1, set2, set3."""
    df['kondisi'] = kmeans_cond.predict(df[['set1', 'set2', 'set3']])
    return df

def apply_normalization(df, norm_stats, sensor_aktif):
    """Z-score per kondisi per sensor. Hasil: kolom {sensor}_norm."""
    for cond in range(6):
        mask = df['kondisi'] == cond
        for s in sensor_aktif:
            mean_val = norm_stats[str(cond)][s]['mean']
            std_val = norm_stats[str(cond)][s]['std']
            df.loc[mask, f'{s}_norm'] = (df.loc[mask, s] - mean_val) / std_val
    return df
