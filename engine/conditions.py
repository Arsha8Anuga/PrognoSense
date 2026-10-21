import json

def load_norm_stats(filepath='models/v1/norm_stats.json'):
    with open(filepath, 'r') as f:
        return json.load(f)

def apply_normalization(df, norm_stats, sensor_aktif):
    for cond in range(6):
        mask = df['kondisi'] == cond
        for s in sensor_aktif:
            kunci_cond = str(cond)
            if kunci_cond in norm_stats:
                mean_val = norm_stats[kunci_cond][s]['mean']
                std_val = norm_stats[kunci_cond][s]['std']
                df.loc[mask, f'{s}_norm'] = (df.loc[mask, s] - mean_val) / std_val
    return df
