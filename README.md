# RF Spectrum Analyzer Dashboard

Dashboard web untuk analisis spektrum frekuensi radio - Balai Monitor Spektrum Frekuensi Radio Kelas II Lampung

## 🎯 Fitur Utama

- **Upload & Parsing CSV**: Upload file CSV dari spectrum analyzer dengan format khusus (separator `^`)
- **Analisis Spektrum**: Perhitungan okupansi, noise floor, deteksi peak, dan deteksi anomali
- **Visualisasi Interaktif**: Grafik spektrum dengan Plotly.js, klik point untuk navigasi ke peta
- **Peta Lokasi**: Tampilan lokasi pengukuran dan stasiun berizin dengan Leaflet/OpenStreetMap
- **Fullscreen Mode**: Mode fullscreen untuk peta, grafik, dan tabel sinyal
- **Laporan PDF**: Generate laporan profesional secara otomatis
- **Multi-Band Support**: Analisis untuk berbagai band frekuensi (FM, VHF, UHF, dll)
- **Database Stasiun**: Upload data lisensi dari file Excel (POSTEL format)
- **Mobile Responsive**: Tampilan responsif untuk desktop dan mobile

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
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

Backend akan berjalan di `http://localhost:8002`

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

Frontend akan berjalan di `http://localhost:3002`

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
│   │   ├── license_parser.py    # Excel license parser
│   │   ├── report_generator.py  # PDF report generator
│   │   └── licensed_stations.json # Fallback database stasiun
│   ├── tests/
│   │   ├── test_parser.py
│   │   └── test_analyzer.py
│   ├── uploads/                 # Uploaded CSV files
│   ├── reports/                 # Generated PDF reports
│   ├── requirements.txt
│   ├── pytest.ini
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx         # Home page
│   │   │   ├── analysis/[id]/page.tsx # Analysis detail page
│   │   │   └── licenses/page.tsx # License management page
│   │   ├── components/
│   │   │   ├── FileUpload.tsx
│   │   │   ├── AnalysisList.tsx
│   │   │   ├── SpectrumChart.tsx
│   │   │   ├── AnalysisResults.tsx
│   │   │   └── MapView.tsx
│   │   ├── lib/
│   │   │   ├── api.ts           # API client
│   │   │   └── utils.ts         # Utility functions
│   │   └── types/
│   │       └── modules.d.ts     # TypeScript declarations
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
CORS_ORIGINS=http://localhost:3002,http://127.0.0.1:3002
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8002
```

### Database Stasiun Berlisensi

Upload file Excel lisensi melalui halaman **Database Lisensi** (`/licenses`):

1. Buka menu "Database Lisensi" di sidebar
2. Klik "Upload File Excel"
3. Pilih file Excel dengan format POSTEL (kolom: CLNT_ID, CLNT_NAME, SID_FREQ, SID_LAT, SID_LONG, CALLSIGN, EQ_MFR, EQ_MDL, EMIS_CLASS_1)
4. Data akan otomatis di-parse dan disimpan ke database

**Format Excel yang didukung:**
- File `.xlsx` dengan header kolom standar POSTEL
- Koordinat dalam format desimal (latitude/longitude)
- Frekuensi dalam MHz

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

### Fitur Keamanan Built-in

1. **Rate Limiting** - Proteksi DDoS dengan pembatasan request per IP
   - Upload: 10 request/menit
   - Delete: 5-20 request/menit
   - API umum: 60 request/menit

2. **File Size Validation** - Batas ukuran file upload (default 50MB)

3. **Input Sanitization** - Validasi dan sanitasi input untuk mencegah SQL injection

4. **HTTP Basic Authentication** - Proteksi endpoint sensitif (upload, delete)

5. **CORS Protection** - Pembatasan origin yang diizinkan

### Konfigurasi Keamanan (.env)

```env
# Aktifkan autentikasi untuk production
ENABLE_AUTH=true
AUTH_USERNAME=admin
AUTH_PASSWORD=your-strong-password-here

# Rate limiting
RATE_LIMIT_PER_MINUTE=60
MAX_UPLOAD_SIZE_MB=50

# CORS - batasi ke domain production
CORS_ORIGINS=https://yourdomain.com

# Secret key untuk JWT (gunakan random string panjang)
SECRET_KEY=your-very-long-random-secret-key-here
```

### Best Practices Production

- Set `ENABLE_AUTH=true` untuk mengaktifkan autentikasi
- Gunakan SECRET_KEY yang kuat (min 32 karakter random)
- Ubah AUTH_USERNAME dan AUTH_PASSWORD default
- Batasi CORS_ORIGINS hanya ke domain yang diizinkan
- Jangan expose database credentials
- Gunakan HTTPS di production
- Gunakan reverse proxy (Nginx) dengan rate limiting tambahan

## 🚢 Deployment

### Deployment ke VPS (Production Ready)

#### 1. Infrastruktur yang Dibutuhkan
- VPS (Ubuntu 22.04/20.04)
- Domain/subdomain: `rf-spektrum-analyzer.farzani.space`
- Python 3.11+, Node.js 18+, SQLite (local file)
- Reverse proxy (Nginx) + Let's Encrypt untuk HTTPS

#### 2. DNS Configuration
1. Masuk panel DNS domain
2. Tambahkan record:
   - **Type**: `A`
   - **Host**: `rf-spektrum-analyzer`
   - **Value**: `IP VPS`
   - **TTL**: 5 menit
3. Tunggu propagasi (biasanya < 15 menit)

#### 3. Backend Deployment (FastAPI + Uvicorn + Nginx)

**3.1 Setup Server**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3.11 python3.11-venv python3-pip nginx certbot python3-certbot-nginx git unzip -y
```

