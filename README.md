# RF Spectrum Analyzer Dashboard

Dashboard web untuk analisis spektrum frekuensi radio - Balai Monitor Spektrum Frekuensi Radio Kelas II Lampung

## 🎯 Fitur Utama

- **Upload & Parsing CSV**: Upload file CSV dari spectrum analyzer dengan format khusus (separator `^`)
- **Analisis Spektrum**: Perhitungan okupansi, noise floor, dan deteksi anomali
- **Visualisasi Interaktif**: Grafik spektrum dengan Plotly.js
- **Peta Lokasi**: Tampilan lokasi pengukuran dengan Leaflet/OpenStreetMap
- **Laporan PDF**: Generate laporan profesional secara otomatis
- **Multi-Band Support**: Analisis untuk berbagai band frekuensi (FM, VHF, UHF, dll)
- **Database Stasiun**: Identifikasi stasiun berlisensi

## 🏗️ Arsitektur

- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **Backend**: Python FastAPI
- **Database**: SQLite (dapat di-upgrade ke PostgreSQL)
- **Visualisasi**: Plotly.js + React-Plotly
- **Maps**: Leaflet + OpenStreetMap
- **PDF**: ReportLab + Kaleido

## 📋 Prasyarat

- **Node.js** 18+ dan npm/yarn
- **Python** 3.9+
- **pip** untuk instalasi package Python

## 🚀 Instalasi

### Backend Setup

1. Masuk ke direktori backend:
```bash
cd backend
```

2. Buat virtual environment:
```bash
python -m venv venv
```

3. Aktifkan virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Copy file environment:
```bash
copy .env.example .env
```

6. Edit `.env` dan sesuaikan konfigurasi (opsional)

7. Jalankan server:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend akan berjalan di `http://localhost:8000`

### Frontend Setup

1. Masuk ke direktori frontend:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Copy file environment:
```bash
copy .env.local.example .env.local
```

4. Jalankan development server:
```bash
npm run dev
```

Frontend akan berjalan di `http://localhost:3000`

## 📁 Struktur Project

```
RF-Spectrum-Analyzer-Dashboard/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration settings
│   │   ├── database.py          # Database models & setup
│   │   ├── parser.py            # CSV parser
│   │   ├── analyzer.py          # Spectrum analysis engine
│   │   ├── report_generator.py # PDF report generator
│   │   └── licensed_stations.json # Database stasiun berlisensi
│   ├── tests/
│   │   ├── test_parser.py
│   │   └── test_analyzer.py
│   ├── requirements.txt
│   ├── pytest.ini
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx         # Home page
│   │   │   └── analysis/[id]/page.tsx # Analysis detail page
│   │   ├── components/
│   │   │   ├── FileUpload.tsx
│   │   │   ├── AnalysisList.tsx
│   │   │   ├── SpectrumChart.tsx
│   │   │   ├── AnalysisResults.tsx
│   │   │   └── MapView.tsx
│   │   └── lib/
│   │       ├── api.ts           # API client
│   │       └── utils.ts         # Utility functions
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── next.config.js
└── README.md
```

## 🔧 Konfigurasi

### Backend (.env)

```env
DATABASE_URL=sqlite:///./rf_analyzer.db
UPLOAD_DIR=./uploads
REPORTS_DIR=./reports
SECRET_KEY=your-secret-key-here
AUTH_USERNAME=admin
AUTH_PASSWORD=changeme123
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Database Stasiun Berlisensi

Edit file `backend/app/licensed_stations.json` untuk menambah/update data stasiun:

```json
[
  {
    "name": "RRI Pro 1 Lampung",
    "callsign": "RRI",
    "frequency": 87.7,
    "location": "Bandar Lampung"
  }
]
```

## 📊 Format File CSV

File CSV harus menggunakan format berikut:

```csv
sep=^
Task ID^Storage Interval^Operator ID^...^Location (lat)^Location (lon)^...
1924^15 secs^UPT-LAMPUNG^...^-5.357882^105.216545^...

Band #^Start Frequency (MHz)^Stop Frequency (MHz)^Bandwidth (kHz)
1^87.000000^108.000000^50.00000
2^108.000000^137.000000^6.25000

Channel No.^Frequency (MHz)^Maximum Field Strength (dBuV/m)^Average Field Strength (dBuV/m)
1^87.000000^44^36
2^87.050000^47^43
```

**Penting:**
- Separator: `^` (caret)
- Tiga bagian: Metadata, Bands, Channels
- Encoding: UTF-8

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests (jika ada)

```bash
cd frontend
npm test
```

## 📖 Penggunaan

1. **Upload File CSV**
   - Buka dashboard di browser
   - Klik area upload atau pilih file CSV
   - File akan otomatis di-parse dan disimpan

2. **Analisis Spektrum**
   - Pilih analisis dari daftar
   - Pilih band yang ingin dianalisis
   - Atur threshold okupansi (default: 50 dBµV/m)
   - Klik "Analisis Spektrum"

3. **Lihat Hasil**
   - Statistik okupansi
   - Grafik spektrum interaktif
   - Tabel 20 sinyal terkuat
   - Daftar channel terisi
   - Deteksi anomali

4. **Generate Laporan PDF**
   - Klik tombol "Download PDF"
   - Laporan akan di-generate dan otomatis terdownload

## 🔒 Keamanan

- Gunakan SECRET_KEY yang kuat di production
- Ubah AUTH_USERNAME dan AUTH_PASSWORD default
- Batasi CORS_ORIGINS sesuai domain yang diizinkan
- Jangan expose database credentials
- Gunakan HTTPS di production

## 🚢 Deployment

### Backend (Render/Heroku)

1. Push code ke Git repository
2. Connect repository ke Render/Heroku
3. Set environment variables
4. Deploy

### Frontend (Vercel)

1. Push code ke Git repository
2. Import project di Vercel
3. Set `NEXT_PUBLIC_API_URL` ke URL backend
4. Deploy

### Self-Hosted

1. Setup reverse proxy (Nginx/Apache)
2. Configure SSL certificate
3. Setup systemd services untuk auto-restart
4. Configure firewall

## 🐛 Troubleshooting

### Backend tidak bisa start
- Pastikan semua dependencies ter-install
- Check Python version (3.9+)
- Periksa file .env

### Frontend tidak bisa connect ke backend
- Pastikan backend sudah running
- Check NEXT_PUBLIC_API_URL di .env.local
- Periksa CORS settings di backend

### PDF generation error
- Install kaleido: `pip install kaleido`
- Check write permissions di REPORTS_DIR

### CSV parsing error
- Pastikan separator adalah `^`
- Check encoding file (harus UTF-8)
- Pastikan format sesuai contoh

## 📝 Lisensi

Internal use - Balai Monitor Spektrum Frekuensi Radio Kelas II Lampung

## 👥 Kontributor

- Development Team - Balai Monitor SFR Lampung

## 📞 Support

Untuk pertanyaan atau issue, hubungi tim IT Balai Monitor SFR Lampung.

## 🔄 Changelog

### Version 1.0.0 (2025-12-15)
- Initial release
- Upload & parsing CSV
- Analisis spektrum multi-band
- Visualisasi interaktif
- PDF report generation
- Database stasiun berlisensi
