# SIAGA Jantung – Contoh Struktur Proyek

Proyek ini adalah contoh implementasi sederhana untuk sistem analisa risiko penyakit jantung
dengan:

- **Backend klinis**: Streamlit (`streamlit_app/app.py`)
- **Model ML**: XGBoost yang dibungkus dalam pipeline (`ml/cardio_model.py`)
- **Layer aplikasi**: `appheart` (sebagai placeholder untuk modul auth / API)

> Catatan: File ini adalah *template*. Anda perlu menambahkan file model
> `best_xgb_pipeline.joblib` hasil training dari `cardio.py` ke folder `ml/`.

## 1. Tech Stack

### Bahasa & Runtime
- Python 3.10+

### Machine Learning
- `pandas`
- `numpy`
- `scikit-learn`
- `xgboost`
- `imbalanced-learn`
- `joblib`

### Backend Klinis & UI
- `streamlit` – antarmuka input dan output untuk tenaga kesehatan.

### (Opsional) API Aplikasi
- `fastapi`
- `uvicorn`

## 2. Struktur Proyek

```text
siaga_heart_app/
├── README.md
├── requirements.txt
├── ml/
│   ├── cardio_model.py
│   └── best_xgb_pipeline.joblib   # <-- Anda tempatkan sendiri di sini
├── streamlit_app/
│   └── app.py
└── appheart/
    ├── __init__.py
    └── api/
        ├── __init__.py
        └── predict.py
```

## 3. Integrasi & Alur Kerja

### 3.1. Model ML (XGBoost)

- Anda melakukan training model di notebook / script `cardio.py` (di luar contoh ini).
- Simpan pipeline (ColumnTransformer + SMOTE + XGBClassifier) ke file
  `best_xgb_pipeline.joblib` menggunakan `joblib.dump(...)`.
- Letakkan file tersebut di folder `ml/`.

`ml/cardio_model.py`:
- Memuat file `best_xgb_pipeline.joblib` saat pertama kali dipanggil.
- Menyediakan fungsi:
  - `predict_proba(data: dict) -> float`
  - `predict_label(data: dict, threshold: float = 0.5) -> int`

### 3.2. Streamlit sebagai Backend Klinis

`streamlit_app/app.py`:

- Menyediakan UI untuk tenaga kesehatan:
  - Input usia, jenis kelamin, tinggi, berat, tekanan darah (sistolik/diastolik),
    kolesterol, glukosa, merokok, alkohol, aktivitas fisik.
  - Menghitung **BMI** dan **MAP** otomatis.
  - Memanggil `CardioRiskModel` untuk mendapatkan probabilitas risiko penyakit jantung.
  - Menampilkan hasil dalam bentuk:
    - Persentase risiko.
    - Kategori (Rendah / Sedang / Tinggi).
    - Ringkasan interpretasi singkat.

- Aplikasi ini dapat dijalankan dengan:

```bash
cd siaga_heart_app
pip install -r requirements.txt
streamlit run streamlit_app/app.py
```

### 3.3. Integrasi dengan `appheart` (Opsional)

`appheart/api/predict.py`:

- Menyediakan contoh **endpoint FastAPI** `/predict` yang:
  - Menerima JSON dengan field yang sama seperti UI Streamlit.
  - Menggunakan `CardioRiskModel` untuk prediksi.
  - Mengembalikan probabilitas dan label risiko.

Integrasi opsional:

1. Jalankan FastAPI:

```bash
uvicorn appheart.api.predict:app --reload
```

2. Ubah `streamlit_app/app.py`:
   - Alih-alih import langsung `CardioRiskModel`, Anda dapat mengirim HTTP request
     ke `http://localhost:8000/predict` menggunakan `requests.post(...)`.

Dengan arsitektur ini:

- **Tenaga kesehatan** hanya berinteraksi dengan **Streamlit**.
- Streamlit bisa:
  - langsung memakai model (sederhana), atau
  - berperan sebagai *client* ke API FastAPI (lebih fleksibel untuk multi-client).
# SIAGA_DETEKSI-JANTUNG
