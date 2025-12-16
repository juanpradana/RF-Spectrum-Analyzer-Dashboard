from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from .config import settings

engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, index=True)
    filename = Column(String)
    file_path = Column(String, nullable=True)
    upload_time = Column(DateTime, default=datetime.utcnow)
    location_lat = Column(Float)
    location_lon = Column(Float)
    start_time = Column(DateTime)
    stop_time = Column(DateTime)
    station_name = Column(String)
    operator_id = Column(String)
    analysis_metadata = Column(JSON)
    bands = Column(JSON)
    occupancy_results = Column(JSON)
    report_path = Column(String, nullable=True)

class LicensedStation(Base):
    __tablename__ = "licensed_stations"
    
    id = Column(Integer, primary_key=True, index=True)
    clnt_id = Column(Integer, index=True)
    no_simf = Column(String, index=True)
    appl_id = Column(String)
    clnt_name = Column(String, index=True)
    callsign = Column(String, index=True)
    stn_name = Column(String)
    service = Column(String, index=True)
    subservice = Column(String)
    freq = Column(Float, index=True)
    freq_pair = Column(Float, nullable=True)
    latitude = Column(Float)
    longitude = Column(Float)
    province = Column(String, index=True)
    city = Column(String)
    district = Column(String)
    status_simf = Column(String)
    licence_date = Column(String)
    validity_date = Column(String)
    eq_mfr = Column(String, nullable=True)
    eq_mdl = Column(String, nullable=True)
    emis_class_1 = Column(String, nullable=True)
    upload_time = Column(DateTime, default=datetime.utcnow)
    source_file = Column(String)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
