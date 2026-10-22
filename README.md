# PrognoSense

Sistem *predictive maintenance* untuk mesin turbofan: memperkirakan sisa umur mesin (RUL) dari data sensor, lalu memutuskan kapan mesin sebaiknya dirawat. Dibangun di atas data NASA C-MAPSS FD002 + FD004 dan menggabungkan tiga paradigma machine learning:

| Paradigma | Model | Tugas |
| --- | --- | --- |
| Unsupervised | K-Means (K = 6) | Mengelompokkan setting operasional menjadi 6 kondisi, untuk normalisasi sensor per kondisi |
| Unsupervised | K-Means (K = 3) | Membagi kondisi mesin menjadi tahap kesehatan |
| Supervised | LightGBM | Menebak RUL dari 43 fitur jendela 10 siklus |
| Reinforcement | Q-Learning | Memilih *lanjut* atau *rawat* dari RUL prediksi dan tahap kesehatan |

## Alur sistem

Training berjalan **sekali** di Google Colab, dan server **tidak pernah melatih ulang** apa pun. Titik serah terimanya adalah `models/v1/` dan `data/results/`.

```
data/raw (NASA)
  └─ 01 EDA + split mesin A/B/C ─────────────── data/splits.json
      └─ 02 K-Means kondisi + z-score ──────── kmeans_cond.joblib, norm_stats.json
          └─ 03 fitur + 5 kandidat model ───── rul_model.joblib, rul_evaluasi.json
              └─ K-Means tahap kesehatan ───── health_kmeans.joblib
              └─ prediksi kelompok B & C ───── predictions.csv
                  └─ 04 Q-Learning (B) ────── qtable_r{50,100,200}.npy, evaluasi.json
                      └─ 06 ekspor web (C) ── armada_r*.json, mesin/r*/{unit}.json

Server: Vue + nginx ──/api──► FastAPI ──► engine.validate ──► engine.predict
                                          (memuat models/v1 sekali saat menyala)
```

Pembagian data dilakukan **per mesin** dengan `seed = 42`:

| Kelompok | Porsi | Dipakai untuk |
| --- | --- | --- |
| A | 60% (305 mesin) | Melatih K-Means, statistik normalisasi, model RUL |
| B | 20% (102 mesin) | Memilih model RUL, melatih agen RL, memilih parameter strategi pembanding |
| C | 20% (102 mesin) | Evaluasi akhir semua strategi dan isi dasbor |
| Test resmi NASA | 507 mesin | Melaporkan RMSE model RUL |

## Hasil

**Model RUL** (RMSE dalam siklus; test dinilai di siklus terakhir tiap mesin, RUL dipotong di 125):

| Model | RMSE B | RMSE test |
| --- | ---: | ---: |
| Baseline rata-rata | 41,24 | 45,26 |
| Regresi linear (Ridge) | 19,97 | 22,02 |
| kNN (k = 15) | 17,16 | 19,13 |
| Random Forest | 15,81 | 16,47 |
| **LightGBM** (terpilih di B) | **15,69** | 16,90 |

**Strategi perawatan** (kelompok C, rasio biaya gagal : rawat = 100 : 10):

| Strategi | Gagal | Siklus terbuang | Siklus produktif |
| --- | ---: | ---: | ---: |
| Agen Q-Learning | 0,98% | 11,8 | 218,9 |
| Ambang RUL (T = 20) | 0% | 19,4 | 211,2 |
| Periodik (N = 140) | 2,94% | 94,6 | 138,8 |
| Oracle (acuan) | 0% | 1,0 | 229,6 |

Agen lebih hemat siklus daripada aturan ambang, tetapi membiarkan 1 dari 102 mesin rusak.

## Struktur repo

```
engine/            paket Python yang dipakai notebook dan backend
  schema.py        nama kolom, 14 sensor aktif
  data.py          loader + ID mesin + splits
  conditions.py    kondisi operasi + normalisasi
  health.py        tahap kesehatan
  features.py      43 fitur jendela + label RUL
  rul.py           kandidat model + metrik
  rl_env.py        lingkungan RL (MaintenanceEnv)
  qlearning.py     agen Q-Learning
  evaluate.py      strategi pembanding + evaluasi.json
  validate.py      validasi CSV upload
  predict.py       load() + predict() untuk server
notebooks/         01 EDA · 02 kondisi & kesehatan · 03 fitur & RUL · 04 Q-Learning · 06 ekspor
models/v1/         artefak model + metadata.json (versi library)
data/results/      JSON yang dibaca web + predictions.csv
backend/           FastAPI
frontend/          Vue 3 + Vite + Tailwind + shadcn-vue + Chart.js
```

## Menjalankan secara lokal

