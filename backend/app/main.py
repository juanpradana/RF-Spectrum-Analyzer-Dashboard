from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd
import os
import uuid
from datetime import datetime

from .config import settings
from .database import get_db, init_db, Analysis, LicensedStation
from .parser import CSVParser
from .license_parser import LicenseParser
from .analyzer import SpectrumAnalyzer
from .report_generator import ReportGenerator, create_chart_image

app = FastAPI(title="RF Spectrum Analyzer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def read_root():
    return {
        "message": "RF Spectrum Analyzer API",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    try:
        content = await file.read()
        
        parser = CSVParser(content)
        parsed_data = parser.parse()
        
        file_id = str(uuid.uuid4())
        file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}.csv")
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Convert datetime objects to strings for JSON serialization
        metadata_for_json = parsed_data['metadata'].copy()
        if 'Start Time' in metadata_for_json and isinstance(metadata_for_json['Start Time'], datetime):
            metadata_for_json['Start Time'] = metadata_for_json['Start Time'].isoformat()
        if 'Stop Time' in metadata_for_json and isinstance(metadata_for_json['Stop Time'], datetime):
            metadata_for_json['Stop Time'] = metadata_for_json['Stop Time'].isoformat()
        
        analysis = Analysis(
            task_id=parsed_data['metadata'].get('Task ID', 'Unknown'),
            filename=file.filename,
            location_lat=parsed_data['metadata'].get('Location (lat)'),
            location_lon=parsed_data['metadata'].get('Location (lon)'),
            start_time=parsed_data['metadata'].get('Start Time'),
            stop_time=parsed_data['metadata'].get('Stop Time'),
            station_name=parsed_data['metadata'].get('Station Name'),
            operator_id=parsed_data['metadata'].get('Operator ID'),
            analysis_metadata=metadata_for_json,
            bands=parsed_data['bands']
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        return {
            "id": analysis.id,
            "file_id": file_id,
            "filename": file.filename,
            "metadata": parsed_data['metadata'],
            "bands": parsed_data['bands'],
            "channels_count": parsed_data['channels_count'],
            "message": "File uploaded and parsed successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/api/analyses")
def get_analyses(db: Session = Depends(get_db)):
    analyses = db.query(Analysis).order_by(Analysis.upload_time.desc()).limit(50).all()
    
    return [{
        "id": a.id,
        "task_id": a.task_id,
        "filename": a.filename,
        "upload_time": a.upload_time,
        "location": {
            "lat": a.location_lat,
            "lon": a.location_lon
        },
        "station_name": a.station_name,
        "bands_count": len(a.bands) if a.bands else 0
    } for a in analyses]

@app.get("/api/analyses/{analysis_id}")
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return {
        "id": analysis.id,
        "task_id": analysis.task_id,
        "filename": analysis.filename,
        "upload_time": analysis.upload_time,
        "metadata": analysis.analysis_metadata,
        "bands": analysis.bands,
        "location": {
            "lat": analysis.location_lat,
            "lon": analysis.location_lon
        },
        "occupancy_results": analysis.occupancy_results,
        "report_path": analysis.report_path
    }

@app.get("/api/analyses/{analysis_id}/auto-threshold")
def get_auto_threshold(
    analysis_id: int,
    band_number: int = 1,
    margin_db: float = 10.0,
    db: Session = Depends(get_db)
):
    """
    Calculate automatic threshold based on noise floor + margin
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    try:
        file_path = None
        for filename in os.listdir(settings.UPLOAD_DIR):
            if filename.endswith('.csv'):
                full_path = os.path.join(settings.UPLOAD_DIR, filename)
                file_path = full_path
                break
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="CSV file not found")
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        parser = CSVParser(content)
        parsed_data = parser.parse()
        
        channels_df = pd.DataFrame(parsed_data['channels'])
        
        analyzer = SpectrumAnalyzer(
            channels_df,
            parsed_data['bands'],
            parsed_data['metadata'],
            db
        )
        
        auto_threshold_info = analyzer.calculate_auto_threshold(band_number, margin_db)
        
        return auto_threshold_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating auto threshold: {str(e)}")

@app.post("/api/analyses/{analysis_id}/analyze")
def analyze_spectrum(
    analysis_id: int,
    band_number: int = Form(1),
    threshold: float = Form(50.0),
    use_auto_threshold: bool = Form(False),
    margin_db: float = Form(10.0),
    db: Session = Depends(get_db)
):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    try:
        file_pattern = f"*{analysis.filename}"
        file_path = None
        
        for filename in os.listdir(settings.UPLOAD_DIR):
            if filename.endswith('.csv'):
                full_path = os.path.join(settings.UPLOAD_DIR, filename)
                file_path = full_path
                break
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="CSV file not found")
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        parser = CSVParser(content)
        parsed_data = parser.parse()
        
        channels_df = pd.DataFrame(parsed_data['channels'])
        
        analyzer = SpectrumAnalyzer(
            channels_df,
            parsed_data['bands'],
            parsed_data['metadata'],
            db
        )
        
        results = analyzer.analyze_band(band_number, threshold, use_auto_threshold, margin_db)
        
        analysis.occupancy_results = results
        db.commit()
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing spectrum: {str(e)}")

@app.post("/api/analyses/{analysis_id}/report")
def generate_report(
    analysis_id: int,
    band_number: int = Form(1),
    threshold: float = Form(50.0),
    db: Session = Depends(get_db)
):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    try:
        file_path = None
        for filename in os.listdir(settings.UPLOAD_DIR):
            if filename.endswith('.csv'):
                full_path = os.path.join(settings.UPLOAD_DIR, filename)
                file_path = full_path
                break
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="CSV file not found")
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        parser = CSVParser(content)
        parsed_data = parser.parse()
        
        channels_df = pd.DataFrame(parsed_data['channels'])
        
        analyzer = SpectrumAnalyzer(
            channels_df,
            parsed_data['bands'],
            parsed_data['metadata'],
            db
        )
        
        results = analyzer.analyze_band(band_number, threshold)
        
        report_filename = f"report_{analysis.task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        report_path = os.path.join(settings.REPORTS_DIR, report_filename)
        
        chart_filename = f"chart_{analysis.task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        chart_path = os.path.join(settings.REPORTS_DIR, chart_filename)
        
        create_chart_image(channels_df, results['band_info'], chart_path)
        
        generator = ReportGenerator(report_path)
        generator.generate_report(
            parsed_data['metadata'],
            results,
            [chart_path]
        )
        
        analysis.report_path = report_path
        db.commit()
        
        return {
            "message": "Report generated successfully",
            "report_path": report_path,
            "filename": report_filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

@app.get("/api/reports/{filename}")
def download_report(filename: str):
    file_path = os.path.join(settings.REPORTS_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report not found")
    
    return FileResponse(
        file_path,
        media_type='application/pdf',
        filename=filename
    )

@app.get("/api/analyses/{analysis_id}/channels")
def get_channels(
    analysis_id: int,
    band_number: Optional[int] = None,
    db: Session = Depends(get_db)
):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    try:
        file_path = None
        for filename in os.listdir(settings.UPLOAD_DIR):
            if filename.endswith('.csv'):
                full_path = os.path.join(settings.UPLOAD_DIR, filename)
                file_path = full_path
                break
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="CSV file not found")
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        parser = CSVParser(content)
        parsed_data = parser.parse()
        
        channels_df = pd.DataFrame(parsed_data['channels'])
        
        if band_number:
            band = parsed_data['bands'][band_number - 1]
            channels_df = channels_df[
                (channels_df['frequency'] >= band['start_freq']) &
                (channels_df['frequency'] <= band['stop_freq'])
            ]
        
        return {
            "channels": channels_df.to_dict('records'),
            "count": len(channels_df)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving channels: {str(e)}")

@app.post("/api/licenses/upload")
async def upload_license_file(
    file: UploadFile = File(...),
    replace_existing: bool = Form(False),
    db: Session = Depends(get_db)
):
    """
    Upload Excel file containing license data
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are allowed")
    
    try:
        content = await file.read()
        
        parser = LicenseParser(content, file.filename)
        licenses = parser.parse()
        
        if len(licenses) == 0:
            raise HTTPException(status_code=400, detail="No valid license data found in file")
        
        if replace_existing:
            db.query(LicensedStation).delete()
            db.commit()
        
        added_count = 0
        for license_data in licenses:
            station = LicensedStation(**license_data)
            db.add(station)
            added_count += 1
        
        db.commit()
        
        return {
            "message": "License data uploaded successfully",
            "filename": file.filename,
            "total_records": len(licenses),
            "added_count": added_count,
            "replaced_existing": replace_existing
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/api/licenses")
def get_licenses(
    province: Optional[str] = None,
    service: Optional[str] = None,
    freq_min: Optional[float] = None,
    freq_max: Optional[float] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get licensed stations with optional filters
    """
    query = db.query(LicensedStation)
    
    if province:
        query = query.filter(LicensedStation.province.ilike(f"%{province}%"))
    
    if service:
        query = query.filter(LicensedStation.service.ilike(f"%{service}%"))
    
    if freq_min is not None:
        query = query.filter(LicensedStation.freq >= freq_min)
    
    if freq_max is not None:
        query = query.filter(LicensedStation.freq <= freq_max)
    
    total = query.count()
    stations = query.offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": [{
            "id": s.id,
            "clnt_name": s.clnt_name,
            "callsign": s.callsign,
            "stn_name": s.stn_name,
            "service": s.service,
            "subservice": s.subservice,
            "freq": s.freq,
            "province": s.province,
            "city": s.city,
            "latitude": s.latitude,
            "longitude": s.longitude,
            "status_simf": s.status_simf
        } for s in stations]
    }

@app.get("/api/licenses/stats")
def get_license_stats(db: Session = Depends(get_db)):
    """
    Get statistics about licensed stations
    """
    total = db.query(LicensedStation).count()
    
    services = db.query(
        LicensedStation.service,
        db.func.count(LicensedStation.id)
    ).group_by(LicensedStation.service).all()
    
    provinces = db.query(
        LicensedStation.province,
        db.func.count(LicensedStation.id)
    ).group_by(LicensedStation.province).order_by(
        db.func.count(LicensedStation.id).desc()
    ).limit(10).all()
    
    return {
        "total_stations": total,
        "by_service": [{"service": s[0], "count": s[1]} for s in services],
        "top_provinces": [{"province": p[0], "count": p[1]} for p in provinces]
    }

@app.delete("/api/licenses")
def delete_all_licenses(db: Session = Depends(get_db)):
    """
    Delete all license data
    """
    count = db.query(LicensedStation).count()
    db.query(LicensedStation).delete()
    db.commit()
    
    return {
        "message": "All license data deleted",
        "deleted_count": count
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