**3.2 Clone & Install**
```bash
cd /var/www
sudo git clone https://github.com/juanpradana/RF-Spectrum-Analyzer-Dashboard.git rf-spectrum
cd rf-spectrum/backend
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**3.3 Konfigurasi .env**
```bash
cp .env.example .env
nano .env
```

Set konfigurasi:
```env
DATABASE_URL=sqlite:////var/www/rf-spectrum/backend/rf_analyzer.db
UPLOAD_DIR=/var/www/rf-spectrum/backend/uploads
REPORTS_DIR=/var/www/rf-spectrum/backend/reports
SECRET_KEY=generate_random_32_chars
AUTH_USERNAME=admin
AUTH_PASSWORD=strong_password
CORS_ORIGINS=https://rf-spektrum-analyzer.farzani.space
ENABLE_AUTH=true
RATE_LIMIT_PER_MINUTE=60
MAX_UPLOAD_SIZE_MB=50
```

**3.4 Folder Permissions**
```bash
mkdir -p uploads reports
sudo chown -R www-data:www-data /var/www/rf-spectrum/backend
sudo chmod -R 755 /var/www/rf-spectrum/backend
sudo chmod -R 775 /var/www/rf-spectrum/backend/uploads
sudo chmod -R 775 /var/www/rf-spectrum/backend/reports
```

**3.5 Systemd Service**

Buat file `/etc/systemd/system/rf-spectrum-backend.service`:
```ini
[Unit]
Description=RF Spectrum Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/rf-spectrum/backend
Environment="PATH=/var/www/rf-spectrum/backend/venv/bin"
ExecStart=/var/www/rf-spectrum/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8002
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now rf-spectrum-backend
sudo systemctl status rf-spectrum-backend
```

**3.6 Nginx Reverse Proxy**

Buat file `/etc/nginx/sites-available/rf-spectrum`:
```nginx
server {
    listen 80;
    server_name rf-spektrum-analyzer.farzani.space;
    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Enable & reload:
```bash
sudo ln -s /etc/nginx/sites-available/rf-spectrum /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**3.7 HTTPS (Let's Encrypt)**
```bash
sudo certbot --nginx -d rf-spektrum-analyzer.farzani.space
```
Pilih redirect all HTTP to HTTPS.

#### 4. Frontend Deployment (Next.js 14)

**4.1 Build Static**
```bash
cd /var/www/rf-spectrum/frontend
npm install
cp .env.local.example .env.local
# Edit .env.local: NEXT_PUBLIC_API_URL=https://rf-spektrum-analyzer.farzani.space
npm run build
```

**4.2 Jalankan via PM2**
```bash
npm install -g pm2
pm2 start npm --name rf-frontend -- start -- -p 3002
pm2 save
pm2 startup
```

**4.3 Nginx Frontend Proxy**

Update `/etc/nginx/sites-available/rf-spectrum`:
```nginx
server {
    listen 80;
    server_name rf-spektrum-analyzer.farzani.space;
    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:3002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8002/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Reload Nginx dan jalankan certbot lagi:
```bash
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d rf-spektrum-analyzer.farzani.space
```

#### 5. Security & Hardening

**Firewall (UFW)**
```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

**Security Checklist**
- ✅ Set `ENABLE_AUTH=true` di backend `.env`
- ✅ Database dan folder uploads/reports punya permission `www-data`
- ✅ Jadwalkan backup database (cron rsync)
- ✅ Monitor logs:
  ```bash
  journalctl -u rf-spectrum-backend -f
  tail -f /var/log/nginx/access.log
  ```

#### 6. Routine Deployment Updates

```bash
# SSH ke VPS
ssh user@your-vps-ip

# Update code
cd /var/www/rf-spectrum
sudo git pull

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart rf-spectrum-backend

# Update frontend
cd ../frontend
npm install
npm run build
pm2 reload rf-frontend
```

### Alternative: Cloud Platforms

**Backend (Render/Heroku)**
1. Push code ke Git repository
2. Connect repository ke Render/Heroku
3. Set environment variables
4. Deploy

**Frontend (Vercel)**
1. Push code ke Git repository
2. Import project di Vercel
3. Set `NEXT_PUBLIC_API_URL` ke URL backend
4. Deploy

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

### Version 1.1.0 (2025-12-16)
- **Click-to-Map Navigation**: Klik point pada grafik untuk navigasi ke lokasi di peta
- **Fullscreen Mode**: Mode fullscreen untuk peta, grafik, dan tabel sinyal
- **Mobile Responsive**: Tampilan responsif untuk semua ukuran layar
- **Peak Detection**: Algoritma deteksi peak yang lebih akurat
- **Auto Threshold**: Perhitungan threshold otomatis berdasarkan noise floor
- **Excel License Upload**: Upload data lisensi dari file Excel POSTEL
- **Enhanced PDF Report**: Laporan PDF yang lebih rapi dan lengkap
- **Station Markers**: Tampilan marker stasiun berizin di peta
- **Delete Analysis**: Fitur hapus analisis dari history

### Version 1.0.0 (2025-12-15)
- Initial release
- Upload & parsing CSV
- Analisis spektrum multi-band
- Visualisasi interaktif
- PDF report generation
- Database stasiun berlisensi
