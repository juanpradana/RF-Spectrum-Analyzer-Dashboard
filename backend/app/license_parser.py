import pandas as pd
from typing import Dict, List
from datetime import datetime

class LicenseParser:
    def __init__(self, file_content: bytes, filename: str):
        self.file_content = file_content
        self.filename = filename
        
    def parse(self) -> List[Dict]:
        """
        Parse Excel file containing license data
        Returns list of license records
        """
        try:
            df = pd.read_excel(self.file_content, engine='openpyxl')
            
            licenses = []
            
            for _, row in df.iterrows():
                try:
                    latitude = self._convert_to_decimal(
                        row.get('LAT_DEG'),
                        row.get('LAT_MIN'),
                        row.get('LAT_SEC'),
                        row.get('LAT_DIR_IND', 'S')
                    )
                    
                    longitude = self._convert_to_decimal(
                        row.get('LONG_DEG'),
                        row.get('LONG_MIN'),
                        row.get('LONG_SEC'),
                        row.get('LONG_DIR_IND', 'E')
                    )
                    
                    freq = self._safe_float(row.get('FREQ'))
                    freq_pair = self._safe_float(row.get('FREQ_PAIR'))
                    
                    if freq is None:
                        continue
                    
                    license_data = {
                        'clnt_id': self._safe_int(row.get('CLNT_ID')),
                        'no_simf': str(row.get('NO_SIMF', '')),
                        'appl_id': str(row.get('APPL_ID', '')),
                        'clnt_name': str(row.get('CLNT_NAME', '')),
                        'callsign': str(row.get('CALLSIGN', '')),
                        'stn_name': str(row.get('STN_NAME', '')),
                        'service': str(row.get('SERVICE', '')),
                        'subservice': str(row.get('SUBSERVICE', '')),
                        'freq': freq,
                        'freq_pair': freq_pair,
                        'latitude': latitude,
                        'longitude': longitude,
                        'province': str(row.get('PROVINCE', '')),
                        'city': str(row.get('CITY', '')),
                        'district': str(row.get('DISTRICT', '')),
                        'status_simf': str(row.get('STATUS_SIMF', '')),
                        'licence_date': str(row.get('LICENCE_DATE', '')),
                        'validity_date': str(row.get('VALIDITY_DATE', '')),
                        'source_file': self.filename
                    }
                    
                    licenses.append(license_data)
                    
                except Exception as e:
                    continue
            
            return licenses
            
        except Exception as e:
            raise ValueError(f"Error parsing Excel file: {str(e)}")
    
    def _convert_to_decimal(self, deg, min_val, sec, direction):
        """Convert DMS (Degrees, Minutes, Seconds) to decimal degrees"""
        try:
            deg = float(deg) if pd.notna(deg) else 0
            min_val = float(min_val) if pd.notna(min_val) else 0
            sec = float(sec) if pd.notna(sec) else 0
            
            decimal = deg + (min_val / 60) + (sec / 3600)
            
            if direction in ['S', 'W']:
                decimal = -decimal
                
            return round(decimal, 6)
        except:
            return None
    
    def _safe_float(self, value):
        """Safely convert value to float"""
        try:
            if pd.isna(value):
                return None
            return float(value)
        except:
            return None
    
    def _safe_int(self, value):
        """Safely convert value to int"""
        try:
            if pd.isna(value):
                return None
            return int(value)
        except:
            return None
