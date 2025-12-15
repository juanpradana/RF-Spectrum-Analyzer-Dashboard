import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime
import io

class CSVParser:
    def __init__(self, file_content: bytes):
        self.file_content = file_content
        self.metadata = {}
        self.bands = []
        self.channels = pd.DataFrame()
        
    def parse(self) -> Dict:
        try:
            content = self.file_content.decode('utf-8')
            lines = content.split('\n')
            
            if not lines[0].strip().startswith('sep='):
                raise ValueError("Invalid CSV format: missing separator declaration")
            
            separator = lines[0].strip().split('=')[1]
            
            metadata_start = 1
            bands_start = None
            channels_start = None
            
            for i, line in enumerate(lines):
                if 'Band #' in line:
                    bands_start = i
                elif 'Channel No.' in line:
                    channels_start = i
                    break
            
            if bands_start is None or channels_start is None:
                raise ValueError("Invalid CSV format: missing required sections")
            
            self._parse_metadata(lines[metadata_start:bands_start], separator)
            self._parse_bands(lines[bands_start:channels_start], separator)
            self._parse_channels(lines[channels_start:], separator)
            
            return {
                'metadata': self.metadata,
                'bands': self.bands,
                'channels': self.channels.to_dict('records'),
                'channels_count': len(self.channels)
            }
            
        except Exception as e:
            raise ValueError(f"Error parsing CSV: {str(e)}")
    
    def _parse_metadata(self, lines: List[str], sep: str):
        header_line = lines[0].strip()
        data_line = lines[1].strip() if len(lines) > 1 else ""
        
        if not header_line or not data_line:
            return
        
        headers = [h.strip() for h in header_line.split(sep)]
        values = [v.strip() for v in data_line.split(sep)]
        
        for i, header in enumerate(headers):
            if i < len(values):
                self.metadata[header] = values[i]
        
        if 'Start Time' in self.metadata:
            try:
                self.metadata['Start Time'] = datetime.strptime(
                    self.metadata['Start Time'], '%m/%d/%Y %I:%M:%S %p'
                )
            except:
                pass
        
        if 'Stop Time' in self.metadata:
            try:
                self.metadata['Stop Time'] = datetime.strptime(
                    self.metadata['Stop Time'], '%m/%d/%Y %I:%M:%S %p'
                )
            except:
                pass
        
        if 'Location (lat)' in self.metadata:
            try:
                self.metadata['Location (lat)'] = float(self.metadata['Location (lat)'])
            except:
                pass
        
        if 'Location (lon)' in self.metadata:
            try:
                self.metadata['Location (lon)'] = float(self.metadata['Location (lon)'])
            except:
                pass
    
    def _parse_bands(self, lines: List[str], sep: str):
        if len(lines) < 2:
            return
        
        header_line = lines[0].strip()
        
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            
            parts = [p.strip() for p in line.split(sep)]
            if len(parts) >= 4:
                try:
                    band = {
                        'band_number': int(parts[0]),
                        'start_freq': float(parts[1]),
                        'stop_freq': float(parts[2]),
                        'bandwidth': float(parts[3])
                    }
                    self.bands.append(band)
                except ValueError:
                    continue
    
    def _parse_channels(self, lines: List[str], sep: str):
        if len(lines) < 2:
            return
        
        csv_content = '\n'.join(lines)
        
        try:
            df = pd.read_csv(
                io.StringIO(csv_content),
                sep=sep,
                engine='python'
            )
            
            df.columns = df.columns.str.strip()
            
            column_mapping = {
                'Channel No.': 'channel_no',
                'Frequency (MHz)': 'frequency',
                'Maximum Field Strength (dBuV/m)': 'max_field_strength',
                'Average Field Strength (dBuV/m)': 'avg_field_strength'
            }
            
            df = df.rename(columns=column_mapping)
            
            for col in ['frequency', 'max_field_strength', 'avg_field_strength']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df = df.dropna(subset=['frequency', 'avg_field_strength'])
            
            self.channels = df
            
        except Exception as e:
            raise ValueError(f"Error parsing channels data: {str(e)}")
