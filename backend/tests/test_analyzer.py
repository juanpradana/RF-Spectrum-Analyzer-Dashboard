import pytest
import pandas as pd
from app.analyzer import SpectrumAnalyzer

def test_occupancy_calculation():
    channels_data = {
        'channel_no': list(range(1, 11)),
        'frequency': [87.0 + i * 0.05 for i in range(10)],
        'avg_field_strength': [30, 35, 55, 60, 45, 70, 40, 65, 50, 38],
        'max_field_strength': [35, 40, 60, 65, 50, 75, 45, 70, 55, 43]
    }
    
    channels_df = pd.DataFrame(channels_data)
    
    bands = [
        {'band_number': 1, 'start_freq': 87.0, 'stop_freq': 88.0, 'bandwidth': 50.0}
    ]
    
    metadata = {'Task ID': '1924', 'Station Name': 'Test'}
    
    analyzer = SpectrumAnalyzer(channels_df, bands, metadata)
    results = analyzer.analyze_band(1, threshold=50.0)
    
    assert results['total_channels'] == 10
    assert results['occupied_channels'] == 4
    assert results['occupancy_percentage'] == 40.0
    assert results['threshold_used'] == 50.0

def test_noise_floor_calculation():
    channels_data = {
        'channel_no': list(range(1, 11)),
        'frequency': [87.0 + i * 0.05 for i in range(10)],
        'avg_field_strength': [30, 31, 32, 33, 34, 60, 65, 70, 75, 80],
        'max_field_strength': [35, 36, 37, 38, 39, 65, 70, 75, 80, 85]
    }
    
    channels_df = pd.DataFrame(channels_data)
    
    bands = [
        {'band_number': 1, 'start_freq': 87.0, 'stop_freq': 88.0, 'bandwidth': 50.0}
    ]
    
    metadata = {'Task ID': '1924'}
    
    analyzer = SpectrumAnalyzer(channels_df, bands, metadata)
    results = analyzer.analyze_band(1, threshold=50.0)
    
    assert results['noise_floor'] == 30.0

def test_anomaly_detection():
    channels_data = {
        'channel_no': list(range(1, 6)),
        'frequency': [87.0, 87.1, 87.2, 87.3, 87.4],
        'avg_field_strength': [40, 50, 85, 60, 45],
        'max_field_strength': [45, 55, 90, 65, 50]
    }
    
    channels_df = pd.DataFrame(channels_data)
    
    bands = [
        {'band_number': 1, 'start_freq': 87.0, 'stop_freq': 88.0, 'bandwidth': 50.0}
    ]
    
    metadata = {'Task ID': '1924'}
    
    analyzer = SpectrumAnalyzer(channels_df, bands, metadata)
    results = analyzer.analyze_band(1, threshold=50.0)
    
    assert len(results['anomalies']) == 1
    assert results['anomalies'][0]['type'] == 'high_power'
    assert results['anomalies'][0]['frequency'] == 87.2

def test_top_signals():
    channels_data = {
        'channel_no': list(range(1, 26)),
        'frequency': [87.0 + i * 0.05 for i in range(25)],
        'avg_field_strength': list(range(30, 55)),
        'max_field_strength': list(range(35, 60))
    }
    
    channels_df = pd.DataFrame(channels_data)
    
    bands = [
        {'band_number': 1, 'start_freq': 87.0, 'stop_freq': 88.5, 'bandwidth': 50.0}
    ]
    
    metadata = {'Task ID': '1924'}
    
    analyzer = SpectrumAnalyzer(channels_df, bands, metadata)
    results = analyzer.analyze_band(1, threshold=50.0)
    
    assert len(results['top_signals']) == 20
    assert results['top_signals'][0]['avg_field_strength'] == 54
