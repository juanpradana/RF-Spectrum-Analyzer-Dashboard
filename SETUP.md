# Setup Guide - RF Spectrum Analyzer Dashboard

## Quick Start (Development)

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env

# Run backend server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend akan berjalan di: http://localhost:8000

API Documentation: http://localhost:8000/docs

### 2. Frontend Setup

```bash
# Navigate to frontend directory (new terminal)
cd frontend

# Install dependencies
npm install

# Create environment file
copy .env.local.example .env.local

# Run development server
npm run dev
```

Frontend akan berjalan di: http://localhost:3000

## Testing dengan Sample Data

1. Buka browser ke http://localhost:3000
2. Upload file CSV sample yang ada di root directory:
   - `Field Strength vs. Channel (Task 1924)_Bandar Lampung 30 Menit.csv`
3. Setelah upload berhasil, klik pada analisis yang muncul
4. Pilih Band 1 (FM: 87-108 MHz)
5. Atur threshold (default 50 dBµV/m)
6. Klik "Analisis Spektrum"
7. Lihat hasil analisis dan grafik
8. Klik "Download PDF" untuk generate laporan

## Verifikasi Instalasi

### Backend Health Check

```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "message": "RF Spectrum Analyzer API",
  "version": "1.0.0",
  "status": "running"
}
```

### Frontend Check

Buka browser ke http://localhost:3000 - Anda harus melihat halaman upload dengan header "RF Spectrum Analyzer"

## Running Tests

### Backend Tests

```bash
cd backend
pytest
```

Expected: All tests should pass

### Manual API Testing

```bash
# Upload file
curl -X POST http://localhost:8000/api/upload \
  -F "file=@../Field Strength vs. Channel (Task 1924)_Bandar Lampung 30 Menit.csv"

# Get analyses list
curl http://localhost:8000/api/analyses

# Get specific analysis (replace {id} with actual ID)
curl http://localhost:8000/api/analyses/{id}
```

## Troubleshooting

### Port Already in Use

**Backend (Port 8000):**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

**Frontend (Port 3000):**
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:3000 | xargs kill -9
```

### Python Dependencies Error

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Node Modules Error

```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Database Error

```bash
# Delete existing database and let it recreate
cd backend
rm rf_analyzer.db
# Restart backend server
```

### CORS Error

Pastikan `CORS_ORIGINS` di backend/.env mencakup URL frontend:
```env
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Production Deployment

### Environment Variables

**Backend (.env):**
```env
DATABASE_URL=postgresql://user:pass@host:5432/dbname  # Use PostgreSQL in production
UPLOAD_DIR=./uploads
REPORTS_DIR=./reports
SECRET_KEY=<generate-strong-random-key>
AUTH_USERNAME=<your-username>
AUTH_PASSWORD=<strong-password>
CORS_ORIGINS=https://yourdomain.com
```

**Frontend (.env.local):**
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

### Build for Production

**Backend:**
```bash
cd backend
pip install -r requirements.txt
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Frontend:**
```bash
cd frontend
npm run build
npm start
```

## System Requirements

### Minimum
- CPU: 2 cores
- RAM: 2GB
- Storage: 5GB
- Python 3.9+
- Node.js 18+

### Recommended
- CPU: 4 cores
- RAM: 4GB
- Storage: 20GB
- Python 3.11+
- Node.js 20+

## Next Steps

1. Customize `backend/app/licensed_stations.json` dengan data stasiun lokal
2. Adjust threshold defaults sesuai kebutuhan
3. Setup backup untuk database
4. Configure logging untuk production
5. Setup monitoring (optional)

## Support

Jika mengalami masalah, check:
1. Logs di terminal backend dan frontend
2. Browser console untuk frontend errors
3. API documentation di http://localhost:8000/docs
4. README.md untuk informasi lebih detail