Butuh Python 3.12+ dan Node 20.19+.

```bash
# backend (dari root repo)
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --port 8000

# frontend (terminal lain)
cd frontend
npm install
npm run dev          # proxy Vite meneruskan /api dan /health ke port 8000
```

Dokumentasi API interaktif tersedia di `http://127.0.0.1:8000/docs`.

## Melatih ulang di Colab

Jalankan notebook berurutan; setiap notebook punya sel pertama untuk meng-clone repo dan menyalin data dari Google Drive (atur `PATH_DRIVE`).

1. `01_eda_cleaning.ipynb` dan `02_kondisi_kesehatan.ipynb`
2. `03_fitur_rul.ipynb`: perbandingan algoritma (Bagian A) dan model final (Bagian B)
3. `04_qlearning.ipynb`: tiga Q-table dan `evaluasi.json`
4. `06_ekspor_hasil.ipynb`: file untuk Dasbor dan Detail mesin

Data mentah NASA tidak di-commit. Versi library yang dipakai saat training tercatat di `models/v1/metadata.json` dan dikunci di `backend/requirements.txt`; model `joblib` dari versi scikit-learn lain bisa gagal dimuat atau berubah hasilnya.

## Deploy dengan Portainer

1. Portainer → **Stacks → Add stack → Repository**
2. Repository URL: `https://github.com/Arsha8Anuga/PrognoSense`, Compose path: `docker-compose.yml`
3. **Environment variables** (opsional):

   | Variabel | Default | Fungsi |
   | --- | --- | --- |
   | `PORT` | `8080` | Port di server yang membuka web |
   | `CORS_ORIGIN` | `*` | Asal yang boleh memanggil API langsung |

4. Deploy, lalu buka `http://<ip-server>:<PORT>`

Hanya container `frontend` (nginx) yang membuka port; `backend` hanya bisa diakses lewat nginx. Model dan data hasil ikut dibangun ke dalam image backend, jadi untuk memperbarui model cukup push ke Git lalu **Pull and redeploy**. Log permintaan disimpan di volume `logs` (`requests.jsonl`).

Tanpa Portainer: `PORT=8080 docker compose up -d --build`.

## API

| Endpoint | Isi |
| --- | --- |
| `GET /health` | Status, versi model, waktu dimuat |
| `GET /api/armada?rasio=100` | Ringkasan dan daftar mesin kelompok C |
| `GET /api/mesin/{unit}?rasio=100` | Lintasan per siklus satu mesin (mis. `FD004_17`) |
| `GET /api/kondisi` | Hasil clustering kondisi dan tahap kesehatan |
| `GET /api/evaluasi` | Perbandingan model RUL, strategi, kurva reward, policy |
| `POST /api/prediksi` | Upload CSV/TXT (`file`, `rasio`, `sampai_rusak`) → validasi + prediksi |

`rasio` adalah biaya gagal berbanding biaya rawat 10: `50`, `100`, atau `200`. Upload menerima CSV dengan header `unit, cycle, set1, set2, set3, s1 … s21`, atau file teks NASA tanpa header, maksimal 20 MB. Mesin ditolak bila siklusnya tidak urut, kurang dari 10 siklus, atau setting operasionalnya berjarak lebih dari 0,05 dari keenam kondisi yang dikenal.

## Keterbatasan

- Data simulasi, bukan data pabrik; kondisi operasinya diskrit.
- Degradasi diputar ulang dari data: agen hanya memilih kapan lintasan dihentikan.
- RUL di atas 125 hanya bisa ditebak sebagai "≥ 125".
- Tahap "kritis" lebih mewakili mode kerusakan fan di FD004 daripada tingkat keparahan.
- Enam bin RUL terlalu kasar, sehingga rasio 200 menghasilkan kebijakan yang sama dengan rasio 100.
- Belum ada database, login, maupun riwayat prediksi; semua hasil bersifat read-only dan upload tidak menyimpan apa pun.

## Pengembangan lanjutan

Model sekuens (LSTM / 1D-CNN), GMM atau HDBSCAN sebagai pembanding clustering, state RL yang lebih halus atau DQN, peringatan `sensor_ekstrem`, serta penyimpanan riwayat upload untuk training ulang.

## Tim

| Peran | Bagian |
| --- | --- |
| Orang 1 · EDA & data cleaning | Split, K-Means kondisi dan kesehatan, normalisasi |
| Orang 2 · Feature engineering & model training | Fitur, model RUL, Q-Learning, ekspor hasil |
| Orang 3 · Evaluation | Lingkungan RL, strategi pembanding, `evaluasi.json` |
| Orang 4 · Deployment & monitoring | Backend, frontend, deploy |
