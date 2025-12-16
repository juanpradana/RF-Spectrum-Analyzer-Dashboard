import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import json
import os

class SpectrumAnalyzer:
    def __init__(self, channels_df: pd.DataFrame, bands: List[Dict], metadata: Dict, db_session=None):
        self.channels_df = channels_df
        self.bands = bands
        self.metadata = metadata
        self.db_session = db_session
        self.licensed_stations = self._load_licensed_stations()
    
    def _load_licensed_stations(self) -> List[Dict]:
        """
        Load licensed stations from database if available, otherwise from JSON file
        """
        stations = []
        
        # Try to load from database first
        if self.db_session:
            try:
                from .database import LicensedStation
                db_stations = self.db_session.query(LicensedStation).all()
                
                for s in db_stations:
                    stations.append({
                        'name': s.stn_name or s.clnt_name,
                        'clnt_name': s.clnt_name,
                        'callsign': s.callsign,
                        'frequency': s.freq,
                        'location': s.city or s.province,
                        'service': s.service,
                        'latitude': s.latitude,
                        'longitude': s.longitude,
                        'eq_mfr': s.eq_mfr,
                        'eq_mdl': s.eq_mdl,
                        'emis_class_1': s.emis_class_1,
                        'licensed': True
                    })
                
                if len(stations) > 0:
                    return stations
            except:
                pass
        
        # Fallback to JSON file
        stations_file = os.path.join(os.path.dirname(__file__), 'licensed_stations.json')
        if os.path.exists(stations_file):
            try:
                with open(stations_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return []
    
    def calculate_auto_threshold(self, band_number: int, margin_db: float = 10.0) -> Dict:
        """
        Calculate automatic threshold based on noise floor + margin
        Default margin: 10 dB above noise floor
        """
        if band_number > len(self.bands):
            raise ValueError(f"Band {band_number} not found")
        
        band = self.bands[band_number - 1]
        
        band_channels = self.channels_df[
            (self.channels_df['frequency'] >= band['start_freq']) &
            (self.channels_df['frequency'] <= band['stop_freq'])
        ].copy()
        
        if len(band_channels) == 0:
            return {
                'noise_floor': 0,
                'auto_threshold': 50.0,
                'margin_db': margin_db
            }
        
        noise_floor = self._calculate_noise_floor(band_channels)
        auto_threshold = noise_floor + margin_db
        
        return {
            'noise_floor': round(noise_floor, 2),
            'auto_threshold': round(auto_threshold, 2),
            'margin_db': margin_db,
            'recommendation': f"Threshold otomatis: {round(auto_threshold, 2)} dBµV/m (Noise Floor: {round(noise_floor, 2)} + Margin: {margin_db} dB)"
        }
    
    def analyze_band(self, band_number: int, threshold: float = 50.0, use_auto_threshold: bool = False, margin_db: float = 10.0) -> Dict:
        if band_number > len(self.bands):
            raise ValueError(f"Band {band_number} not found")
        
        band = self.bands[band_number - 1]
        
        band_channels = self.channels_df[
            (self.channels_df['frequency'] >= band['start_freq']) &
            (self.channels_df['frequency'] <= band['stop_freq'])
        ].copy()
        
        if len(band_channels) == 0:
            return {
                'band_number': band_number,
                'band_info': band,
                'total_channels': 0,
                'occupancy_percentage': 0,
                'occupied_channels': 0,
                'noise_floor': 0,
                'occupied_list': [],
                'top_signals': [],
                'anomalies': [],
                'threshold_used': threshold,
                'auto_threshold_info': None
            }
        
        noise_floor = self._calculate_noise_floor(band_channels)
        
        # Calculate auto threshold if requested
        if use_auto_threshold:
            threshold = noise_floor + margin_db
        
        occupied_mask = band_channels['avg_field_strength'] > threshold
        occupied_channels = band_channels[occupied_mask].copy()
        
        occupancy_percentage = (len(occupied_channels) / len(band_channels)) * 100
        
        occupied_list = []
        for _, row in occupied_channels.iterrows():
            station_match = self._match_station(row['frequency'])
            occupied_list.append({
                'channel_no': int(row['channel_no']),
                'frequency': float(row['frequency']),
                'avg_field_strength': float(row['avg_field_strength']),
                'max_field_strength': float(row['max_field_strength']),
                'station': station_match
            })
        
        top_signals = band_channels.nlargest(20, 'avg_field_strength')[
            ['channel_no', 'frequency', 'avg_field_strength', 'max_field_strength']
        ].to_dict('records')
        
        for signal in top_signals:
            signal['station'] = self._match_station(signal['frequency'])
        
        anomalies = self._detect_anomalies(band_channels, band)
        
        auto_threshold_info = {
            'noise_floor': round(noise_floor, 2),
            'suggested_threshold': round(noise_floor + margin_db, 2),
            'margin_db': margin_db,
            'is_auto': use_auto_threshold
        }
        
        return {
            'band_number': band_number,
            'band_info': band,
            'total_channels': len(band_channels),
            'occupancy_percentage': round(occupancy_percentage, 2),
            'occupied_channels': len(occupied_channels),
            'noise_floor': round(noise_floor, 2),
            'occupied_list': occupied_list,
            'top_signals': top_signals,
            'anomalies': anomalies,
            'threshold_used': round(threshold, 2),
            'auto_threshold_info': auto_threshold_info
        }
    
    def _calculate_noise_floor(self, band_channels: pd.DataFrame) -> float:
        lowest_10_percent = int(len(band_channels) * 0.1)
        if lowest_10_percent < 1:
            lowest_10_percent = 1
        
        lowest_signals = band_channels.nsmallest(lowest_10_percent, 'avg_field_strength')
        return float(lowest_signals['avg_field_strength'].median())
    
    def _match_station(self, frequency: float) -> Optional[Dict]:
        for station in self.licensed_stations:
            if abs(station.get('frequency', 0) - frequency) < 0.1:
                return {
                    'name': station.get('name', 'Unknown'),
                    'clnt_name': station.get('clnt_name', ''),
                    'callsign': station.get('callsign', ''),
                    'latitude': station.get('latitude'),
                    'longitude': station.get('longitude'),
                    'eq_mfr': station.get('eq_mfr', ''),
                    'eq_mdl': station.get('eq_mdl', ''),
                    'emis_class_1': station.get('emis_class_1', ''),
                    'licensed': True
                }
        return None
    
    def _detect_anomalies(self, band_channels: pd.DataFrame, band: Dict) -> List[Dict]:
        anomalies = []
        
        high_power = band_channels[band_channels['avg_field_strength'] > 80]
        for _, row in high_power.iterrows():
            anomalies.append({
                'type': 'high_power',
                'frequency': float(row['frequency']),
                'avg_field_strength': float(row['avg_field_strength']),
                'description': f"Signal kuat tidak biasa: {row['avg_field_strength']:.1f} dBµV/m"
            })
        
        return anomalies
    
    def compare_analyses(self, other_channels_df: pd.DataFrame, band_number: int) -> Dict:
        band = self.bands[band_number - 1]
        
        current_band = self.channels_df[
            (self.channels_df['frequency'] >= band['start_freq']) &
            (self.channels_df['frequency'] <= band['stop_freq'])
        ]
        
        other_band = other_channels_df[
            (other_channels_df['frequency'] >= band['start_freq']) &
            (other_channels_df['frequency'] <= band['stop_freq'])
        ]
        
        merged = pd.merge(
            current_band[['frequency', 'avg_field_strength']],
            other_band[['frequency', 'avg_field_strength']],
            on='frequency',
            suffixes=('_current', '_other')
        )
        
        return {
            'frequencies': merged['frequency'].tolist(),
            'current_values': merged['avg_field_strength_current'].tolist(),
            'other_values': merged['avg_field_strength_other'].tolist()
        }
