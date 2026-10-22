"""Validasi CSV upload (Kontrak 2). Fungsi murni: tidak menulis file."""
import numpy as np
import pandas as pd

KOLOM = ['unit', 'cycle', 'set1', 'set2', 'set3'] + [f's{i}' for i in range(1, 22)]
AMBANG_KONDISI = 0.05
MAKS_DETAIL = 20


def validate(df: pd.DataFrame, bundle=None) -> dict:
    """df: 26 kolom mentah dari file. Kembalikan ok, mesin_lolos, error, peringatan (Kontrak 5)."""
    hasil = {'ok': False, 'mesin_lolos': [], 'error': [], 'peringatan': []}
    if df.shape[1] != len(KOLOM):
        hasil['error'].append({'kode': 'kolom_salah', 'pesan': f'File punya {df.shape[1]} kolom; harus {len(KOLOM)}.'})
        return hasil
    df = df.copy()
    df.columns = KOLOM
    kosong = df.isna()
    df['unit'] = df['unit'].astype(str).str.strip()

    angka = df.drop(columns='unit').apply(pd.to_numeric, errors='coerce')
    bukan = angka.isna() & ~kosong.drop(columns='unit')
    for kode, mask, pesan in [('nilai_kosong', kosong, 'Sel kosong.'), ('bukan_angka', bukan, 'Sel bukan angka.')]:
        baris, kolom = np.nonzero(mask.to_numpy())
        for b, k in list(zip(baris, kolom))[:MAKS_DETAIL]:
            hasil['error'].append({'kode': kode, 'baris': int(b) + 1, 'kolom': mask.columns[k], 'pesan': pesan})
    if hasil['error']:
        return hasil

    df[angka.columns] = angka
    for unit, g in df.groupby('unit', sort=False):
        siklus = g['cycle'].to_numpy()
        if len(g) < 10:
            hasil['peringatan'].append({'kode': 'terlalu_pendek', 'unit': unit,
                                        'pesan': f'Mesin {unit} hanya punya {len(g)} siklus; minimal 10.'})
            continue
        if not np.array_equal(siklus, np.arange(1, len(g) + 1)):
            hasil['peringatan'].append({'kode': 'siklus_tidak_urut', 'unit': unit,
                                        'pesan': f'Siklus mesin {unit} tidak mulai dari 1 atau melompat.'})
            continue
        if bundle is not None:
            jarak = bundle['kmeans_cond'].transform(g[['set1', 'set2', 'set3']]).min(axis=1)
            if (jarak > AMBANG_KONDISI).any():
                b = int(np.argmax(jarak > AMBANG_KONDISI))
                hasil['peringatan'].append({'kode': 'kondisi_asing', 'unit': unit, 'baris': int(g.index[b]) + 1,
                                            'pesan': 'Setting operasional di luar enam kondisi yang dikenal.'})
                continue
        hasil['mesin_lolos'].append(unit)

    hasil['ok'] = bool(hasil['mesin_lolos'])
    if not hasil['ok']:
        hasil['error'].append({'kode': 'csv_tidak_valid', 'pesan': 'Tidak ada mesin yang lolos validasi.'})
    return hasil
