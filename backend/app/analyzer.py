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
        
        # Detect true peaks using scipy find_peaks
        peak_channels = self._detect_peaks(band_channels, threshold)
        
        occupancy_percentage = (len(peak_channels) / len(band_channels)) * 100
        
        occupied_list = []
        for _, row in peak_channels.iterrows():
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
            'occupied_channels': len(peak_channels),
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
    
    def _detect_peaks(self, band_channels: pd.DataFrame, threshold: float, 
                       prominence: float = 3.0, min_distance: int = 3) -> pd.DataFrame:
        """
        Detect true signal peaks using numpy-based peak detection.
        Only returns actual peaks (local maxima) that are above the threshold.
        Excludes valleys and non-peak points.
        
        Args:
            band_channels: DataFrame with channel data
            threshold: Minimum signal strength to consider
            prominence: Minimum dB difference from surrounding valleys (default 3 dB)
            min_distance: Minimum channels between peaks (default 3)
        """
        if len(band_channels) < 3:
            return band_channels[band_channels['avg_field_strength'] > threshold]
        
        # Sort by frequency to ensure proper peak detection
        sorted_channels = band_channels.sort_values('frequency').reset_index(drop=True)
        signal_values = sorted_channels['avg_field_strength'].values
        n = len(signal_values)
        
        # Find local maxima (points higher than both neighbors)
        local_max_mask = np.zeros(n, dtype=bool)
        for i in range(1, n - 1):
            if signal_values[i] > signal_values[i-1] and signal_values[i] > signal_values[i+1]:
                local_max_mask[i] = True
        
        # Also check edges if they're higher than their single neighbor
        if n > 1:
            if signal_values[0] > signal_values[1]:
                local_max_mask[0] = True
            if signal_values[-1] > signal_values[-2]:
                local_max_mask[-1] = True
        
        # Get indices of local maxima
        peak_indices = np.where(local_max_mask)[0]
        
        if len(peak_indices) == 0:
            return pd.DataFrame(columns=band_channels.columns)
        
        # Filter by threshold
        peak_indices = [i for i in peak_indices if signal_values[i] > threshold]
        
        if len(peak_indices) == 0:
            return pd.DataFrame(columns=band_channels.columns)
        
        # Filter by prominence (peak must be X dB above surrounding valleys)
        prominent_peaks = []
        for idx in peak_indices:
            # Find left valley
            left_min = signal_values[idx]
            for j in range(idx - 1, -1, -1):
                if signal_values[j] < left_min:
                    left_min = signal_values[j]
                if signal_values[j] > signal_values[idx]:
                    break
            
            # Find right valley
            right_min = signal_values[idx]
            for j in range(idx + 1, n):
                if signal_values[j] < right_min:
                    right_min = signal_values[j]
                if signal_values[j] > signal_values[idx]:
                    break
            
            # Calculate prominence (height above the higher of the two valleys)
            valley_height = max(left_min, right_min)
            peak_prominence = signal_values[idx] - valley_height
            
            if peak_prominence >= prominence:
                prominent_peaks.append((idx, signal_values[idx], peak_prominence))
        
        if len(prominent_peaks) == 0:
            return pd.DataFrame(columns=band_channels.columns)
        
        # Sort by signal strength descending
        prominent_peaks.sort(key=lambda x: x[1], reverse=True)
        
        # Apply minimum distance filter (keep strongest peaks, remove nearby weaker ones)
        final_peaks = []
        for peak in prominent_peaks:
            idx = peak[0]
            # Check if too close to an already selected peak
            too_close = False
            for selected_idx in final_peaks:
                if abs(idx - selected_idx) < min_distance:
                    too_close = True
                    break
            if not too_close:
                final_peaks.append(idx)
        
        if len(final_peaks) == 0:
            return pd.DataFrame(columns=band_channels.columns)
        
        # Get the peak channels
        peak_channels = sorted_channels.iloc[final_peaks].copy()
        
        # Sort by field strength descending
        peak_channels = peak_channels.sort_values('avg_field_strength', ascending=False)
        
        return peak_channels
    
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
